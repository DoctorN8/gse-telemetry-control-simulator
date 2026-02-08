# GSE Operations Handbook

## Ground Power Unit (GPU) Operations

### GPU-001 Specifications

**Electrical Characteristics:**
- Output Voltage: 20-32 VDC (nominal 28V)
- Current Capacity: 0-150A continuous
- Power Output: Up to 5000W
- Voltage Regulation: ±0.5V
- Current Limiting: Adjustable, 0-150A

**Operating Limits:**
- Maximum Temperature: 85°C
- Safe Operating Temperature: 25-75°C
- Overtemperature Shutdown: 85°C
- Cooling: Forced air, fan-assisted

### GPU Standard Operating Procedures

#### SOP-GPU-001: Power-Up Sequence

1. **Pre-Start Checks:**
   - Verify all connections are secure
   - Check cooling system operation
   - Ensure load is disconnected
   - Verify voltage setpoint is at nominal (28V)

2. **Startup:**
   - Set mode to STANDBY
   - Wait 30 seconds for self-test completion
   - Set mode to ACTIVE
   - Monitor temperature (should be < 30°C)

3. **Output Enable:**
   - Verify mode is ACTIVE
   - Verify operational status is NOMINAL
   - Issue enable_output command
   - Monitor voltage rise to setpoint
   - Verify current draw is within expected range

4. **Verification:**
   - Voltage: 28.0V ±0.5V
   - Current: As required by load
   - Temperature: < 40°C under load
   - No active alarms

#### SOP-GPU-002: Normal Shutdown

1. **Load Disconnect:**
   - Notify downstream systems of impending shutdown
   - Wait for load acknowledgment
   - Issue disable_output command
   - Verify voltage drops to 0V

2. **Mode Change:**
   - Set mode to STANDBY
   - Monitor temperature decrease
   - Wait for temperature < 30°C

3. **Final Shutdown:**
   - Set mode to MAINTENANCE (if maintenance required)
   - Document final readings in log
   - Secure all connections

#### SOP-GPU-003: Emergency Shutdown

**When to Use:**
- Overtemperature condition (>80°C)
- Overcurrent condition (>145A)
- Smoke or unusual odors
- Electrical arcing
- Any safety concern

**Procedure:**
1. Issue EMERGENCY_SHUTDOWN command immediately
2. Verify output is disabled
3. Disconnect load if safe to do so
4. Notify supervisor and safety officer
5. Do not restart until cleared by engineering

#### SOP-GPU-004: Voltage Adjustment

**Safe Operating Range:** 20-32V

1. Verify output is disabled
2. Issue set_voltage command with desired value
3. Verify setpoint acceptance
4. Enable output
5. Monitor voltage stabilization (< 5 seconds)
6. Verify load response is acceptable

**Common Setpoints:**
- Standard Operations: 28.0V
- Battery Charging: 29.5V
- Low-Power Mode: 24.0V

#### SOP-GPU-005: Current Limit Adjustment

**Purpose:** Protect downstream equipment from overcurrent

1. Calculate maximum expected load current
2. Add 20% safety margin
3. Issue set_current_limit command
4. Verify limit is set correctly
5. Test with load (current should not exceed limit)

**Example:**
- Expected load: 80A
- Safety margin: 16A (20%)
- Set limit: 96A

### GPU Troubleshooting Guide

#### Problem: Output voltage low

**Symptoms:** Voltage < 27.5V under load

**Possible Causes:**
1. Excessive load current
2. Voltage setpoint incorrect
3. Internal regulation fault

**Resolution:**
1. Check current draw (should be < 150A)
2. Verify voltage setpoint (should be 28.0V)
3. Reduce load if current > 140A
4. If problem persists, initiate emergency shutdown

#### Problem: Overtemperature alarm

**Symptoms:** Temperature > 75°C, WARNING status

**Possible Causes:**
1. Cooling system failure
2. Excessive ambient temperature
3. Prolonged high-current operation
4. Blocked air vents

