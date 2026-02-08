import asyncio
import os
import sys
from ground_power_unit import GroundPowerUnit
from cryogenic_line import CryogenicLine


async def main():
    device_type = os.getenv("DEVICE_TYPE", "ground_power_unit")
    device_id = os.getenv("DEVICE_ID", "DEVICE-001")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    telemetry_rate = float(os.getenv("TELEMETRY_RATE_HZ", "5.0"))
    
    print(f"Starting {device_type} with ID {device_id}")
    print(f"Backend URL: {backend_url}")
    print(f"Telemetry rate: {telemetry_rate} Hz")
    
    if device_type == "ground_power_unit":
        device = GroundPowerUnit(device_id, backend_url)
    elif device_type == "cryogenic_line":
        device = CryogenicLine(device_id, backend_url)
    else:
        print(f"Unknown device type: {device_type}")
        sys.exit(1)
    
    try:
        await device.run(telemetry_rate_hz=telemetry_rate)
    except KeyboardInterrupt:
        print(f"\n[{device_id}] Shutting down...")
        device.stop()


if __name__ == "__main__":
    asyncio.run(main())
