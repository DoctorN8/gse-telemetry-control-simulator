# GSE Simulator - Test Plan

## 1. Test Overview

### 1.1 Purpose
This test plan defines the testing strategy, test cases, and acceptance criteria for the Ground Support Equipment (GSE) Telemetry & Control Simulator system.

### 1.2 Scope
Testing covers:
- Device simulators (GPU and Cryogenic Line)
- Backend API endpoints
- Anomaly detection and alarm generation
- Database operations
- Frontend UI functionality
- System integration
- Performance and reliability

### 1.3 Test Environment
- **Operating System:** Linux/Windows/macOS
- **Python Version:** 3.11+
- **Database:** PostgreSQL 15
- **Containerization:** Docker & Docker Compose
- **Testing Framework:** pytest, requests, selenium

---

## 2. Test Strategy

### 2.1 Test Levels

#### Unit Testing
- Individual functions and methods
- Database models and queries
- Anomaly detection algorithms
- Command processing logic

#### Integration Testing
- Device-to-backend communication
- Backend-to-database operations
- API endpoint workflows
- Frontend-to-backend integration

#### System Testing
- End-to-end scenarios
- Multi-device coordination
- Alarm escalation workflows
- Launch checklist validation

#### Performance Testing
- Telemetry ingestion throughput
- Database query performance
- Concurrent user handling
- Memory and CPU utilization

---

## 3. Test Cases

### 3.1 Device Simulator Tests

#### TC-DEV-001: GPU Initialization
**Objective:** Verify GPU simulator initializes correctly

**Preconditions:**
- Docker environment running
- Backend API available

**Test Steps:**
1. Start GPU container
2. Verify device registers with backend
3. Check initial telemetry transmission
4. Verify default state (STANDBY, NOMINAL)

**Expected Results:**
- Device appears in `/api/devices` endpoint
- Initial telemetry received within 5 seconds
- State is STANDBY, status is NOMINAL
- All parameters within normal ranges

**Pass/Fail Criteria:** All expected results met

---

#### TC-DEV-002: GPU Telemetry Generation
**Objective:** Verify GPU generates realistic telemetry

**Test Steps:**
1. Start GPU in ACTIVE mode
2. Collect 100 telemetry samples
3. Analyze voltage, current, power, temperature

**Expected Results:**
- Voltage: 28.0V ±0.5V
- Current: 0-150A (varies with load simulation)
- Power: Voltage × Current ±5%
- Temperature: 25-45°C in normal operation
- Telemetry rate: 1 sample/second

**Pass/Fail Criteria:** 95% of samples within expected ranges

---

#### TC-DEV-003: GPU Command Processing
**Objective:** Verify GPU responds to commands correctly

**Test Steps:**
1. Send `set_mode` command (ACTIVE)
2. Send `enable_output` command
3. Send `set_voltage` command (30V)
4. Send `set_current_limit` command (100A)
5. Send `disable_output` command

**Expected Results:**
- Each command acknowledged within 2 seconds
- Mode changes reflected in state
- Voltage setpoint updated
- Current limit enforced
- Output disabled successfully

**Pass/Fail Criteria:** All commands executed successfully

---

#### TC-DEV-004: GPU Fault Injection
**Objective:** Verify GPU can simulate faults

**Test Steps:**
1. Inject `overheat` fault
2. Observe temperature increase
3. Verify alarm generation
4. Clear fault
5. Observe temperature normalization

**Expected Results:**
- Temperature rises above 75°C
- Alarm created with severity WARNING or FAULT
- Fault clears successfully
- Temperature returns to normal range

**Pass/Fail Criteria:** Fault behavior matches specification

---

#### TC-DEV-005: Cryogenic Line Initialization
**Objective:** Verify Cryo simulator initializes correctly

**Test Steps:**
1. Start Cryo container
2. Verify device registration
3. Check initial telemetry
4. Verify valve is closed (0%)

**Expected Results:**
- Device registered in backend
- Initial telemetry received
- Valve position: 0%
- Temperature: ambient initially
- Pressure: ~14.7 psi

