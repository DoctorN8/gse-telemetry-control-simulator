# 🚀 GSE Command & Control Simulator

A comprehensive Ground Support Equipment (GSE) telemetry and control simulator designed to demonstrate SCADA/HMI-style operations for aerospace ground systems. This project simulates real-time monitoring, command and control, anomaly detection, and operational analytics for ground support equipment.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [System Components](#system-components)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project simulates a ground support equipment command and control system similar to those used at launch facilities like Kennedy Space Center. It demonstrates:

- **Real-time telemetry monitoring** from simulated GSE devices
- **Command and control** capabilities with safety interlocks
- **Anomaly detection** using 3-sigma statistical analysis
- **Alarm management** with acknowledgment and tracking
- **Operator HMI** with live dashboards and controls
- **Analytics and reporting** including MTTR metrics
- **Star-schema data warehouse** for telemetry and events

### Simulated Equipment

1. **Ground Power Unit (GPU-001)**
   - Voltage, current, and power monitoring
   - Temperature tracking
   - Output enable/disable control
   - Setpoint adjustments

2. **Cryogenic Line (CRYO-001)**
   - Valve position control
   - Pressure and flow rate monitoring
   - Temperature monitoring
   - Liquid level tracking
   - Safety interlocks for valve operation

## ✨ Features

### Core Capabilities

- ✅ **Device Simulation**: Python-based simulators emitting realistic telemetry at 5 Hz
- ✅ **Telemetry Ingestion**: FastAPI backend ingesting and validating telemetry data
- ✅ **Anomaly Detection**: 3-sigma statistical analysis and threshold violation detection
- ✅ **Alarm Management**: Automatic alarm creation, acknowledgment, and clearance
- ✅ **Command & Control**: REST API for issuing commands with safety interlocks
- ✅ **Operator Interface**: Streamlit-based HMI with live monitoring and controls
- ✅ **Analytics Dashboard**: MTTR metrics, alarm frequency, and trend analysis
- ✅ **Launch Checklist**: Go/No-Go status display for pre-launch operations
- ✅ **Star Schema Database**: PostgreSQL with dimensional modeling for analytics
- ✅ **Containerized Deployment**: Docker Compose for easy setup

### Advanced Features

- 🔍 Real-time telemetry visualization with Plotly
- 📊 Historical data analysis and trending
- 🚨 Color-coded alarm severity (NOMINAL, WARNING, FAULT, CRITICAL)
- 🔐 Command logging with operator identification
- 📈 Performance metrics and system health monitoring
- 🧪 Fault injection for testing and training

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GSE Simulator System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │ Ground Power │         │  Cryogenic   │                      │
│  │     Unit     │         │     Line     │                      │
│  │  (GPU-001)   │         │  (CRYO-001)  │                      │
│  └──────┬───────┘         └──────┬───────┘                      │
│         │                        │                               │
│         │   Telemetry (5 Hz)     │                               │
│         │   Commands (Polling)   │                               │
│         └────────┬───────────────┘                               │
│                  │                                                │
│                  ▼                                                │
│         ┌────────────────────┐                                   │
│         │   FastAPI Backend  │                                   │
│         │  ┌──────────────┐  │                                   │
│         │  │  Telemetry   │  │                                   │
│         │  │   Ingestion  │  │                                   │
│         │  └──────────────┘  │                                   │
│         │  ┌──────────────┐  │                                   │
│         │  │   Anomaly    │  │                                   │
│         │  │  Detection   │  │                                   │
│         │  └──────────────┘  │                                   │
│         │  ┌──────────────┐  │                                   │
│         │  │    Alarm     │  │                                   │
│         │  │  Management  │  │                                   │
│         │  └──────────────┘  │                                   │
│         └─────────┬──────────┘                                   │
│                   │                                               │
│         ┌─────────┴──────────┐                                   │
│         │                    │                                   │
│         ▼                    ▼                                   │
│  ┌─────────────┐      ┌─────────────┐                           │
│  │ PostgreSQL  │      │  Streamlit  │                           │
│  │  Database   │      │  Frontend   │                           │
│  │             │      │             │                           │
│  │ Star Schema │      │ Operator HMI│                           │
│  └─────────────┘      └─────────────┘                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: FastAPI, SQLAlchemy, NumPy
- **Frontend**: Streamlit, Plotly, Pandas
- **Database**: PostgreSQL 16
- **Devices**: Python 3.11, asyncio, httpx
- **Deployment**: Docker, Docker Compose
- **Data Analysis**: NumPy, Pandas

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- 4GB RAM minimum
- 10GB disk space

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd ABK_Learning_Solutions/Amentum/gse-simulator
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Start the system:**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to initialize** (approximately 30 seconds)

5. **Access the interfaces:**
   - **Operator HMI**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Verification

Check that all services are running:
```bash
docker-compose ps
```

You should see:
- `gse-postgres` (healthy)
- `gse-redis` (healthy)
- `gse-backend` (running)
- `gse-gpu` (running)
- `gse-cryo` (running)
- `gse-frontend` (running)

## 🔧 System Components

### 1. Device Simulators (`/devices`)

Python-based simulators that generate realistic telemetry and respond to commands.

**Ground Power Unit:**
- Simulates voltage, current, power, and temperature
- Supports output enable/disable
- Configurable voltage and current limits
- Fault injection for testing

**Cryogenic Line:**
- Simulates valve control with position feedback
- Monitors pressure, flow rate, temperature, and liquid level
- Enforces safety interlocks (temperature-based valve operation)
- Leak and valve-stuck fault injection

### 2. Backend API (`/backend`)

FastAPI-based command and control server.

**Key Modules:**
- `main.py`: API endpoints and request handling
- `database.py`: SQLAlchemy models and database connection
- `schemas.py`: Pydantic models for validation
- `anomaly_detection.py`: Statistical anomaly detection and alarm management

**Endpoints:**
- `/api/telemetry/ingest`: Ingest telemetry from devices
- `/api/devices`: List all devices
- `/api/devices/{id}/status`: Get device status
- `/api/devices/{id}/telemetry`: Get historical telemetry
- `/api/commands`: Issue commands to devices
- `/api/alarms`: Retrieve and manage alarms
- `/api/events`: View event log
- `/api/analytics/mttr`: MTTR metrics
- `/api/analytics/alarm-frequency`: Alarm frequency analysis

### 3. Frontend HMI (`/frontend`)

Streamlit-based operator interface with multiple views.

**Pages:**
- **Overview**: System status, device summary, recent alarms
- **Device Control**: Issue commands, view real-time status
- **Telemetry Monitor**: Live time-series plots with auto-refresh
- **Alarms & Events**: Active alarms, event log, acknowledgment
- **Analytics**: MTTR metrics, alarm frequency, severity distribution
- **Launch Checklist**: Go/No-Go status for launch preparation

### 4. Database (`/database`)

PostgreSQL with star-schema design for analytics.

**Dimension Tables:**
- `dim_device`: Device metadata
- `dim_parameter`: Parameter definitions
- `dim_severity`: Severity levels
- `dim_time`: Time dimension (future enhancement)

**Fact Tables:**
- `fact_telemetry`: Telemetry measurements
- `fact_events`: System events
- `fact_commands`: Command history
- `fact_alarms`: Alarm records
- `device_state`: Current device states

## 📖 Usage Guide

### Starting the System

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f gse-backend
docker-compose logs -f gse-gpu
```

### Stopping the System

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Operating the System

1. **Access the Operator HMI** at http://localhost:8501

2. **Monitor Device Status:**
   - Navigate to "Overview" to see all devices
   - Check operational status (NOMINAL, WARNING, FAULT)
   - View current telemetry values

3. **Control Devices:**
   - Navigate to "Device Control"
   - Select a device
   - Issue commands (set mode, enable output, adjust setpoints)
   - Observe command execution and feedback

4. **Monitor Telemetry:**
   - Navigate to "Telemetry Monitor"
   - Select device and parameters
   - View live time-series plots
   - Enable auto-refresh for continuous monitoring

5. **Manage Alarms:**
   - Navigate to "Alarms & Events"
   - View active alarms
   - Acknowledge alarms
   - Review event log

6. **Analyze Performance:**
   - Navigate to "Analytics"
   - Review MTTR metrics
   - Analyze alarm frequency by device
   - View severity distribution

7. **Launch Checklist:**
   - Navigate to "Launch Checklist"
   - Verify all systems are NOMINAL and ACTIVE
   - Check for active alarms
   - Confirm GO/NO-GO status

### Testing Scenarios

#### Scenario 1: Normal Operations
1. Set GPU-001 to ACTIVE mode
2. Enable output
3. Monitor voltage and current telemetry
4. Adjust voltage setpoint
5. Observe telemetry changes

#### Scenario 2: Fault Injection
1. Inject fault on GPU-001
2. Observe alarm generation
3. Check operational status changes to FAULT
4. Acknowledge alarm
5. Clear fault
6. Verify system returns to NOMINAL

#### Scenario 3: Cryogenic Operations
1. Set CRYO-001 to ACTIVE mode
2. Wait for temperature to reach < -100°C
3. Open valve to 50%
4. Monitor pressure and flow rate
5. Close valve
6. Observe telemetry stabilization

#### Scenario 4: Safety Interlock
1. Set CRYO-001 to ACTIVE mode
2. Inject fault to raise temperature
3. Attempt to open valve
4. Observe command rejection due to safety interlock
5. Clear fault
6. Retry valve operation

## 📚 API Documentation

### Interactive API Docs

Access Swagger UI at: http://localhost:8000/docs

### Example API Calls

**Get Device Status:**
```bash
curl http://localhost:8000/api/devices/GPU-001/status
```

**Issue Command:**
```bash
curl -X POST http://localhost:8000/api/commands \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "GPU-001",
    "command_type": "set_voltage",
    "parameters": {"voltage": 30.0},
    "issued_by": "operator"
  }'
