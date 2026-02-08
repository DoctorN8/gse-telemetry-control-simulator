from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import logging

from database import get_db, DimDevice, DimParameter, FactTelemetry, FactCommands, DeviceState, FactEvents, DimSeverity
from schemas import (
    TelemetryPoint, DeviceStateUpdate, CommandRequest, CommandResponse,
    AlarmResponse, DeviceStatus, EventCreate
)
from anomaly_detection import AnomalyDetector, AlarmManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GSE Command & Control API",
    description="Ground Support Equipment Telemetry and Control System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

anomaly_detector = AnomalyDetector(window_size=100, sigma_threshold=3.0)

try:
    from rag_routes import router as rag_router
    app.include_router(rag_router)
    logger.info("RAG assistant routes loaded successfully")
except Exception as e:
    logger.warning(f"RAG assistant not available: {e}")


@app.get("/")
async def root():
    return {
        "service": "GSE Command & Control System",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/telemetry/ingest")
async def ingest_telemetry(telemetry_points: List[TelemetryPoint], db: Session = Depends(get_db)):
    try:
        alarm_manager = AlarmManager(db)
        
        for point in telemetry_points:
            parameter = db.query(DimParameter).filter(
                DimParameter.parameter_name == point.parameter
            ).first()
            
            if not parameter:
                logger.warning(f"Unknown parameter: {point.parameter}")
                continue
            
            telemetry_record = FactTelemetry(
                device_id=point.device_id,
                parameter_id=parameter.parameter_id,
                timestamp=datetime.fromisoformat(point.timestamp.replace('Z', '+00:00')),
                value=point.value,
                status=point.status,
                quality_flag="GOOD"
            )
            db.add(telemetry_record)
            
            anomaly_detector.add_data_point(point.device_id, point.parameter, point.value)
            
            is_anomaly, mean, std, z_score = anomaly_detector.detect_anomaly(
                point.device_id, point.parameter, point.value
            )
            
            if is_anomaly and point.status == "NOMINAL":
                logger.warning(
                    f"Statistical anomaly detected: {point.device_id}/{point.parameter} = {point.value} "
                    f"(z-score: {z_score:.2f}, mean: {mean:.2f}, std: {std:.2f})"
                )
                alarm_manager.create_alarm(
                    device_id=point.device_id,
                    parameter=point.parameter,
                    alarm_type="STATISTICAL_ANOMALY",
                    severity="WARNING",
                    threshold_value=mean + (3 * std),
                    actual_value=point.value
                )
            
            if parameter.min_value is not None and parameter.max_value is not None:
                violation, violation_type = anomaly_detector.check_threshold_violation(
                    point.parameter, point.value, parameter.min_value, parameter.max_value
                )
                
                if violation:
                    severity = "FAULT" if point.status == "FAULT" else "WARNING"
                    threshold = parameter.max_value if violation_type == "HIGH" else parameter.min_value
                    
                    logger.warning(
                        f"Threshold violation: {point.device_id}/{point.parameter} = {point.value} "
                        f"({violation_type}, threshold: {threshold})"
                    )
                    alarm_manager.create_alarm(
                        device_id=point.device_id,
                        parameter=point.parameter,
                        alarm_type=f"THRESHOLD_{violation_type}",
                        severity=severity,
                        threshold_value=threshold,
                        actual_value=point.value
                    )
                else:
                    alarm_manager.clear_alarm(point.device_id, point.parameter)
            
            if point.status in ["WARNING", "FAULT"]:
                event = FactEvents(
                    device_id=point.device_id,
                    event_type=f"{point.parameter.upper()}_{point.status}",
                    severity_id=db.query(DimSeverity).filter(
                        DimSeverity.severity_level == point.status
                    ).first().severity_id,
                    timestamp=datetime.fromisoformat(point.timestamp.replace('Z', '+00:00')),
                    description=f"{point.parameter} reported {point.status}: {point.value} {point.unit}"
                )
                db.add(event)
        
        db.commit()
        return {"status": "success", "points_ingested": len(telemetry_points)}
    
    except Exception as e:
        logger.error(f"Error ingesting telemetry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/devices/state")
async def update_device_state(state: DeviceStateUpdate, db: Session = Depends(get_db)):
    try:
        existing_state = db.query(DeviceState).filter(
            DeviceState.device_id == state.device_id
        ).first()
        
        if existing_state:
            existing_state.mode = state.mode
            existing_state.operational_status = state.operational_status
            existing_state.last_command = state.last_command
            if state.last_command_time:
                existing_state.last_command_time = datetime.fromisoformat(
                    state.last_command_time.replace('Z', '+00:00')
                )
            existing_state.updated_at = datetime.utcnow()
        else:
            new_state = DeviceState(
                device_id=state.device_id,
                mode=state.mode,
                operational_status=state.operational_status,
                last_command=state.last_command,
                last_command_time=datetime.fromisoformat(
                    state.last_command_time.replace('Z', '+00:00')
                ) if state.last_command_time else None
            )
            db.add(new_state)
        
        db.commit()
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error updating device state: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/devices")
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(DimDevice).all()
    return [
        {
            "device_id": d.device_id,
            "device_type": d.device_type,
            "subsystem": d.subsystem,
            "location": d.location
        }
        for d in devices
    ]


@app.get("/api/devices/{device_id}/status")
async def get_device_status(device_id: str, db: Session = Depends(get_db)):
    device = db.query(DimDevice).filter(DimDevice.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    state = db.query(DeviceState).filter(DeviceState.device_id == device_id).first()
    
    recent_telemetry = db.query(FactTelemetry).filter(
        FactTelemetry.device_id == device_id
    ).order_by(FactTelemetry.timestamp.desc()).limit(50).all()
    
    current_telemetry = {}
    for t in recent_telemetry:
        param = db.query(DimParameter).filter(
            DimParameter.parameter_id == t.parameter_id
        ).first()
        if param and param.parameter_name not in current_telemetry:
            current_telemetry[param.parameter_name] = t.value
    
    return {
        "device_id": device.device_id,
        "device_type": device.device_type,
        "mode": state.mode if state else "UNKNOWN",
        "operational_status": state.operational_status if state else "UNKNOWN",
        "last_command": state.last_command if state else None,
        "last_command_time": state.last_command_time if state else None,
        "current_telemetry": current_telemetry
    }


@app.get("/api/devices/{device_id}/telemetry")
async def get_device_telemetry(
    device_id: str,
    parameter: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(FactTelemetry).filter(FactTelemetry.device_id == device_id)
    
    if parameter:
        param = db.query(DimParameter).filter(
            DimParameter.parameter_name == parameter
        ).first()
        if param:
            query = query.filter(FactTelemetry.parameter_id == param.parameter_id)
    
    telemetry = query.order_by(FactTelemetry.timestamp.desc()).limit(limit).all()
    
    result = []
    for t in telemetry:
        param = db.query(DimParameter).filter(
            DimParameter.parameter_id == t.parameter_id
        ).first()
        result.append({
            "timestamp": t.timestamp.isoformat(),
            "parameter": param.parameter_name if param else "unknown",
            "value": t.value,
            "unit": param.unit if param else "",
            "status": t.status
        })
    
    return result


@app.post("/api/commands")
async def issue_command(command: CommandRequest, db: Session = Depends(get_db)):
    try:
        device = db.query(DimDevice).filter(
            DimDevice.device_id == command.device_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        cmd_record = FactCommands(
            device_id=command.device_id,
            command_type=command.command_type,
            parameters=command.parameters,
            issued_by=command.issued_by,
            issued_at=datetime.utcnow(),
            acknowledged=False,
            execution_status="PENDING"
        )
        
        db.add(cmd_record)
        db.commit()
        db.refresh(cmd_record)
        
        event = FactEvents(
            device_id=command.device_id,
            event_type="COMMAND_ISSUED",
            severity_id=db.query(DimSeverity).filter(
                DimSeverity.severity_level == "INFO"
            ).first().severity_id,
            timestamp=datetime.utcnow(),
            description=f"Command {command.command_type} issued by {command.issued_by}"
        )
        db.add(event)
        db.commit()
        
        logger.info(f"Command issued: {command.command_type} to {command.device_id}")
        
        return {
            "command_id": cmd_record.command_id,
            "success": True,
            "message": "Command queued for execution"
        }
    
    except Exception as e:
        logger.error(f"Error issuing command: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/commands/pending/{device_id}")
async def get_pending_commands(device_id: str, db: Session = Depends(get_db)):
    commands = db.query(FactCommands).filter(
        FactCommands.device_id == device_id,
        FactCommands.acknowledged == False
    ).order_by(FactCommands.issued_at).all()
    
    return [
        {
            "id": cmd.command_id,
            "command_type": cmd.command_type,
            "parameters": cmd.parameters,
            "issued_at": cmd.issued_at.isoformat()
        }
        for cmd in commands
    ]


@app.post("/api/commands/acknowledge")
async def acknowledge_command(data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        command_id = data.get("command_id")
        result = data.get("result", {})
        
        command = db.query(FactCommands).filter(
            FactCommands.command_id == command_id
        ).first()
        
        if not command:
            raise HTTPException(status_code=404, detail="Command not found")
        
        command.acknowledged = True
        command.acknowledged_at = datetime.utcnow()
        command.execution_status = "SUCCESS" if result.get("success") else "FAILED"
        command.execution_result = result
        command.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error acknowledging command: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alarms")
async def get_alarms(active_only: bool = True, db: Session = Depends(get_db)):
    alarm_manager = AlarmManager(db)
    
    if active_only:
        alarms = alarm_manager.get_active_alarms()
    else:
        alarms = alarm_manager.get_recent_alarms(hours=24)
    
    result = []
    for alarm in alarms:
        param = db.query(DimParameter).filter(
            DimParameter.parameter_id == alarm.parameter_id
        ).first()
        severity = db.query(DimSeverity).filter(
            DimSeverity.severity_id == alarm.severity_id
        ).first()
        
        result.append({
            "alarm_id": alarm.alarm_id,
            "device_id": alarm.device_id,
            "parameter": param.parameter_name if param else "unknown",
            "severity": severity.severity_level if severity else "UNKNOWN",
            "alarm_type": alarm.alarm_type,
            "threshold_value": alarm.threshold_value,
            "actual_value": alarm.actual_value,
            "triggered_at": alarm.triggered_at.isoformat(),
            "acknowledged": alarm.acknowledged,
            "acknowledged_by": alarm.acknowledged_by,
            "acknowledged_at": alarm.acknowledged_at.isoformat() if alarm.acknowledged_at else None,
            "cleared": alarm.cleared,
            "cleared_at": alarm.cleared_at.isoformat() if alarm.cleared_at else None,
            "duration_seconds": alarm.duration_seconds
        })
    
    return result


@app.post("/api/alarms/{alarm_id}/acknowledge")
async def acknowledge_alarm(alarm_id: int, acknowledged_by: str = "operator", db: Session = Depends(get_db)):
    try:
        alarm_manager = AlarmManager(db)
        alarm_manager.acknowledge_alarm(alarm_id, acknowledged_by)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error acknowledging alarm: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events")
async def get_events(limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(FactEvents).order_by(
        FactEvents.timestamp.desc()
    ).limit(limit).all()
    
    result = []
    for event in events:
        severity = db.query(DimSeverity).filter(
            DimSeverity.severity_id == event.severity_id
        ).first()
        
        result.append({
            "event_id": event.event_id,
            "device_id": event.device_id,
            "event_type": event.event_type,
            "severity": severity.severity_level if severity else "UNKNOWN",
            "timestamp": event.timestamp.isoformat(),
            "description": event.description,
            "acknowledged": event.acknowledged,
            "resolved": event.resolved
        })
    
    return result


@app.get("/api/analytics/mttr")
async def get_mttr_metrics(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    alarms_with_duration = db.query(FactAlarms).filter(
        FactAlarms.cleared == True,
        FactAlarms.duration_seconds.isnot(None)
    ).all()
    
    if not alarms_with_duration:
        return {
            "mean_time_to_acknowledge": 0,
            "mean_time_to_resolve": 0,
            "total_alarms": 0,
            "cleared_alarms": 0
        }
    
    total_alarms = db.query(func.count(FactAlarms.alarm_id)).scalar()
    cleared_alarms = len(alarms_with_duration)
    
    ack_times = []
    resolution_times = []
    
    for alarm in alarms_with_duration:
        if alarm.acknowledged_at and alarm.triggered_at:
            ack_time = (alarm.acknowledged_at - alarm.triggered_at).total_seconds()
            ack_times.append(ack_time)
        
        if alarm.duration_seconds:
            resolution_times.append(alarm.duration_seconds)
    
    mean_ack = sum(ack_times) / len(ack_times) if ack_times else 0
    mean_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    return {
        "mean_time_to_acknowledge": round(mean_ack, 2),
        "mean_time_to_resolve": round(mean_resolution, 2),
        "total_alarms": total_alarms,
        "cleared_alarms": cleared_alarms
    }


@app.get("/api/analytics/alarm-frequency")
async def get_alarm_frequency(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    frequency = db.query(
        FactAlarms.device_id,
        func.count(FactAlarms.alarm_id).label('count')
    ).group_by(FactAlarms.device_id).all()
    
    return [
        {"device_id": device_id, "alarm_count": count}
        for device_id, count in frequency
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