**Pass/Fail Criteria:** All expected results met

---

#### TC-DEV-006: Cryogenic Line Cooldown
**Objective:** Verify cryo line cooldown simulation

**Test Steps:**
1. Set mode to ACTIVE
2. Monitor temperature over 60 seconds
3. Verify temperature decreases

**Expected Results:**
- Temperature decreases from ambient
- Target temperature: < -100°C
- Cooldown rate: realistic (gradual)
- No pressure spikes during cooldown

**Pass/Fail Criteria:** Temperature reaches < -100°C within 5 minutes

---

#### TC-DEV-007: Cryogenic Valve Operation
**Objective:** Verify valve control and interlocks

**Test Steps:**
1. Attempt to open valve at ambient temperature (should fail)
2. Cool line to < -100°C
3. Open valve to 50%
4. Observe pressure and flow rate increase
5. Close valve to 0%

**Expected Results:**
- Valve command rejected when T > -100°C
- Valve opens successfully when T < -100°C
- Pressure increases proportionally
- Flow rate increases proportionally
- Valve closes successfully

**Pass/Fail Criteria:** Interlock enforced, valve operates correctly

---

#### TC-DEV-008: Cryogenic Leak Simulation
**Objective:** Verify leak fault detection

**Test Steps:**
1. Open valve to establish flow
2. Inject `leak` fault
3. Observe pressure drop
4. Verify alarm generation
5. Clear fault

**Expected Results:**
- Pressure drops rapidly (> 5 psi/min)
- Alarm created with severity FAULT
- Leak fault indicated in device state
- Fault clears successfully

**Pass/Fail Criteria:** Leak detected and alarmed

---

### 3.2 Backend API Tests

#### TC-API-001: Health Check
**Objective:** Verify API health endpoint

**Test Steps:**
1. Send GET request to `/health`

**Expected Results:**
- HTTP 200 status
- Response contains `status: healthy`
- Response contains timestamp

**Pass/Fail Criteria:** Response matches expected format

---

#### TC-API-002: Telemetry Ingestion
**Objective:** Verify telemetry ingestion endpoint

**Test Steps:**
1. Send POST to `/api/telemetry/ingest` with sample data
2. Query database for stored telemetry
3. Verify data integrity

**Expected Results:**
- HTTP 200 status
- Telemetry stored in `fact_telemetry` table
- Timestamp, device_id, parameter_id, value correct
- No data loss or corruption

**Pass/Fail Criteria:** Data stored accurately

---

#### TC-API-003: Device State Update
**Objective:** Verify device state endpoint

**Test Steps:**
1. Send POST to `/api/devices/state` with state update
2. Query device state from database
3. Verify state change

**Expected Results:**
- HTTP 200 status
- State updated in `device_state` table
- Timestamp updated
- Event logged in `fact_events`

**Pass/Fail Criteria:** State updated correctly

---

#### TC-API-004: Command Issuance
**Objective:** Verify command endpoint

**Test Steps:**
1. Send POST to `/api/commands` with command
2. Verify command stored in database
3. Check command appears in pending queue
4. Acknowledge command execution

**Expected Results:**
- HTTP 200 status
- Command stored with status PENDING
- Command retrievable via `/api/commands/pending/{device_id}`
- Acknowledgment updates status to COMPLETED

**Pass/Fail Criteria:** Command workflow complete

---

#### TC-API-005: Anomaly Detection
**Objective:** Verify anomaly detection triggers alarms

**Test Steps:**
1. Send normal telemetry (10 samples)
2. Send anomalous telemetry (value 5σ from mean)
3. Query alarms endpoint
4. Verify alarm created

**Expected Results:**
- Normal telemetry does not trigger alarm
- Anomalous telemetry triggers alarm
- Alarm has correct severity (WARNING or FAULT)
- Alarm contains relevant details

**Pass/Fail Criteria:** Anomaly detected and alarmed

---