```

**Get Active Alarms:**
```bash
curl http://localhost:8000/api/alarms?active_only=true
```

**Get Telemetry:**
```bash
curl "http://localhost:8000/api/devices/GPU-001/telemetry?parameter=voltage&limit=50"
```

## 🛠️ Development

### Local Development Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL:**
   ```bash
   docker-compose up -d postgres
   ```

3. **Run backend locally:**
   ```bash
   cd backend
   export DATABASE_URL="postgresql://gse_user:gse_password@localhost:5432/gse_db"
   python main.py
   ```

4. **Run device simulator locally:**
   ```bash
   cd devices
   export DEVICE_TYPE="ground_power_unit"
   export DEVICE_ID="GPU-001"
   export BACKEND_URL="http://localhost:8000"
   python main.py
   ```

5. **Run frontend locally:**
   ```bash
   cd frontend
   export BACKEND_URL="http://localhost:8000"
   streamlit run app.py
   ```

### Adding New Device Types

1. Create new device class in `devices/` inheriting from `BaseDevice`
2. Implement `generate_telemetry()` and `process_command()` methods
3. Add device parameters to `database/init.sql`
4. Update `devices/main.py` to instantiate new device type
5. Add device entry to `dim_device` table
6. Update frontend controls in `frontend/app.py`

### Database Migrations

```bash
# Connect to database
docker exec -it gse-postgres psql -U gse_user -d gse_db

