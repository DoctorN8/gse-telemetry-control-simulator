import random
import time
from datetime import datetime
from typing import Dict, Any
from base_device import BaseDevice, TelemetryPoint


class GroundPowerUnit(BaseDevice):
    def __init__(self, device_id: str, backend_url: str):
        super().__init__(device_id, "ground_power_unit", backend_url)
        
        self.voltage_setpoint = 28.0
        self.current_limit = 100.0
        self.temperature = 25.0
        self.output_enabled = False
        
        self.voltage_actual = 0.0
        self.current_actual = 0.0
        self.power_actual = 0.0
        
        self.fault_injected = False
        self.overheat_injected = False
        
    def generate_telemetry(self) -> list[TelemetryPoint]:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if self.output_enabled:
            voltage_noise = random.gauss(0, 0.1)
            self.voltage_actual = self.voltage_setpoint + voltage_noise
            
            load_factor = random.uniform(0.3, 0.9)
            self.current_actual = self.current_limit * load_factor + random.gauss(0, 0.5)
            
            self.power_actual = self.voltage_actual * self.current_actual
            
            self.temperature += random.uniform(-0.5, 1.5)
            if self.temperature > 85.0:
                self.temperature = 85.0
                self.overheat_injected = True
                self.operational_status = "FAULT"
        else:
            self.voltage_actual = 0.0
            self.current_actual = 0.0
            self.power_actual = 0.0
            
            self.temperature += random.uniform(-1.0, 0.2)
            if self.temperature < 25.0:
                self.temperature = 25.0
        
        if self.overheat_injected and self.temperature > 80.0:
            voltage_status = "FAULT"
            current_status = "FAULT"
            temp_status = "FAULT"
        elif self.temperature > 75.0:
            temp_status = "WARNING"
            voltage_status = "NOMINAL"
            current_status = "NOMINAL"
        else:
            voltage_status = "NOMINAL"
            current_status = "NOMINAL"
            temp_status = "NOMINAL"
        
        if self.current_actual > self.current_limit * 0.95:
            current_status = "WARNING"
        
        telemetry = [
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="voltage",
                value=round(self.voltage_actual, 2),
                unit="V",
                status=voltage_status
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="current",
                value=round(self.current_actual, 2),
                unit="A",
                status=current_status
            ),
            TelemetryPoint(
                device_id=self.device_id,
                device_type=self.device_type,
                timestamp=timestamp,
                parameter="power",
                value=round(self.power_actual, 2),
                unit="W",
                status="NOMINAL"
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
                    self.output_enabled = False
                    self.operational_status = "SHUTDOWN"
                return {"success": True, "message": f"Mode set to {new_mode}"}
            else:
                return {"success": False, "message": f"Invalid mode: {new_mode}"}
        
        elif cmd_type == "enable_output":
            if self.mode == "ACTIVE" and self.operational_status != "FAULT":
                self.output_enabled = True
                return {"success": True, "message": "Output enabled"}
            else:
                return {"success": False, "message": f"Cannot enable output in mode {self.mode} with status {self.operational_status}"}
        
        elif cmd_type == "disable_output":
            self.output_enabled = False
            return {"success": True, "message": "Output disabled"}
        
        elif cmd_type == "set_voltage":
            voltage = params.get("voltage", 28.0)
            if 20.0 <= voltage <= 32.0:
                self.voltage_setpoint = voltage
                return {"success": True, "message": f"Voltage setpoint set to {voltage}V"}
            else:
                return {"success": False, "message": f"Voltage {voltage}V out of range (20-32V)"}
        
        elif cmd_type == "set_current_limit":
            current = params.get("current", 100.0)
            if 0.0 <= current <= 150.0:
                self.current_limit = current
                return {"success": True, "message": f"Current limit set to {current}A"}
            else:
                return {"success": False, "message": f"Current {current}A out of range (0-150A)"}
        
        elif cmd_type == "inject_fault":
            self.fault_injected = True
            self.operational_status = "FAULT"
            self.output_enabled = False
            return {"success": True, "message": "Fault injected"}
        
        elif cmd_type == "clear_fault":
            self.fault_injected = False
            self.overheat_injected = False
            self.operational_status = "NOMINAL"
            self.temperature = 25.0
            return {"success": True, "message": "Fault cleared"}
        
        else:
            return {"success": False, "message": f"Unknown command: {cmd_type}"}