#### TC-API-006: Alarm Acknowledgment
**Objective:** Verify alarm acknowledgment workflow

**Test Steps:**
1. Create alarm (via anomaly or fault)
2. Send POST to `/api/alarms/{alarm_id}/acknowledge`
3. Query alarm status
4. Verify acknowledgment timestamp

**Expected Results:**
- HTTP 200 status
- Alarm status updated to acknowledged
- Acknowledgment timestamp set
- Alarm still visible in history

**Pass/Fail Criteria:** Alarm acknowledged correctly

---

#### TC-API-007: Analytics - MTTR
**Objective:** Verify MTTR calculation

**Test Steps:**
1. Create multiple alarms
2. Acknowledge alarms at different times
3. Resolve alarms at different times
4. Query `/api/analytics/mttr`

**Expected Results:**
- MTTA (Mean Time To Acknowledge) calculated
- MTTR (Mean Time To Resolve) calculated
- Values are reasonable (seconds/minutes)
- Calculation matches manual verification

**Pass/Fail Criteria:** MTTR metrics accurate

---

#### TC-API-008: Historical Telemetry Query
**Objective:** Verify telemetry history retrieval

**Test Steps:**
1. Ingest telemetry over 5 minutes
2. Query `/api/devices/{device_id}/telemetry` with time range
3. Verify returned data

**Expected Results:**
- HTTP 200 status
- Data within requested time range
- Data sorted by timestamp
- All requested parameters included

**Pass/Fail Criteria:** Query returns correct data

---

### 3.3 Frontend UI Tests

#### TC-UI-001: Overview Page Load
**Objective:** Verify overview page displays correctly

**Test Steps:**
1. Navigate to Streamlit app
2. Select "Overview" page
3. Verify content loads

**Expected Results:**
- System summary displayed
- Device status cards shown
- Recent alarms listed
- No errors or exceptions

**Pass/Fail Criteria:** Page loads without errors

---

#### TC-UI-002: Device Control
**Objective:** Verify device control interface

**Test Steps:**
1. Navigate to "Device Control" page
2. Select GPU device
3. Issue command (e.g., set mode to ACTIVE)
4. Verify command sent
5. Observe status update

**Expected Results:**
- Device selector works
- Command buttons functional
- Success message displayed
- Device status updates within 5 seconds

**Pass/Fail Criteria:** Command issued and confirmed

---

#### TC-UI-003: Telemetry Monitor
**Objective:** Verify live telemetry display

**Test Steps:**
1. Navigate to "Telemetry Monitor" page
2. Select device and parameters
3. Observe live plot updates
4. Verify data accuracy

**Expected Results:**
- Plot displays and updates every 2 seconds
- Data matches backend values
- Multiple parameters can be plotted
- Time axis scrolls correctly

**Pass/Fail Criteria:** Telemetry displayed accurately

---

#### TC-UI-004: Alarm Acknowledgment
**Objective:** Verify alarm acknowledgment from UI

**Test Steps:**
1. Navigate to "Alarms & Events" page
2. Trigger alarm (via device fault)
3. Click "Acknowledge" button
4. Verify alarm status changes

**Expected Results:**
- Alarm appears in active alarms list
- Acknowledge button functional
- Alarm moves to acknowledged state
- Timestamp updated

**Pass/Fail Criteria:** Alarm acknowledged via UI

---

#### TC-UI-005: Analytics Dashboard
**Objective:** Verify analytics page displays metrics

**Test Steps:**
1. Generate alarms and events
2. Navigate to "Analytics" page
3. Verify MTTR metrics displayed
4. Verify charts render

**Expected Results:**
- MTTA and MTTR values shown
- Alarm frequency chart displayed
- Severity distribution chart displayed
- Data matches backend calculations

**Pass/Fail Criteria:** Analytics displayed correctly

---

#### TC-UI-006: Launch Checklist
**Objective:** Verify launch checklist functionality

**Test Steps:**
1. Navigate to "Launch Checklist" page
2. Verify device status checks
3. Trigger fault to create NO-GO condition
4. Verify checklist updates

