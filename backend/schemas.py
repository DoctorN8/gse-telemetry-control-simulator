from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TelemetryPoint(BaseModel):
    device_id: str
    device_type: str
    timestamp: str
    parameter: str
    value: float
    unit: str
    status: str


class DeviceStateUpdate(BaseModel):
    device_id: str
    device_type: str
    mode: str
    operational_status: str
    last_command: Optional[str] = None
    last_command_time: Optional[str] = None


class CommandRequest(BaseModel):
    device_id: str
    command_type: str
    parameters: Optional[Dict[str, Any]] = {}
    issued_by: str = "operator"


class CommandResponse(BaseModel):
    command_id: int
    success: bool
    message: str


class AlarmResponse(BaseModel):
    alarm_id: int
    device_id: str
    parameter: str
    severity: str
    alarm_type: str
    threshold_value: Optional[float]
    actual_value: float
    triggered_at: datetime
    acknowledged: bool
    cleared: bool


class DeviceStatus(BaseModel):
    device_id: str
    device_type: str
    mode: str
    operational_status: str
    last_command: Optional[str]
    last_command_time: Optional[datetime]
    current_telemetry: Dict[str, float]


class EventCreate(BaseModel):
    device_id: str
    event_type: str
    severity: str
    description: str


class AnomalyDetectionResult(BaseModel):
    device_id: str
    parameter: str
    value: float
    mean: float
    std: float
    z_score: float
    is_anomaly: bool
    threshold: float
