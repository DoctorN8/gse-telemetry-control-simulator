from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://gse_user:gse_password@localhost:5432/gse_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DimDevice(Base):
    __tablename__ = "dim_device"
    
    device_id = Column(String, primary_key=True)
    device_type = Column(String, nullable=False)
    subsystem = Column(String)
    location = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    serial_number = Column(String)
    installation_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DimParameter(Base):
    __tablename__ = "dim_parameter"
    
    parameter_id = Column(Integer, primary_key=True, autoincrement=True)
    parameter_name = Column(String, nullable=False)
    parameter_type = Column(String)
    unit = Column(String)
    description = Column(String)
    min_value = Column(Float)
    max_value = Column(Float)
    nominal_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DimSeverity(Base):
    __tablename__ = "dim_severity"
    
    severity_id = Column(Integer, primary_key=True, autoincrement=True)
    severity_level = Column(String, nullable=False, unique=True)
    severity_code = Column(Integer)
    description = Column(String)
    color_code = Column(String)


class FactTelemetry(Base):
    __tablename__ = "fact_telemetry"
    
    telemetry_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("dim_device.device_id"), nullable=False)
    parameter_id = Column(Integer, ForeignKey("dim_parameter.parameter_id"))
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    status = Column(String)
    quality_flag = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_parameter', 'parameter_id'),
    )


class FactEvents(Base):
    __tablename__ = "fact_events"
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("dim_device.device_id"), nullable=False)
    event_type = Column(String, nullable=False)
    severity_id = Column(Integer, ForeignKey("dim_severity.severity_id"))
    timestamp = Column(DateTime, nullable=False)
    description = Column(String)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String)
    resolved_at = Column(DateTime)
    resolution_notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_severity', 'severity_id'),
        Index('idx_acknowledged', 'acknowledged'),
        Index('idx_resolved', 'resolved'),
    )


class FactCommands(Base):
    __tablename__ = "fact_commands"
    
    command_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("dim_device.device_id"), nullable=False)
    command_type = Column(String, nullable=False)
    parameters = Column(JSON)
    issued_by = Column(String)
    issued_at = Column(DateTime, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    execution_status = Column(String)
    execution_result = Column(JSON)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_device_issued', 'device_id', 'issued_at'),
        Index('idx_acknowledged', 'acknowledged'),
    )


class FactAlarms(Base):
    __tablename__ = "fact_alarms"
    
    alarm_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("dim_device.device_id"), nullable=False)
    parameter_id = Column(Integer, ForeignKey("dim_parameter.parameter_id"))
    severity_id = Column(Integer, ForeignKey("dim_severity.severity_id"))
    alarm_type = Column(String, nullable=False)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    triggered_at = Column(DateTime, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    cleared = Column(Boolean, default=False)
    cleared_at = Column(DateTime)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_device_triggered', 'device_id', 'triggered_at'),
        Index('idx_severity', 'severity_id'),
        Index('idx_cleared', 'cleared'),
    )


class DeviceState(Base):
    __tablename__ = "device_state"
    
    state_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("dim_device.device_id"), nullable=False, unique=True)
    mode = Column(String, nullable=False)
    operational_status = Column(String, nullable=False)
    last_command = Column(String)
    last_command_time = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