**Expected Results:**
- All devices listed with GO/NO-GO status
- Active alarms cause NO-GO
- Overall status calculated correctly
- Recommendations provided

**Pass/Fail Criteria:** Checklist logic correct

---

### 3.4 Integration Tests

#### TC-INT-001: End-to-End Telemetry Flow
**Objective:** Verify complete telemetry pipeline

**Test Steps:**
1. Start all services (devices, backend, frontend)
2. Device generates telemetry
3. Backend ingests and stores telemetry
4. Frontend displays telemetry
5. Verify data consistency

**Expected Results:**
- Telemetry flows from device to UI
- No data loss
- Latency < 5 seconds end-to-end
- Data accurate at each stage

**Pass/Fail Criteria:** Complete pipeline functional

---

#### TC-INT-002: Command-and-Control Loop
**Objective:** Verify command execution workflow

**Test Steps:**
1. Issue command from UI
2. Backend stores command
3. Device polls and retrieves command
4. Device executes command
5. Device acknowledges execution
6. UI reflects new state

**Expected Results:**
- Command propagates through system
- Execution confirmed within 10 seconds
- State change visible in UI
- Event logged

**Pass/Fail Criteria:** Command loop complete

---

#### TC-INT-003: Alarm Escalation
**Objective:** Verify alarm creation and notification

**Test Steps:**
1. Inject fault in device
2. Anomalous telemetry generated
3. Backend detects anomaly
4. Alarm created
5. UI displays alarm
6. Operator acknowledges alarm

**Expected Results:**
- Alarm created within 5 seconds of anomaly
- Alarm visible in UI immediately
- Acknowledgment propagates to backend
- Event logged

**Pass/Fail Criteria:** Alarm workflow complete

---

#### TC-INT-004: Multi-Device Coordination
**Objective:** Verify system handles multiple devices

**Test Steps:**
1. Start GPU and Cryo devices simultaneously
2. Both devices send telemetry
3. Issue commands to both devices
4. Verify no interference or data mixing

**Expected Results:**
- Both devices operational
- Telemetry correctly attributed
- Commands routed correctly
- No cross-contamination

**Pass/Fail Criteria:** Multi-device operation successful

---

### 3.5 Performance Tests

#### TC-PERF-001: Telemetry Throughput
**Objective:** Measure telemetry ingestion rate

**Test Steps:**
1. Configure devices for high-frequency telemetry (10 Hz)
2. Run for 5 minutes
3. Measure ingestion rate
4. Check for dropped samples

**Expected Results:**
- Ingestion rate: > 100 samples/second
- No dropped samples
- Database write latency < 100ms
- CPU usage < 80%

**Pass/Fail Criteria:** Performance targets met

---

#### TC-PERF-002: Concurrent Users
**Objective:** Verify system handles multiple operators

**Test Steps:**
1. Simulate 10 concurrent UI users
2. Each user queries telemetry and issues commands
3. Measure response times
4. Check for errors

**Expected Results:**
- All requests succeed
- Response time < 2 seconds (95th percentile)
- No database deadlocks
- No UI errors

**Pass/Fail Criteria:** System stable under load

---

#### TC-PERF-003: Database Query Performance
**Objective:** Verify database query efficiency

**Test Steps:**
1. Populate database with 1 million telemetry records
2. Query historical telemetry (various time ranges)
3. Measure query execution time

**Expected Results:**
- Query time < 1 second for 1-hour range
- Query time < 5 seconds for 1-day range
- Indexes utilized effectively
- No full table scans

**Pass/Fail Criteria:** Query performance acceptable

---

#### TC-PERF-004: Memory Usage
**Objective:** Verify system memory footprint

**Test Steps:**
1. Run system for 24 hours
2. Monitor memory usage of all services
3. Check for memory leaks

**Expected Results:**
- Backend memory: < 512 MB
- Device memory: < 128 MB each
- Frontend memory: < 256 MB
- No memory growth over time

**Pass/Fail Criteria:** Memory usage stable