**Resolution:**
1. Check cooling fan operation
2. Verify air vents are clear
3. Reduce load current if > 120A
4. If temperature > 80°C, initiate emergency shutdown
5. Allow cooldown to < 30°C before restart

#### Problem: Cannot enable output

**Symptoms:** enable_output command fails

**Possible Causes:**
1. Mode is not ACTIVE
2. Operational status is FAULT
3. Active alarms present

**Resolution:**
1. Verify mode is ACTIVE (set if needed)
2. Check operational status
3. Clear any active faults
4. Acknowledge and resolve alarms
5. Retry enable_output command

---

## Cryogenic Line (CRYO) Operations

### CRYO-001 Specifications

**Fluid Characteristics:**
- Fluid Type: Liquid Nitrogen (LN2) or LOX
- Operating Temperature: -196°C to -150°C
- Operating Pressure: 14.7-70 psi
- Maximum Flow Rate: 500 L/min
- Tank Capacity: 1000L

**Valve Specifications:**
- Type: Pneumatic actuated ball valve
- Position Range: 0-100%
- Response Time: 10 seconds (0-100%)
- Control: Remote electric/pneumatic

**Safety Systems:**
- Pressure relief valve: 80 psi
- Temperature interlock: Valve disabled if T > -100°C
- Leak detection: Pressure drop monitoring
- Emergency shutoff: Manual and automatic

### CRYO Standard Operating Procedures

#### SOP-CRYO-001: Pre-Cooling Procedure

**Purpose:** Prepare line for cryogenic fluid transfer

1. **Initial Checks:**
   - Verify all connections are tight
   - Check valve is fully closed (0%)
   - Verify pressure is at ambient (14.7 psi)
   - Ensure downstream equipment is ready

2. **Cooldown:**
   - Set mode to ACTIVE
   - Monitor temperature decrease
   - Wait for temperature < -100°C (typically 10-15 minutes)
   - Verify no pressure buildup during cooldown

3. **Verification:**
   - Temperature: < -100°C
   - Pressure: 14.7-20 psi
   - Valve position: 0%
   - No active alarms

#### SOP-CRYO-002: Valve Operation

**CRITICAL SAFETY RULE:** Valve may only be operated when line temperature < -100°C

1. **Pre-Operation Checks:**
   - Verify temperature < -100°C
   - Verify mode is ACTIVE
   - Verify operational status is NOMINAL
   - Check downstream is ready for flow

2. **Opening Valve:**
   - Issue open_valve command with desired position
   - Monitor valve position feedback
   - Observe pressure increase
   - Monitor flow rate establishment
   - Verify temperature remains < -100°C

3. **Flow Monitoring:**
   - Pressure: Should stabilize at 20-60 psi
   - Flow rate: Proportional to valve position
   - Temperature: Should remain stable or decrease
   - Liquid level: Monitor depletion rate

4. **Closing Valve:**
   - Issue close_valve command
   - Monitor valve position decrease
   - Observe pressure decrease
   - Verify flow rate drops to zero

#### SOP-CRYO-003: Normal Shutdown

1. **Flow Termination:**
   - Close valve to 0%
   - Verify flow rate is zero
   - Monitor pressure stabilization
   - Wait 2 minutes for system stabilization

2. **Warmup (if required):**
   - Set mode to STANDBY
   - Allow natural warmup
   - Monitor temperature increase
   - Vent pressure as needed

3. **Final Checks:**
   - Verify valve is closed
   - Check for leaks
   - Document final readings
   - Set mode to MAINTENANCE if needed

#### SOP-CRYO-004: Emergency Shutdown

**When to Use:**
- Leak detected (rapid pressure drop)
- Valve stuck or unresponsive
- Downstream emergency
- Personnel safety concern
- Fire or explosion risk

**Procedure:**
1. Issue EMERGENCY_SHUTDOWN command immediately
2. Verify valve closes (or manually close if needed)
3. Activate emergency ventilation
4. Evacuate area if leak is significant
5. Notify supervisor and safety officer
6. Do not restart until cleared by engineering