# Run SQL commands
\dt  # List tables
\d fact_telemetry  # Describe table
```

## 🧪 Testing

### Manual Testing

Use the frontend interface to test all functionality:
- Device control commands
- Telemetry monitoring
- Alarm generation and acknowledgment
- Analytics calculations

### API Testing

Use the Swagger UI at http://localhost:8000/docs to test API endpoints.

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test telemetry ingestion
ab -n 1000 -c 10 -p telemetry.json -T application/json \
  http://localhost:8000/api/telemetry/ingest
```

## 📄 Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[REQUIREMENTS.md](docs/REQUIREMENTS.md)**: Functional and non-functional requirements
- **[ICD.md](docs/ICD.md)**: Interface Control Document with API specifications
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture and design
- **[TEST_PLAN.md](docs/TEST_PLAN.md)**: Test procedures and traceability matrix

## 🔍 Troubleshooting

### Services Won't Start

```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker exec gse-postgres pg_isready -U gse_user

# Verify database exists
docker exec -it gse-postgres psql -U gse_user -l
```

### Devices Not Sending Telemetry

```bash
# Check device logs
docker-compose logs gse-gpu
docker-compose logs gse-cryo

# Verify backend is accessible
curl http://localhost:8000/health
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs gse-frontend

# Verify backend connectivity
curl http://localhost:8000/api/devices
```

### Port Conflicts

If ports 8000, 8501, or 5432 are already in use:

1. Edit `docker-compose.yml`
2. Change port mappings (e.g., `8001:8000`)
3. Update `.env` file if needed
4. Restart services

## 🤝 Contributing

This is a demonstration project. For improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational and demonstration purposes.

## 🎓 Learning Outcomes

This project demonstrates:

- **Systems Engineering**: Requirements, architecture, ICD, test planning
- **Full-Stack Development**: Backend API, frontend UI, database design
- **Real-Time Systems**: Telemetry streaming, command processing
- **Data Engineering**: Star schema, ETL, analytics
- **DevOps**: Containerization, orchestration, deployment
- **Domain Knowledge**: SCADA/HMI patterns, GSE operations, safety interlocks

## 📞 Support

For questions or issues:
- Review documentation in `/docs`
- Check troubleshooting section
- Review API documentation at http://localhost:8000/docs

## 🚀 Future Enhancements

Potential additions:
- [ ] RAG assistant for procedures and operations handbook
- [ ] Authentication and role-based access control
- [ ] WebSocket support for real-time telemetry streaming
- [ ] Grafana dashboards for advanced visualization
- [ ] Prometheus metrics export
- [ ] Historical data replay
- [ ] Multi-site support
- [ ] Mobile-responsive UI
- [ ] Automated test suite
- [ ] CI/CD pipeline

---

**Built with ❤️ for aerospace ground operations simulation**
