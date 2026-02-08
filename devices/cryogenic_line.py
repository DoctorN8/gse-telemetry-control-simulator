import random
import time
from datetime import datetime
from typing import Dict, Any
from base_device import BaseDevice, TelemetryPoint


class CryogenicLine(BaseDevice):
    def __init__(self, device_id: str, backend_url: str):
        super().__init__(device_id, "cryogenic_line", backend_url)
        
        self.valve_position = 0.0
        self.valve_commanded = 0.0
        
        self.pressure = 14.7
        self.flow_rate = 0.0
        self.temperature = -150.0
        self.liquid_level = 75.0
        
        self.leak_injected = False
        self.valve_stuck = False
        
    def generate_telemetry(self) -> list[TelemetryPoint]:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if not self.valve_stuck:
            valve_diff = self.valve_commanded - self.valve_position
            self.valve_position += valve_diff * 0.1
            if abs(valve_diff) < 0.5:
                self.valve_position = self.valve_commanded
        
        if self.valve_position > 5.0:
            base_flow = (self.valve_position / 100.0) * 500.0
            self.flow_rate = base_flow + random.gauss(0, 5.0)
            
            pressure_increase = (self.valve_position / 100.0) * 50.0
            self.pressure = 14.7 + pressure_increase + random.gauss(0, 2.0)
            
            temp_decrease = (self.valve_position / 100.0) * 100.0
            self.temperature = -150.0 - temp_decrease + random.gauss(0, 5.0)
            
            self.liquid_level -= (self.flow_rate / 500.0) * 0.1
            if self.liquid_level < 0:
                self.liquid_level = 0
        else:
            self.flow_rate = random.gauss(0, 0.5)
            if self.flow_rate < 0:
                self.flow_rate = 0
            
            self.pressure = 14.7 + random.gauss(0, 0.5)
            self.temperature = -150.0 + random.gauss(0, 2.0)
            
            self.liquid_level += random.uniform(0, 0.05)
            if self.liquid_level > 100:
                self.liquid_level = 100
        
        if self.leak_injected:
            self.pressure -= random.uniform(0.5, 2.0)
            if self.pressure < 5.0:
                self.pressure = 5.0
            self.operational_status = "FAULT"
        
        pressure_status = "NOMINAL"
        if self.pressure > 80.0:
            pressure_status = "FAULT"
            self.operational_status = "FAULT"
        elif self.pressure > 70.0:
            pressure_status = "WARNING"
        elif self.pressure < 10.0:
            pressure_status = "WARNING"
        
        flow_status = "NOMINAL"
        if self.flow_rate > 480.0:
            flow_status = "WARNING"
        
        temp_status = "NOMINAL"
        if self.temperature > -100.0:
            temp_status = "WARNING"
        if self.temperature > -50.0:
            temp_status = "FAULT"
            self.operational_status = "FAULT"
        
        level_status = "NOMINAL"
        if self.liquid_level < 20.0:
            level_status = "WARNING"
        if self.liquid_level < 10.0:
            level_status = "FAULT"
        
        telemetry = [
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="valve_position",
                value=round(self.valve_position, 2),
                unit="%",
                status="NOMINAL"
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="pressure",
                value=round(self.pressure, 2),
                unit="psi",
                status=pressure_status
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="flow_rate",
                value=round(self.flow_rate, 2),
                unit="L/min",
                status=flow_status
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="temperature",
                value=round(self.temperature, 2),
                unit="°C",
                status=temp_status
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="liquid_level",
                value=round(self.liquid_level, 2),
                unit="%",
                status=level_status
            ),
        ]
        
        return telemetry
    
    def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = command.get("command_type")
        params = command.get("parameters", {})
        
        self.last_command = cmd_type
        self.last_command_time = datetime.utcnow().isoformat() + "Z"
        
        print(f"[{self.device_id}] Processing command: {cmd_type} with params: {params}")
        
        if cmd_type == "set_mode":
            new_mode = params.get("mode", "STANDBY")
            if new_mode in ["STANDBY", "ACTIVE", "MAINTENANCE", "EMERGENCY_SHUTDOWN"]:
                self.mode = new_mode
                if new_mode == "EMERGENCY_SHUTDOWN":
                    self.valve_commanded = 0.0
                    self.operational_status = "SHUTDOWN"
                return {"success": True, "message": f"Mode set to {new_mode}"}
            else:
                return {"success": False, "message": f"Invalid mode: {new_mode}"}
        
        elif cmd_type == "open_valve":
            if self.mode == "ACTIVE" and not self.valve_stuck:
                position = params.get("position", 100.0)
                if 0.0 <= position <= 100.0:
                    if self.temperature < -100.0:
                        self.valve_commanded = position
                        return {"success": True, "message": f"Valve opening to {position}%"}
                    else:
                        return {"success": False, "message": f"Temperature too high ({self.temperature}°C) for valve operation"}
                else:
                    return {"success": False, "message": f"Position {position}% out of range (0-100%)"}
            else:
                return {"success": False, "message": f"Cannot open valve in mode {self.mode} or valve stuck"}
        
        elif cmd_type == "close_valve":
            if not self.valve_stuck:
                self.valve_commanded = 0.0
                return {"success": True, "message": "Valve closing"}
            else:
                return {"success": False, "message": "Valve is stuck"}
        
        elif cmd_type == "inject_leak":
            self.leak_injected = True
            self.operational_status = "FAULT"
            return {"success": True, "message": "Leak injected"}
        
        elif cmd_type == "inject_valve_stuck":
            self.valve_stuck = True
            return {"success": True, "message": "Valve stuck fault injected"}
        
        elif cmd_type == "clear_fault":
            self.leak_injected = False
            self.valve_stuck = False
            self.operational_status = "NOMINAL"
            return {"success": True, "message": "Fault cleared"}
        
        else:
            return {"success": False, "message": f"Unknown command: {cmd_type}"}