#### SOP-CRYO-005: Leak Response

**Symptoms:**
- Rapid pressure drop (> 5 psi/min)
- Visible vapor cloud
- Frost formation on external surfaces
- Oxygen deficiency alarm (if in enclosed space)

**Immediate Actions:**
1. Issue close_valve command
2. Activate emergency ventilation
3. Evacuate personnel from immediate area
4. Monitor oxygen levels
5. Notify emergency response team

**Do Not:**
- Attempt to locate leak while system is pressurized
- Enter vapor cloud
- Touch frosted surfaces
- Restart system until leak is repaired

### CRYO Troubleshooting Guide

#### Problem: Valve won't open

**Symptoms:** open_valve command rejected or valve doesn't move

**Possible Causes:**
1. Temperature too high (> -100°C)
2. Mode not ACTIVE
3. Valve stuck fault
4. Pneumatic pressure loss

**Resolution:**
1. Check temperature (must be < -100°C)
2. Verify mode is ACTIVE
3. Check for valve_stuck fault
4. If stuck, clear fault and retry
5. If problem persists, use manual override

#### Problem: Pressure too high

**Symptoms:** Pressure > 70 psi, WARNING or FAULT status

**Possible Causes:**
1. Valve position too high
2. Downstream restriction
3. Pressure relief valve failure

**Resolution:**
1. Reduce valve position immediately
2. If pressure > 75 psi, close valve completely
3. Check downstream for blockages
4. If pressure > 80 psi, initiate emergency shutdown
5. Verify pressure relief valve operation

#### Problem: Flow rate lower than expected

**Symptoms:** Flow rate < expected for valve position

**Possible Causes:**
1. Low liquid level in tank
2. Upstream restriction
3. Valve partially stuck
4. Pressure too low

**Resolution:**
1. Check liquid level (should be > 20%)
2. Verify upstream pressure is adequate
3. Check valve position feedback matches command
4. Increase valve position if safe to do so
5. If no improvement, close valve and investigate

---

## Safety Procedures

### General Safety Rules

1. **Never bypass safety interlocks**
2. **Always wear appropriate PPE:**
   - Cryogenic operations: Face shield, insulated gloves, long sleeves
   - Electrical operations: Insulated gloves, safety glasses
3. **Maintain clear communication with team**
4. **Follow lockout/tagout procedures**
5. **Report all anomalies immediately**

### Emergency Contacts

- **Control Room:** Extension 1000
- **Safety Officer:** Extension 1111
- **Engineering:** Extension 2000
- **Emergency Services:** 911

### Alarm Response Matrix

| Severity | Response Time | Action Required |
|----------|--------------|-----------------|
| NOMINAL | N/A | Normal monitoring |
| INFO | 5 minutes | Acknowledge, log |
| WARNING | 2 minutes | Investigate, acknowledge |
| FAULT | Immediate | Emergency response, shutdown if needed |
| CRITICAL | Immediate | Emergency shutdown, evacuate if needed |

---

## Maintenance Procedures

### GPU Maintenance Schedule

**Daily:**
- Visual inspection
- Temperature check
- Cooling system verification

**Weekly:**
- Connection tightness check
- Voltage calibration verification
- Current limit test

**Monthly:**
- Full load test
- Temperature sensor calibration
- Cooling fan replacement (if needed)

**Annually:**
- Complete electrical inspection
- Insulation resistance test
- Replacement of wear items

### CRYO Maintenance Schedule

**Daily:**
- Leak check
- Valve operation test
- Pressure sensor verification

**Weekly:**
- Valve position calibration
- Temperature sensor check
- Pressure relief valve test

**Monthly:**
- Full system pressure test
- Valve actuator inspection
- Insulation inspection

**Annually:**
- Complete valve overhaul
- Pressure vessel inspection
- Safety system certification

---

**Document Version:** 1.0  
**Last Updated:** February 8, 2026  
**Next Review:** May 8, 2026
