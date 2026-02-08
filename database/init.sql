CREATE TABLE IF NOT EXISTS dim_device (
    device_id VARCHAR PRIMARY KEY,
    device_type VARCHAR NOT NULL,
    subsystem VARCHAR,
    location VARCHAR,
    manufacturer VARCHAR,
    model VARCHAR,
    serial_number VARCHAR,
    installation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_parameter (
    parameter_id SERIAL PRIMARY KEY,
    parameter_name VARCHAR NOT NULL,
    parameter_type VARCHAR,
    unit VARCHAR,
    description TEXT,
    min_value FLOAT,
    max_value FLOAT,
    nominal_value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL UNIQUE,
    year INT,
    month INT,
    day INT,
    hour INT,
    minute INT,
    second INT,
    day_of_week INT,
    week_of_year INT,
    quarter INT
);

CREATE TABLE IF NOT EXISTS dim_severity (
    severity_id SERIAL PRIMARY KEY,
    severity_level VARCHAR NOT NULL UNIQUE,
    severity_code INT,
    description TEXT,
    color_code VARCHAR
);

CREATE TABLE IF NOT EXISTS fact_telemetry (
    telemetry_id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL REFERENCES dim_device(device_id),
    parameter_id INT REFERENCES dim_parameter(parameter_id),
    timestamp TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    status VARCHAR,
    quality_flag VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_device_timestamp ON fact_telemetry (device_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_timestamp ON fact_telemetry (timestamp);
CREATE INDEX IF NOT EXISTS idx_parameter ON fact_telemetry (parameter_id);

CREATE TABLE IF NOT EXISTS fact_events (
    event_id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL REFERENCES dim_device(device_id),
    event_type VARCHAR NOT NULL,
    severity_id INT REFERENCES dim_severity(severity_id),
    timestamp TIMESTAMP NOT NULL,
    description TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR,
    acknowledged_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_device_timestamp ON fact_events (device_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_event_severity ON fact_events (severity_id);
CREATE INDEX IF NOT EXISTS idx_event_acknowledged ON fact_events (acknowledged);
CREATE INDEX IF NOT EXISTS idx_event_resolved ON fact_events (resolved);

CREATE TABLE IF NOT EXISTS fact_commands (
    command_id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL REFERENCES dim_device(device_id),
    command_type VARCHAR NOT NULL,
    parameters JSONB,
    issued_by VARCHAR,
    issued_at TIMESTAMP NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    execution_status VARCHAR,
    execution_result JSONB,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_command_device_issued ON fact_commands (device_id, issued_at);
CREATE INDEX IF NOT EXISTS idx_command_acknowledged ON fact_commands (acknowledged);

CREATE TABLE IF NOT EXISTS fact_alarms (
    alarm_id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL REFERENCES dim_device(device_id),
    parameter_id INT REFERENCES dim_parameter(parameter_id),
    severity_id INT REFERENCES dim_severity(severity_id),
    alarm_type VARCHAR NOT NULL,
    threshold_value FLOAT,
    actual_value FLOAT,
    triggered_at TIMESTAMP NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR,
    acknowledged_at TIMESTAMP,
    cleared BOOLEAN DEFAULT FALSE,
    cleared_at TIMESTAMP,
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alarm_device_triggered ON fact_alarms (device_id, triggered_at);
CREATE INDEX IF NOT EXISTS idx_alarm_severity_id ON fact_alarms (severity_id);
CREATE INDEX IF NOT EXISTS idx_alarm_cleared ON fact_alarms (cleared);

CREATE TABLE IF NOT EXISTS device_state (
    state_id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL REFERENCES dim_device(device_id),
    mode VARCHAR NOT NULL,
    operational_status VARCHAR NOT NULL,
    last_command VARCHAR,
    last_command_time TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id)
);

INSERT INTO dim_severity (severity_level, severity_code, description, color_code) VALUES
    ('NOMINAL', 0, 'Normal operation', '#00FF00'),
    ('INFO', 1, 'Informational message', '#0000FF'),
    ('WARNING', 2, 'Warning condition', '#FFA500'),
    ('FAULT', 3, 'Fault condition', '#FF0000'),
    ('CRITICAL', 4, 'Critical system failure', '#8B0000')
ON CONFLICT (severity_level) DO NOTHING;

INSERT INTO dim_device (device_id, device_type, subsystem, location) VALUES
    ('GPU-001', 'ground_power_unit', 'Power Systems', 'Pad 39A'),
    ('CRYO-001', 'cryogenic_line', 'Propellant Systems', 'Pad 39A')
ON CONFLICT (device_id) DO NOTHING;

INSERT INTO dim_parameter (parameter_name, parameter_type, unit, min_value, max_value, nominal_value) VALUES
    ('voltage', 'electrical', 'V', 20.0, 32.0, 28.0),
    ('current', 'electrical', 'A', 0.0, 150.0, 50.0),
    ('power', 'electrical', 'W', 0.0, 5000.0, 1400.0),
    ('temperature', 'thermal', '°C', -273.0, 150.0, 25.0),
    ('valve_position', 'mechanical', '%', 0.0, 100.0, 0.0),
    ('pressure', 'fluid', 'psi', 0.0, 100.0, 14.7),
    ('flow_rate', 'fluid', 'L/min', 0.0, 600.0, 0.0),
    ('liquid_level', 'fluid', '%', 0.0, 100.0, 75.0)
ON CONFLICT DO NOTHING;