---

### 3.6 Reliability Tests

#### TC-REL-001: Device Reconnection
**Objective:** Verify device reconnects after failure

**Test Steps:**
1. Start device
2. Stop device (simulate crash)
3. Restart device
4. Verify reconnection

**Expected Results:**
- Device reconnects automatically
- Telemetry resumes
- No data corruption
- State restored correctly

**Pass/Fail Criteria:** Reconnection successful

---

#### TC-REL-002: Database Connection Loss
**Objective:** Verify backend handles database outage

**Test Steps:**
1. Run system normally
2. Stop database
3. Attempt operations
4. Restart database
5. Verify recovery

**Expected Results:**
- Backend returns appropriate errors
- No crashes
- Operations resume after database restart
- No data loss

**Pass/Fail Criteria:** Graceful degradation and recovery

---

#### TC-REL-003: Long-Duration Stability
**Objective:** Verify system stability over time

**Test Steps:**
1. Run system for 7 days
2. Monitor for errors, crashes, or degradation
3. Verify data integrity

**Expected Results:**
- No crashes or restarts required
- Performance remains consistent
- No data corruption
- Logs show no critical errors

**Pass/Fail Criteria:** System stable for 7 days

---

## 4. Test Execution

### 4.1 Test Environment Setup

```bash
cd gse-simulator
docker-compose up -d
sleep 30
```

### 4.2 Running Unit Tests

```bash
cd backend
pytest tests/test_anomaly_detection.py -v
pytest tests/test_database.py -v
```

### 4.3 Running Integration Tests

```bash
pytest tests/test_integration.py -v
```

### 4.4 Running Performance Tests

```bash
pytest tests/test_performance.py -v --benchmark
```

---

## 5. Acceptance Criteria

### 5.1 Functional Acceptance
- All critical test cases (TC-DEV-*, TC-API-*, TC-INT-*) pass
- No severity 1 or 2 defects open
- All documented features operational

### 5.2 Performance Acceptance
- Telemetry ingestion: > 100 samples/second
- API response time: < 2 seconds (95th percentile)
- UI load time: < 3 seconds
- Database query time: < 1 second (typical queries)

### 5.3 Reliability Acceptance
- System uptime: > 99% over 7-day test
- No data loss under normal operation
- Graceful degradation under failure conditions

### 5.4 Usability Acceptance
- Operators can complete common tasks without training
- UI is responsive and intuitive
- Alarms are clear and actionable

---

## 6. Defect Management

### 6.1 Severity Levels

**Severity 1 (Critical):**
- System crash or data loss
- Security vulnerability
- Safety hazard

**Severity 2 (High):**
- Major feature not working
- Incorrect data or calculations
- Performance below requirements

**Severity 3 (Medium):**
- Minor feature issue
- Workaround available
- Cosmetic UI issue

**Severity 4 (Low):**
- Enhancement request
- Documentation error
- Minor cosmetic issue

### 6.2 Defect Tracking
- All defects logged in issue tracker
- Severity 1/2 defects must be resolved before release
- Severity 3/4 defects reviewed for inclusion

---

## 7. Test Schedule

| Phase | Duration | Activities |
|-------|----------|------------|
| Unit Testing | Week 1 | TC-DEV-*, TC-API-* (unit level) |
| Integration Testing | Week 2 | TC-INT-*, TC-API-* (integration) |
| System Testing | Week 3 | TC-UI-*, end-to-end scenarios |
| Performance Testing | Week 4 | TC-PERF-*, load testing |
| Reliability Testing | Week 5-6 | TC-REL-*, long-duration tests |
| Regression Testing | Week 7 | Re-run all critical tests |
| Acceptance Testing | Week 8 | User acceptance, final validation |

---

## 8. Test Deliverables

- Test execution reports
- Defect logs
- Performance benchmark results
- Test coverage metrics
- Acceptance test sign-off

---

**Document Version:** 1.0  
**Last Updated:** February 8, 2026  
**Approved By:** [Engineering Lead]
