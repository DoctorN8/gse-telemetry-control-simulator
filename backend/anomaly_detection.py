import numpy as np
from collections import defaultdict, deque
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import FactAlarms, DimParameter, DimSeverity


class AnomalyDetector:
    def __init__(self, window_size: int = 100, sigma_threshold: float = 3.0):
        self.window_size = window_size
        self.sigma_threshold = sigma_threshold
        self.data_windows: Dict[Tuple[str, str], deque] = defaultdict(lambda: deque(maxlen=window_size))
        
    def add_data_point(self, device_id: str, parameter: str, value: float):
        key = (device_id, parameter)
        self.data_windows[key].append(value)
    
    def detect_anomaly(self, device_id: str, parameter: str, value: float) -> Tuple[bool, float, float, float]:
        key = (device_id, parameter)
        window = self.data_windows[key]
        
        if len(window) < 10:
            return False, 0.0, 0.0, 0.0
        
        data = np.array(window)
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False, mean, std, 0.0
        
        z_score = abs((value - mean) / std)
        is_anomaly = z_score > self.sigma_threshold
        
        return is_anomaly, mean, std, z_score
    
    def check_threshold_violation(self, parameter: str, value: float, 
                                   min_val: float, max_val: float) -> Tuple[bool, str]:
        if value > max_val:
            return True, "HIGH"
        elif value < min_val:
            return True, "LOW"
        return False, "NOMINAL"


class AlarmManager:
    def __init__(self, db: Session):
        self.db = db
        self.active_alarms: Dict[Tuple[str, str], int] = {}
        
    def create_alarm(self, device_id: str, parameter: str, alarm_type: str,
                    severity: str, threshold_value: float, actual_value: float) -> int:
        key = (device_id, parameter)
        
        if key in self.active_alarms:
            return self.active_alarms[key]
        
        severity_obj = self.db.query(DimSeverity).filter(
            DimSeverity.severity_level == severity
        ).first()
        
        parameter_obj = self.db.query(DimParameter).filter(
            DimParameter.parameter_name == parameter
        ).first()
        
        alarm = FactAlarms(
            device_id=device_id,
            parameter_id=parameter_obj.parameter_id if parameter_obj else None,
            severity_id=severity_obj.severity_id if severity_obj else None,
            alarm_type=alarm_type,
            threshold_value=threshold_value,
            actual_value=actual_value,
            triggered_at=datetime.utcnow(),
            acknowledged=False,
            cleared=False
        )
        
        self.db.add(alarm)
        self.db.commit()
        self.db.refresh(alarm)
        
        self.active_alarms[key] = alarm.alarm_id
        
        return alarm.alarm_id
    
    def clear_alarm(self, device_id: str, parameter: str):
        key = (device_id, parameter)
        
        if key not in self.active_alarms:
            return
        
        alarm_id = self.active_alarms[key]
        alarm = self.db.query(FactAlarms).filter(FactAlarms.alarm_id == alarm_id).first()
        
        if alarm:
            alarm.cleared = True
            alarm.cleared_at = datetime.utcnow()
            
            if alarm.triggered_at:
                duration = (alarm.cleared_at - alarm.triggered_at).total_seconds()
                alarm.duration_seconds = int(duration)
            
            self.db.commit()
        
        del self.active_alarms[key]
    
    def acknowledge_alarm(self, alarm_id: int, acknowledged_by: str):
        alarm = self.db.query(FactAlarms).filter(FactAlarms.alarm_id == alarm_id).first()
        
        if alarm and not alarm.acknowledged:
            alarm.acknowledged = True
            alarm.acknowledged_by = acknowledged_by
            alarm.acknowledged_at = datetime.utcnow()
            self.db.commit()
    
    def get_active_alarms(self) -> List[FactAlarms]:
        return self.db.query(FactAlarms).filter(
            FactAlarms.cleared == False
        ).order_by(FactAlarms.triggered_at.desc()).all()
    
    def get_recent_alarms(self, hours: int = 24) -> List[FactAlarms]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(FactAlarms).filter(
            FactAlarms.triggered_at >= cutoff
        ).order_by(FactAlarms.triggered_at.desc()).all()
