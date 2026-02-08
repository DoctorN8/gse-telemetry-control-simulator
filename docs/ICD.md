# GSE Command & Control System - Interface Control Document (ICD)

**Document ID:** GSE-ICD-001  
**Version:** 1.0  
**Date:** February 8, 2026  
**Status:** Approved

## 1. Introduction

### 1.1 Purpose
This Interface Control Document (ICD) defines all interfaces, data formats, protocols, and communication patterns for the GSE Command & Control System.

### 1.2 Scope
This document covers:
- Device-to-Backend interfaces
- Backend-to-Frontend interfaces
- Database schemas
- Message formats and protocols

## 2. System Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│  Ground Power   │         │  Cryogenic Line │
│      Unit       │         │     System      │
│   (GPU-001)     │         │   (CRYO-001)    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │  HTTP POST (Telemetry)    │
         │  HTTP GET (Commands)      │
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   FastAPI Backend     │
         │  (Command & Control)  │
         │   - Telemetry Ingest  │
         │   - Anomaly Detection │
         │   - Alarm Management  │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Streamlit     │
│    Database     │    │   Frontend      │
│  (Star Schema)  │    │  (Operator HMI) │
└─────────────────┘    └─────────────────┘
```

## 3. Device-to-Backend Interface

### 3.1 Telemetry Ingestion

**Endpoint:** `POST /api/telemetry/ingest`

**Protocol:** HTTP/1.1

**Content-Type:** application/json

**Request Format:**
```json
[
  {
    "device_id": "GPU-001",
    "device_type": "ground_power_unit",
    "timestamp": "2026-02-08T12:34:56.789Z",
    "parameter": "voltage",
    "value": 28.15,
    "unit": "V",
    "status": "NOMINAL"
  },
  {
    "device_id": "GPU-001",
    "device_type": "ground_power_unit",
    "timestamp": "2026-02-08T12:34:56.789Z",
    "parameter": "current",
    "value": 45.32,
    "unit": "A",
    "status": "NOMINAL"
  }
]
```

**Field Definitions:**

| Field | Type | Required | Description | Valid Values |
|-------|------|----------|-------------|--------------|
| device_id | string | Yes | Unique device identifier | Any valid device ID |
| device_type | string | Yes | Type of device | "ground_power_unit", "cryogenic_line" |
| timestamp | string | Yes | ISO 8601 timestamp in UTC | ISO 8601 format with 'Z' suffix |
| parameter | string | Yes | Parameter name | See Section 3.1.1 |
| value | float | Yes | Measured value | Any float |
| unit | string | Yes | Unit of measurement | See Section 3.1.1 |
| status | string | Yes | Parameter status | "NOMINAL", "WARNING", "FAULT" |

**Response Format:**
```json
{
  "status": "success",
  "points_ingested": 2
}
```

**Error Response:**
```json
{
  "detail": "Error message description"
}
```

**Status Codes:**
- 200: Success
- 400: Bad Request (invalid data format)
- 500: Internal Server Error

#### 3.1.1 Parameter Definitions

**Ground Power Unit Parameters:**

| Parameter | Unit | Min Value | Max Value | Nominal | Description |
|-----------|------|-----------|-----------|---------|-------------|
| voltage | V | 20.0 | 32.0 | 28.0 | Output voltage |
| current | A | 0.0 | 150.0 | 50.0 | Output current |
| power | W | 0.0 | 5000.0 | 1400.0 | Output power |
| temperature | °C | -273.0 | 150.0 | 25.0 | Unit temperature |

**Cryogenic Line Parameters:**

| Parameter | Unit | Min Value | Max Value | Nominal | Description |
|-----------|------|-----------|-----------|---------|-------------|
| valve_position | % | 0.0 | 100.0 | 0.0 | Valve opening percentage |
| pressure | psi | 0.0 | 100.0 | 14.7 | Line pressure |
| flow_rate | L/min | 0.0 | 600.0 | 0.0 | Flow rate |
| temperature | °C | -273.0 | 0.0 | -150.0 | Cryogenic temperature |
| liquid_level | % | 0.0 | 100.0 | 75.0 | Tank liquid level |

### 3.2 Device State Update

**Endpoint:** `POST /api/devices/state`

**Request Format:**
```json
{
  "device_id": "GPU-001",
  "device_type": "ground_power_unit",
  "mode": "ACTIVE",
  "operational_status": "NOMINAL",
  "last_command": "enable_output",
  "last_command_time": "2026-02-08T12:34:56.789Z"
}
```

**Field Definitions:**

| Field | Type | Required | Description | Valid Values |
|-------|------|----------|-------------|--------------|
| device_id | string | Yes | Device identifier | Any valid device ID |
| device_type | string | Yes | Device type | "ground_power_unit", "cryogenic_line" |
| mode | string | Yes | Operational mode | "STANDBY", "ACTIVE", "MAINTENANCE", "EMERGENCY_SHUTDOWN" |
| operational_status | string | Yes | Device status | "NOMINAL", "WARNING", "FAULT", "SHUTDOWN" |
| last_command | string | No | Last executed command | Any command type |
| last_command_time | string | No | Command timestamp | ISO 8601 format |

**Response:**
```json
{
  "status": "success"
}
```

### 3.3 Command Polling

**Endpoint:** `GET /api/commands/pending/{device_id}`

**Request:** No body required

**Response Format:**
```json
[
  {
    "id": 123,
    "command_type": "set_voltage",
    "parameters": {
      "voltage": 30.0
    },
    "issued_at": "2026-02-08T12:34:56.789Z"
  }
]
```

### 3.4 Command Acknowledgment

**Endpoint:** `POST /api/commands/acknowledge`

**Request Format:**
```json
{
  "command_id": 123,
  "result": {
    "success": true,
    "message": "Voltage set to 30.0V"
  }
}
```

**Response:**
```json
{
  "status": "success"
}
```

## 4. Backend-to-Frontend Interface

### 4.1 Device List

**Endpoint:** `GET /api/devices`

**Response Format:**
```json
[
  {
    "device_id": "GPU-001",
    "device_type": "ground_power_unit",
    "subsystem": "Power Systems",
    "location": "Pad 39A"
  },
  {
    "device_id": "CRYO-001",
    "device_type": "cryogenic_line",
    "subsystem": "Propellant Systems",
    "location": "Pad 39A"
  }
]
```

### 4.2 Device Status

**Endpoint:** `GET /api/devices/{device_id}/status`

**Response Format:**
```json
{
  "device_id": "GPU-001",
  "device_type": "ground_power_unit",
  "mode": "ACTIVE",
  "operational_status": "NOMINAL",
  "last_command": "enable_output",
  "last_command_time": "2026-02-08T12:34:56.789Z",
  "current_telemetry": {
    "voltage": 28.15,
    "current": 45.32,
    "power": 1276.40,
    "temperature": 32.5
  }
}
```

### 4.3 Device Telemetry

**Endpoint:** `GET /api/devices/{device_id}/telemetry`

**Query Parameters:**
- `parameter` (optional): Filter by specific parameter
- `limit` (optional): Number of records to return (default: 100)

**Response Format:**
```json
[
  {
    "timestamp": "2026-02-08T12:34:56.789Z",
    "parameter": "voltage",
    "value": 28.15,
    "unit": "V",
    "status": "NOMINAL"
  },
  {
    "timestamp": "2026-02-08T12:34:55.789Z",
    "parameter": "voltage",
    "value": 28.12,
    "unit": "V",
    "status": "NOMINAL"
  }
]
```

### 4.4 Command Issuance

**Endpoint:** `POST /api/commands`

**Request Format:**
```json
{
  "device_id": "GPU-001",
  "command_type": "set_voltage",
  "parameters": {
    "voltage": 30.0
  },
  "issued_by": "operator_john"
}
```

**Response Format:**
```json
{
  "command_id": 123,
  "success": true,
  "message": "Command queued for execution"
}
```

### 4.5 Alarm Retrieval

**Endpoint:** `GET /api/alarms`

**Query Parameters:**
- `active_only` (optional): Boolean, default true

**Response Format:**
```json
[
  {
    "alarm_id": 456,
    "device_id": "GPU-001",
    "parameter": "temperature",
    "severity": "WARNING",
    "alarm_type": "THRESHOLD_HIGH",
    "threshold_value": 75.0,
    "actual_value": 78.5,
    "triggered_at": "2026-02-08T12:34:56.789Z",
    "acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "cleared": false,
    "cleared_at": null,
    "duration_seconds": null
  }
]
```

### 4.6 Alarm Acknowledgment

**Endpoint:** `POST /api/alarms/{alarm_id}/acknowledge`

**Query Parameters:**
- `acknowledged_by`: String, operator identifier

**Response:**
```json
{
  "status": "success"
}
```

### 4.7 Event Log

**Endpoint:** `GET /api/events`

**Query Parameters:**
- `limit` (optional): Number of events to return (default: 100)

**Response Format:**
```json
[
  {
    "event_id": 789,
    "device_id": "GPU-001",
    "event_type": "COMMAND_ISSUED",
    "severity": "INFO",
    "timestamp": "2026-02-08T12:34:56.789Z",
    "description": "Command set_voltage issued by operator_john",
    "acknowledged": false,
    "resolved": false
  }
]
```

### 4.8 Analytics - MTTR

**Endpoint:** `GET /api/analytics/mttr`

**Response Format:**
```json
{
  "mean_time_to_acknowledge": 45.5,
  "mean_time_to_resolve": 320.8,
  "total_alarms": 150,
  "cleared_alarms": 142
}
```

### 4.9 Analytics - Alarm Frequency

**Endpoint:** `GET /api/analytics/alarm-frequency`

**Response Format:**
```json
[
  {
    "device_id": "GPU-001",
    "alarm_count": 45
  },
  {
    "device_id": "CRYO-001",
    "alarm_count": 32
  }
]
```

## 5. Command Specifications

### 5.1 Ground Power Unit Commands

#### 5.1.1 Set Mode
```json
{
  "command_type": "set_mode",
  "parameters": {
    "mode": "ACTIVE"
  }
}
```
**Valid Modes:** STANDBY, ACTIVE, MAINTENANCE, EMERGENCY_SHUTDOWN

#### 5.1.2 Enable Output
```json
{
  "command_type": "enable_output",
  "parameters": {}
}
```
**Preconditions:** Mode must be ACTIVE, status must not be FAULT

#### 5.1.3 Disable Output
```json
{
  "command_type": "disable_output",
  "parameters": {}
}
```

#### 5.1.4 Set Voltage
```json
{
  "command_type": "set_voltage",
  "parameters": {
    "voltage": 28.0
  }
}
```
**Range:** 20.0 - 32.0 V

#### 5.1.5 Set Current Limit
```json
{
  "command_type": "set_current_limit",
  "parameters": {
    "current": 100.0
  }
}
```
**Range:** 0.0 - 150.0 A

### 5.2 Cryogenic Line Commands

#### 5.2.1 Set Mode
```json
{
  "command_type": "set_mode",
  "parameters": {
    "mode": "ACTIVE"
  }
}
```

#### 5.2.2 Open Valve
```json
{
  "command_type": "open_valve",
  "parameters": {
    "position": 50.0
  }
}
```
**Range:** 0.0 - 100.0 %  
**Safety Interlock:** Temperature must be < -100°C

#### 5.2.3 Close Valve
```json
{
  "command_type": "close_valve",
  "parameters": {}
}
```

## 6. Database Schema

### 6.1 Dimension Tables

#### dim_device
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| device_id | VARCHAR | PRIMARY KEY | Unique device identifier |
| device_type | VARCHAR | NOT NULL | Device type |
| subsystem | VARCHAR | | Subsystem name |
| location | VARCHAR | | Physical location |
| manufacturer | VARCHAR | | Manufacturer name |
| model | VARCHAR | | Model number |
| serial_number | VARCHAR | | Serial number |
| installation_date | TIMESTAMP | | Installation date |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

#### dim_parameter
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| parameter_id | SERIAL | PRIMARY KEY | Auto-increment ID |
| parameter_name | VARCHAR | NOT NULL | Parameter name |
| parameter_type | VARCHAR | | Type (electrical, thermal, fluid, mechanical) |
| unit | VARCHAR | | Unit of measurement |
| description | TEXT | | Parameter description |
| min_value | FLOAT | | Minimum valid value |
| max_value | FLOAT | | Maximum valid value |
| nominal_value | FLOAT | | Nominal operating value |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |

#### dim_severity
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| severity_id | SERIAL | PRIMARY KEY | Auto-increment ID |
| severity_level | VARCHAR | NOT NULL, UNIQUE | Severity level name |
| severity_code | INT | | Numeric severity code |
| description | TEXT | | Description |
| color_code | VARCHAR | | Hex color code for UI |

### 6.2 Fact Tables

#### fact_telemetry
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| telemetry_id | SERIAL | PRIMARY KEY | Auto-increment ID |
| device_id | VARCHAR | FK to dim_device | Device identifier |
| parameter_id | INT | FK to dim_parameter | Parameter identifier |
| timestamp | TIMESTAMP | NOT NULL | Measurement timestamp |
| value | FLOAT | NOT NULL | Measured value |
| status | VARCHAR | | Status (NOMINAL, WARNING, FAULT) |
| quality_flag | VARCHAR | | Data quality indicator |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |

**Indexes:**
- idx_device_timestamp (device_id, timestamp)
- idx_timestamp (timestamp)
- idx_parameter (parameter_id)

#### fact_alarms
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| alarm_id | SERIAL | PRIMARY KEY | Auto-increment ID |
| device_id | VARCHAR | FK to dim_device | Device identifier |
| parameter_id | INT | FK to dim_parameter | Parameter identifier |
| severity_id | INT | FK to dim_severity | Severity identifier |
| alarm_type | VARCHAR | NOT NULL | Alarm type |
| threshold_value | FLOAT | | Threshold that was violated |
| actual_value | FLOAT | | Actual measured value |
| triggered_at | TIMESTAMP | NOT NULL | Alarm trigger time |
| acknowledged | BOOLEAN | DEFAULT FALSE | Acknowledgment status |
| acknowledged_by | VARCHAR | | Operator who acknowledged |
| acknowledged_at | TIMESTAMP | | Acknowledgment time |
| cleared | BOOLEAN | DEFAULT FALSE | Clearance status |
| cleared_at | TIMESTAMP | | Clearance time |
| duration_seconds | INT | | Duration from trigger to clear |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation time |

## 7. Communication Protocols

### 7.1 HTTP Protocol
- All communications use HTTP/1.1
- Content-Type: application/json
- Character encoding: UTF-8

### 7.2 Timing Requirements
- Telemetry update rate: 5 Hz (configurable)
- Command polling interval: 200ms
- State update interval: 200ms
- Maximum command latency: 500ms

### 7.3 Error Handling
- HTTP 4xx errors indicate client-side issues
- HTTP 5xx errors indicate server-side issues
- All errors include descriptive messages in response body

## 8. Data Validation Rules

### 8.1 Telemetry Validation
- Timestamp must be valid ISO 8601 format
- Value must be within parameter min/max range (warning if exceeded)
- Status must be one of: NOMINAL, WARNING, FAULT
- Device ID must exist in dim_device table

### 8.2 Command Validation
- Command type must be valid for device type
- Parameters must include all required fields
- Parameter values must be within valid ranges
- Safety interlocks must be satisfied

## 9. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-08 | System Architect | Initial release |

---

**Document Control:**
- **Created:** 2026-02-08
- **Last Modified:** 2026-02-08
- **Next Review:** 2026-03-08
