import asyncio
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
import os


@dataclass
class TelemetryPoint:
    device_id: str
    device_type: str
    timestamp: str
    parameter: str
    value: float
    unit: str
    status: str


@dataclass
class DeviceState:
    device_id: str
    device_type: str
    mode: str
    operational_status: str
    last_command: Optional[str]
    last_command_time: Optional[str]


class BaseDevice(ABC):
    def __init__(self, device_id: str, device_type: str, backend_url: str):
        self.device_id = device_id
        self.device_type = device_type
        self.backend_url = backend_url
        self.mode = "STANDBY"
        self.operational_status = "NOMINAL"
        self.last_command = None
        self.last_command_time = None
        self.running = False
        
    @abstractmethod
    def generate_telemetry(self) -> list[TelemetryPoint]:
        pass
    
    @abstractmethod
    def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def get_state(self) -> DeviceState:
        return DeviceState(
            device_id=self.device_id,
            device_type=self.device_type,
            mode=self.mode,
            operational_status=self.operational_status,
            last_command=self.last_command,
            last_command_time=self.last_command_time
        )
    
    async def send_telemetry(self, telemetry: list[TelemetryPoint]):
        async with httpx.AsyncClient() as client:
            try:
                payload = [asdict(t) for t in telemetry]
                response = await client.post(
                    f"{self.backend_url}/api/telemetry/ingest",
                    json=payload,
                    timeout=5.0
                )
                if response.status_code != 200:
                    print(f"[{self.device_id}] Failed to send telemetry: {response.status_code}")
            except Exception as e:
                print(f"[{self.device_id}] Error sending telemetry: {e}")
    
    async def send_state(self):
        async with httpx.AsyncClient() as client:
            try:
                state = asdict(self.get_state())
                response = await client.post(
                    f"{self.backend_url}/api/devices/state",
                    json=state,
                    timeout=5.0
                )
                if response.status_code != 200:
                    print(f"[{self.device_id}] Failed to send state: {response.status_code}")
            except Exception as e:
                print(f"[{self.device_id}] Error sending state: {e}")
    
    async def poll_commands(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.backend_url}/api/commands/pending/{self.device_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    commands = response.json()
                    for cmd in commands:
                        result = self.process_command(cmd)
                        await client.post(
                            f"{self.backend_url}/api/commands/acknowledge",
                            json={"command_id": cmd["id"], "result": result},
                            timeout=5.0
                        )
            except Exception as e:
                print(f"[{self.device_id}] Error polling commands: {e}")
    
    async def run(self, telemetry_rate_hz: float = 5.0):
        self.running = True
        interval = 1.0 / telemetry_rate_hz
        
        print(f"[{self.device_id}] Starting device simulation at {telemetry_rate_hz} Hz")
        
        while self.running:
            try:
                telemetry = self.generate_telemetry()
                await self.send_telemetry(telemetry)
                await self.send_state()
                await self.poll_commands()
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"[{self.device_id}] Error in main loop: {e}")
                await asyncio.sleep(interval)
    
    def stop(self):
        self.running = False
