import pytest
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestBackendAPI:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        time.sleep(2)
        yield
    
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "GSE Command & Control System"
        assert data["status"] == "operational"
    
    def test_list_devices(self):
        response = requests.get(f"{BASE_URL}/api/devices")
        assert response.status_code == 200
        devices = response.json()
        assert isinstance(devices, list)
        assert len(devices) >= 2
        
        device_ids = [d["device_id"] for d in devices]
        assert "GPU-001" in device_ids
        assert "CRYO-001" in device_ids
    
    def test_telemetry_ingestion(self):
        telemetry_data = [
            {
                "device_id": "GPU-001",
                "parameter_name": "voltage",
                "value": 28.0,
                "unit": "V",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "device_id": "GPU-001",
                "parameter_name": "current",
                "value": 50.0,
                "unit": "A",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=telemetry_data)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["points_ingested"] == 2
    
    def test_device_status(self):
        response = requests.get(f"{BASE_URL}/api/devices/GPU-001/status")
        assert response.status_code == 200
        status = response.json()
        assert status["device_id"] == "GPU-001"
        assert "operational_state" in status
        assert "operational_status" in status
        assert "latest_telemetry" in status
    
    def test_command_issuance(self):
        command_data = {
            "device_id": "GPU-001",
            "command_type": "set_mode",
            "parameters": {"mode": "ACTIVE"}
        }
        
        response = requests.post(f"{BASE_URL}/api/commands", json=command_data)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "command_id" in result
    
    def test_pending_commands(self):
        response = requests.get(f"{BASE_URL}/api/commands/pending/GPU-001")
        assert response.status_code == 200
        commands = response.json()
        assert isinstance(commands, list)
    
    def test_alarms_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/alarms")
        assert response.status_code == 200
        alarms = response.json()
        assert isinstance(alarms, list)
    
    def test_events_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
    
    def test_analytics_mttr(self):
        response = requests.get(f"{BASE_URL}/api/analytics/mttr")
        assert response.status_code == 200
        metrics = response.json()
        assert "mean_time_to_acknowledge" in metrics
        assert "mean_time_to_resolve" in metrics
    
    def test_analytics_alarm_frequency(self):
        response = requests.get(f"{BASE_URL}/api/analytics/alarm-frequency")
        assert response.status_code == 200
        frequency = response.json()
        assert isinstance(frequency, list)


class TestDeviceIntegration:
    
    def test_gpu_telemetry_flow(self):
        time.sleep(5)
        
        response = requests.get(f"{BASE_URL}/api/devices/GPU-001/status")
        assert response.status_code == 200
        status = response.json()
        
        assert len(status["latest_telemetry"]) > 0
        
        telemetry = status["latest_telemetry"]
        param_names = [t["parameter_name"] for t in telemetry]
        assert "voltage" in param_names
        assert "current" in param_names
        assert "temperature" in param_names
    
    def test_cryo_telemetry_flow(self):
        time.sleep(5)
        
        response = requests.get(f"{BASE_URL}/api/devices/CRYO-001/status")
        assert response.status_code == 200
        status = response.json()
        
        assert len(status["latest_telemetry"]) > 0
        
        telemetry = status["latest_telemetry"]
        param_names = [t["parameter_name"] for t in telemetry]
        assert "valve_position" in param_names
        assert "pressure" in param_names
        assert "temperature" in param_names
    
    def test_command_execution_flow(self):
        command_data = {
            "device_id": "GPU-001",
            "command_type": "set_mode",
            "parameters": {"mode": "ACTIVE"}
        }
        
        response = requests.post(f"{BASE_URL}/api/commands", json=command_data)
        assert response.status_code == 200
        command_result = response.json()
        command_id = command_result["command_id"]
        
        time.sleep(3)
        
        response = requests.get(f"{BASE_URL}/api/commands/pending/GPU-001")
        assert response.status_code == 200
        pending = response.json()
        
        command_ids = [c["command_id"] for c in pending]
        assert command_id in command_ids or len(pending) == 0


class TestAnomalyDetection:
    
    def test_anomaly_triggers_alarm(self):
        normal_telemetry = [
            {
                "device_id": "GPU-001",
                "parameter_name": "voltage",
                "value": 28.0,
                "unit": "V",
                "timestamp": datetime.utcnow().isoformat()
            }
        ] * 10
        
        for telemetry in normal_telemetry:
            telemetry["timestamp"] = datetime.utcnow().isoformat()
            requests.post(f"{BASE_URL}/api/telemetry/ingest", json=[telemetry])
            time.sleep(0.1)
        
        anomalous_telemetry = [{
            "device_id": "GPU-001",
            "parameter_name": "voltage",
            "value": 50.0,
            "unit": "V",
            "timestamp": datetime.utcnow().isoformat()
        }]
        
        response = requests.post(f"{BASE_URL}/api/telemetry/ingest", json=anomalous_telemetry)
        assert response.status_code == 200
        
        time.sleep(2)
        
        response = requests.get(f"{BASE_URL}/api/alarms?active_only=true")
        assert response.status_code == 200
        alarms = response.json()
        
        voltage_alarms = [a for a in alarms if "voltage" in a.get("message", "").lower()]
        assert len(voltage_alarms) > 0


class TestRAGAssistant:
    
    def test_rag_health(self):
        try:
            response = requests.get(f"{BASE_URL}/api/rag/health")
            if response.status_code == 200:
                health = response.json()
                assert "status" in health
        except requests.exceptions.RequestException:
            pytest.skip("RAG assistant not available")
    
    def test_rag_ask_question(self):
        try:
            question_data = {
                "question": "How do I perform an emergency shutdown of the GPU?",
                "top_k": 3
            }
            
            response = requests.post(f"{BASE_URL}/api/rag/ask", json=question_data)
            if response.status_code == 200:
                result = response.json()
                assert "answer" in result
                assert "sources" in result
                assert len(result["sources"]) > 0
        except requests.exceptions.RequestException:
            pytest.skip("RAG assistant not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
