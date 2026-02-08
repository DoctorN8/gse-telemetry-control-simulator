import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="GSE Command & Control",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .status-nominal { color: #00FF00; font-weight: bold; }
    .status-warning { color: #FFA500; font-weight: bold; }
    .status-fault { color: #FF0000; font-weight: bold; }
    .device-card {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #333;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)


def get_status_color(status):
    colors = {
        "NOMINAL": "#00FF00",
        "WARNING": "#FFA500",
        "FAULT": "#FF0000",
        "SHUTDOWN": "#808080",
        "UNKNOWN": "#CCCCCC"
    }
    return colors.get(status, "#CCCCCC")


def fetch_devices():
    try:
        response = requests.get(f"{BACKEND_URL}/api/devices", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching devices: {e}")
        return []


def fetch_device_status(device_id):
    try:
        response = requests.get(f"{BACKEND_URL}/api/devices/{device_id}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching device status: {e}")
        return None


def fetch_device_telemetry(device_id, parameter=None, limit=100):
    try:
        params = {"limit": limit}
        if parameter:
            params["parameter"] = parameter
        response = requests.get(
            f"{BACKEND_URL}/api/devices/{device_id}/telemetry",
            params=params,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching telemetry: {e}")
        return []


def fetch_alarms(active_only=True):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/alarms",
            params={"active_only": active_only},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching alarms: {e}")
        return []


def fetch_events(limit=100):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/events",
            params={"limit": limit},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching events: {e}")
        return []


def issue_command(device_id, command_type, parameters=None, issued_by="operator"):
    try:
        payload = {
            "device_id": device_id,
            "command_type": command_type,
            "parameters": parameters or {},
            "issued_by": issued_by
        }
        response = requests.post(
            f"{BACKEND_URL}/api/commands",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Command failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error issuing command: {e}")
        return None


def acknowledge_alarm(alarm_id, acknowledged_by="operator"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/alarms/{alarm_id}/acknowledge",
            params={"acknowledged_by": acknowledged_by},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error acknowledging alarm: {e}")
        return False


def main():
    st.title("🚀 GSE Command & Control System")
    st.markdown("**Ground Support Equipment Telemetry and Control**")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["Overview", "Device Control", "Telemetry Monitor", "Alarms & Events", "Analytics", "Launch Checklist"]
    )
    
    if menu == "Overview":
        show_overview()
    elif menu == "Device Control":
        show_device_control()
    elif menu == "Telemetry Monitor":
        show_telemetry_monitor()
    elif menu == "Alarms & Events":
        show_alarms_events()
    elif menu == "Analytics":
        show_analytics()
    elif menu == "Launch Checklist":
        show_launch_checklist()


def show_overview():
    st.header("System Overview")
    
    devices = fetch_devices()
    alarms = fetch_alarms(active_only=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Devices", len(devices))
    
    with col2:
        active_alarms = len([a for a in alarms if not a["cleared"]])
        st.metric("Active Alarms", active_alarms, delta=None if active_alarms == 0 else "⚠️")
    
    with col3:
        critical_alarms = len([a for a in alarms if a["severity"] in ["FAULT", "CRITICAL"] and not a["cleared"]])
        st.metric("Critical Alarms", critical_alarms, delta=None if critical_alarms == 0 else "🚨")
    
    with col4:
        st.metric("System Status", "OPERATIONAL", delta="✓")
    
    st.markdown("---")
    
    st.subheader("Device Status")
    
    for device in devices:
        status = fetch_device_status(device["device_id"])
        if status:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                
                with col1:
                    st.markdown(f"**{device['device_id']}**")
                    st.caption(device['device_type'].replace('_', ' ').title())
                
                with col2:
                    status_color = get_status_color(status['operational_status'])
                    st.markdown(
                        f"<span style='color: {status_color};'>● {status['operational_status']}</span>",
                        unsafe_allow_html=True
                    )
                
                with col3:
                    st.text(f"Mode: {status['mode']}")
                
                with col4:
                    if status['current_telemetry']:
                        telemetry_str = " | ".join([
                            f"{k}: {v:.2f}" for k, v in list(status['current_telemetry'].items())[:3]
                        ])
                        st.caption(telemetry_str)
                
                st.markdown("---")
    
    if alarms:
        st.subheader("Recent Alarms")
        alarm_df = pd.DataFrame(alarms[:10])
        st.dataframe(
            alarm_df[['device_id', 'parameter', 'severity', 'alarm_type', 'triggered_at', 'acknowledged']],
            use_container_width=True
        )


def show_device_control():
    st.header("Device Control")
    
    devices = fetch_devices()
    
    if not devices:
        st.warning("No devices available")
        return
    
    device_options = {f"{d['device_id']} ({d['device_type']})": d['device_id'] for d in devices}
    selected_device_label = st.selectbox("Select Device", list(device_options.keys()))
    selected_device = device_options[selected_device_label]
    
    status = fetch_device_status(selected_device)
    
    if not status:
        st.error("Could not fetch device status")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Device Status")
        st.markdown(f"**Device ID:** {status['device_id']}")
        st.markdown(f"**Type:** {status['device_type'].replace('_', ' ').title()}")
        
        status_color = get_status_color(status['operational_status'])
        st.markdown(
            f"**Status:** <span style='color: {status_color};'>{status['operational_status']}</span>",
            unsafe_allow_html=True
        )
        st.markdown(f"**Mode:** {status['mode']}")
        
        if status['last_command']:
            st.markdown(f"**Last Command:** {status['last_command']}")
            if status['last_command_time']:
                st.caption(f"At: {status['last_command_time']}")
    
    with col2:
        st.subheader("Current Telemetry")
        if status['current_telemetry']:
            telemetry_cols = st.columns(2)
            for idx, (param, value) in enumerate(status['current_telemetry'].items()):
                with telemetry_cols[idx % 2]:
                    st.metric(param.replace('_', ' ').title(), f"{value:.2f}")
        else:
            st.info("No telemetry data available")
    
    st.markdown("---")
    st.subheader("Command Control")
    
    if status['device_type'] == 'ground_power_unit':
        show_gpu_controls(selected_device, status)
    elif status['device_type'] == 'cryogenic_line':
        show_cryo_controls(selected_device, status)


def show_gpu_controls(device_id, status):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Mode Control**")
        mode = st.selectbox("Set Mode", ["STANDBY", "ACTIVE", "MAINTENANCE", "EMERGENCY_SHUTDOWN"])
        if st.button("Set Mode", key="set_mode_gpu"):
            result = issue_command(device_id, "set_mode", {"mode": mode})
            if result and result.get("success"):
                st.success(f"Mode set to {mode}")
            else:
                st.error("Command failed")
    
    with col2:
        st.markdown("**Output Control**")
        if st.button("Enable Output", key="enable_output"):
            result = issue_command(device_id, "enable_output")
            if result and result.get("success"):
                st.success("Output enabled")
        
        if st.button("Disable Output", key="disable_output"):
            result = issue_command(device_id, "disable_output")
            if result and result.get("success"):
                st.success("Output disabled")
    
    with col3:
        st.markdown("**Setpoints**")
        voltage = st.number_input("Voltage (V)", min_value=20.0, max_value=32.0, value=28.0, step=0.1)
        if st.button("Set Voltage", key="set_voltage"):
            result = issue_command(device_id, "set_voltage", {"voltage": voltage})
            if result and result.get("success"):
                st.success(f"Voltage set to {voltage}V")
        
        current = st.number_input("Current Limit (A)", min_value=0.0, max_value=150.0, value=100.0, step=1.0)
        if st.button("Set Current Limit", key="set_current"):
            result = issue_command(device_id, "set_current_limit", {"current": current})
            if result and result.get("success"):
                st.success(f"Current limit set to {current}A")
    
    st.markdown("---")
    st.markdown("**Fault Injection (Testing)**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Inject Fault", key="inject_fault_gpu"):
            result = issue_command(device_id, "inject_fault")
            if result:
                st.warning("Fault injected")
    with col2:
        if st.button("Clear Fault", key="clear_fault_gpu"):
            result = issue_command(device_id, "clear_fault")
            if result:
                st.success("Fault cleared")


def show_cryo_controls(device_id, status):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Mode Control**")
        mode = st.selectbox("Set Mode", ["STANDBY", "ACTIVE", "MAINTENANCE", "EMERGENCY_SHUTDOWN"])
        if st.button("Set Mode", key="set_mode_cryo"):
            result = issue_command(device_id, "set_mode", {"mode": mode})
            if result and result.get("success"):
                st.success(f"Mode set to {mode}")
    
    with col2:
        st.markdown("**Valve Control**")
        position = st.slider("Valve Position (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        if st.button("Open Valve", key="open_valve"):
            result = issue_command(device_id, "open_valve", {"position": position})
            if result and result.get("success"):
                st.success(f"Valve opening to {position}%")
            else:
                st.error("Command failed - check temperature and mode")
        
        if st.button("Close Valve", key="close_valve"):
            result = issue_command(device_id, "close_valve")
            if result and result.get("success"):
                st.success("Valve closing")
    
    with col3:
        st.markdown("**Safety Status**")
        current_temp = status['current_telemetry'].get('temperature', 0)
        if current_temp < -100.0:
            st.success("✓ Temperature OK for valve operation")
        else:
            st.error("⚠️ Temperature too high for valve operation")
        
        current_pressure = status['current_telemetry'].get('pressure', 0)
        if current_pressure < 70.0:
            st.success("✓ Pressure within safe limits")
        else:
            st.warning("⚠️ Pressure approaching limits")
    
    st.markdown("---")
    st.markdown("**Fault Injection (Testing)**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Inject Leak", key="inject_leak"):
            result = issue_command(device_id, "inject_leak")
            if result:
                st.warning("Leak injected")
    with col2:
        if st.button("Inject Valve Stuck", key="inject_valve_stuck"):
            result = issue_command(device_id, "inject_valve_stuck")
            if result:
                st.warning("Valve stuck fault injected")
    with col3:
        if st.button("Clear Fault", key="clear_fault_cryo"):
            result = issue_command(device_id, "clear_fault")
            if result:
                st.success("Fault cleared")


def show_telemetry_monitor():
    st.header("Telemetry Monitor")
    
    devices = fetch_devices()
    
    if not devices:
        st.warning("No devices available")
        return
    
    device_options = {f"{d['device_id']} ({d['device_type']})": d['device_id'] for d in devices}
    selected_device_label = st.selectbox("Select Device", list(device_options.keys()))
    selected_device = device_options[selected_device_label]
    
    status = fetch_device_status(selected_device)
    
    if not status or not status['current_telemetry']:
        st.warning("No telemetry data available")
        return
    
    parameters = list(status['current_telemetry'].keys())
    selected_params = st.multiselect("Select Parameters", parameters, default=parameters[:2])
    
    if not selected_params:
        st.info("Select at least one parameter to display")
        return
    
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    for param in selected_params:
        telemetry_data = fetch_device_telemetry(selected_device, parameter=param, limit=100)
        
        if telemetry_data:
            df = pd.DataFrame(telemetry_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['value'],
                mode='lines+markers',
                name=param,
                line=dict(width=2),
                marker=dict(size=4)
            ))
            
            fig.update_layout(
                title=f"{param.replace('_', ' ').title()} - {selected_device}",
                xaxis_title="Time",
                yaxis_title=f"{param} ({df['unit'].iloc[0] if not df.empty else ''})",
                height=300,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)


def show_alarms_events():
    st.header("Alarms & Events")
    
    tab1, tab2 = st.tabs(["Active Alarms", "Event Log"])
    
    with tab1:
        st.subheader("Active Alarms")
        
        alarms = fetch_alarms(active_only=True)
        
        if not alarms:
            st.success("No active alarms")
        else:
            for alarm in alarms:
                severity_color = get_status_color(alarm['severity'])
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                    
                    with col1:
                        st.markdown(f"**{alarm['device_id']}**")
                        st.caption(alarm['parameter'])
                    
                    with col2:
                        st.markdown(
                            f"<span style='color: {severity_color};'>● {alarm['severity']}</span>",
                            unsafe_allow_html=True
                        )
                        st.caption(alarm['alarm_type'])
                    
                    with col3:
                        st.text(f"Value: {alarm['actual_value']:.2f}")
                        if alarm['threshold_value']:
                            st.caption(f"Threshold: {alarm['threshold_value']:.2f}")
                    
                    with col4:
                        if not alarm['acknowledged']:
                            if st.button("Acknowledge", key=f"ack_{alarm['alarm_id']}"):
                                if acknowledge_alarm(alarm['alarm_id']):
                                    st.success("Alarm acknowledged")
                                    st.rerun()
                        else:
                            st.caption(f"Ack by: {alarm['acknowledged_by']}")
                    
                    st.markdown("---")
    
    with tab2:
        st.subheader("Event Log")
        
        events = fetch_events(limit=50)
        
        if events:
            event_df = pd.DataFrame(events)
            event_df['timestamp'] = pd.to_datetime(event_df['timestamp'])
            
            st.dataframe(
                event_df[['timestamp', 'device_id', 'event_type', 'severity', 'description']],
                use_container_width=True,
                height=400
            )
        else:
            st.info("No events recorded")


def show_analytics():
    st.header("Analytics & Reporting")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/analytics/mttr", timeout=5)
        if response.status_code == 200:
            mttr_data = response.json()
            
            st.subheader("Mean Time To Repair (MTTR) Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Mean Time to Acknowledge", f"{mttr_data['mean_time_to_acknowledge']:.1f}s")
            
            with col2:
                st.metric("Mean Time to Resolve", f"{mttr_data['mean_time_to_resolve']:.1f}s")
            
            with col3:
                st.metric("Total Alarms", mttr_data['total_alarms'])
            
            with col4:
                st.metric("Cleared Alarms", mttr_data['cleared_alarms'])
        
        response = requests.get(f"{BACKEND_URL}/api/analytics/alarm-frequency", timeout=5)
        if response.status_code == 200:
            freq_data = response.json()
            
            if freq_data:
                st.subheader("Alarm Frequency by Device")
                
                df = pd.DataFrame(freq_data)
                fig = px.bar(
                    df,
                    x='device_id',
                    y='alarm_count',
                    title="Alarm Count by Device",
                    labels={'alarm_count': 'Number of Alarms', 'device_id': 'Device ID'},
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        alarms = fetch_alarms(active_only=False)
        if alarms:
            st.subheader("Alarm Distribution by Severity")
            
            alarm_df = pd.DataFrame(alarms)
            severity_counts = alarm_df['severity'].value_counts()
            
            fig = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                title="Alarms by Severity Level",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")


def show_launch_checklist():
    st.header("Launch Preparation Checklist")
    
    devices = fetch_devices()
    
    checklist_items = []
    
    for device in devices:
        status = fetch_device_status(device['device_id'])
        if status:
            device_status = "✅" if status['operational_status'] == "NOMINAL" else "❌"
            mode_status = "✅" if status['mode'] == "ACTIVE" else "⚠️"
            
            checklist_items.append({
                "Device": device['device_id'],
                "Type": device['device_type'].replace('_', ' ').title(),
                "Operational": device_status,
                "Mode": f"{mode_status} {status['mode']}",
                "Status": status['operational_status']
            })
    
    if checklist_items:
        df = pd.DataFrame(checklist_items)
        st.dataframe(df, use_container_width=True)
        
        all_nominal = all(item['Status'] == 'NOMINAL' for item in checklist_items)
        all_active = all('ACTIVE' in item['Mode'] for item in checklist_items)
        
        st.markdown("---")
        st.subheader("Go/No-Go Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if all_nominal:
                st.success("✅ All Systems Nominal")
            else:
                st.error("❌ System Faults Detected")
        
        with col2:
            if all_active:
                st.success("✅ All Systems Active")
            else:
                st.warning("⚠️ Systems Not All Active")
        
        with col3:
            alarms = fetch_alarms(active_only=True)
            if not alarms:
                st.success("✅ No Active Alarms")
            else:
                st.error(f"❌ {len(alarms)} Active Alarms")
        
        st.markdown("---")
        
        if all_nominal and all_active and not alarms:
            st.success("🚀 **GO FOR LAUNCH**")
        else:
            st.error("🛑 **NO-GO - Resolve issues before proceeding**")


if __name__ == "__main__":
    main()
