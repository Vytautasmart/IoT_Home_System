import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np
import threading
import time
from flask import Flask
from data_processing import light_levels, distances, temperatures

# Flask App for Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Default Thresholds
lightThreshold = 200
distanceThreshold = 200
tempThreshold = 20
security_mode = False

# Dash Layout
app.layout = html.Div([
    html.H1("IoT Sensor Dashboard", style={'textAlign': 'center'}),
    
    # Security Mode Toggle
    html.Button("Security Mode: OFF", id="security-btn", n_clicks=0, style={'fontSize': '18px'}),
    
    # Alerts Section
    html.Div([
        html.H3("Alerts:"),
        html.Div(id="lighting-alert", children="Lighting Alert: OFF", style={'color': 'gray'}),
        html.Div(id="heating-alert", children="Heating Alert: OFF", style={'color': 'gray'}),
        html.Div(id="intruder-alert", children="Intruder Alarm: OFF", style={'color': 'gray'})
    ], style={'padding': '10px', 'border': '1px solid black', 'margin': '10px'}),
    
    # Threshold Sliders
    html.Div([
        html.Label("Light Threshold:"),
        dcc.Slider(id="light-threshold", min=0, max=1023, step=1, value=lightThreshold, 
                   marks={0: "0", 1023: "1023"}),
        
        html.Label("Distance Threshold (cm):"),
        dcc.Slider(id="distance-threshold", min=0, max=1000, step=1, value=distanceThreshold, 
                   marks={0: "0", 1000: "1000"}),
        
        html.Label("Temperature Threshold (°C):"),
        dcc.Slider(id="temp-threshold", min=0, max=50, step=1, value=tempThreshold, 
                   marks={0: "0", 50: "50"}),
    ], style={'padding': '10px', 'border': '1px solid black', 'margin': '10px'}),

    # Real-time Graphs
    dcc.Graph(id="light-graph"),
    dcc.Graph(id="distance-graph"),
    dcc.Graph(id="temperature-graph"),
    dcc.Graph(id="average-graph"),

    # Auto-update Interval
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0)
])


# Update Graphs
@app.callback(
    [Output("light-graph", "figure"),
     Output("distance-graph", "figure"),
     Output("temperature-graph", "figure"),
     Output("average-graph", "figure"),
     Output("lighting-alert", "children"),
     Output("heating-alert", "children"),
     Output("intruder-alert", "children"),
     Output("security-btn", "children")],
    
    [Input("interval-component", "n_intervals"),
     Input("security-btn", "n_clicks"),
     Input("light-threshold", "value"),
     Input("distance-threshold", "value"),
     Input("temp-threshold", "value")]
)
def update_dashboard(n, security_clicks, light_t, distance_t, temp_t):
    global security_mode, lightThreshold, distanceThreshold, tempThreshold

    # Update threshold values
    lightThreshold = light_t
    distanceThreshold = distance_t
    tempThreshold = temp_t
    
    # Toggle security mode
    security_mode = security_clicks % 2 == 1
    security_status = f"Security Mode: {'ON' if security_mode else 'OFF'}"

    # Create Light Graph
    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(y=list(light_levels), mode="lines", name="Light Levels", line=dict(color="orange")))
    light_fig.update_layout(title="Real-time Light Levels", xaxis_title="Time", yaxis_title="Light Level (0-1023)")

    # Create Distance Graph
    distance_fig = go.Figure()
    distance_fig.add_trace(go.Scatter(y=list(distances), mode="lines", name="Distance", line=dict(color="blue")))
    distance_fig.update_layout(title="Real-time Distance", xaxis_title="Time", yaxis_title="Distance (cm)")

    # Create Temperature Graph
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(y=list(temperatures), mode="lines", name="Temperature", line=dict(color="green")))
    temp_fig.update_layout(title="Real-time Temperature", xaxis_title="Time", yaxis_title="Temperature (°C)")

    # Compute Averages
    avg_light = np.mean(light_levels) if len(light_levels) > 0 else 0
    avg_distance = np.mean(distances) if len(distances) > 0 else 0
    avg_temp = np.mean(temperatures) if len(temperatures) > 0 else 0

    # Create Average Graph
    avg_fig = go.Figure()
    avg_fig.add_trace(go.Scatter(y=[avg_light]*len(light_levels), mode="lines", name="Avg Light", line=dict(color="orange", dash="dash")))
    avg_fig.add_trace(go.Scatter(y=[avg_distance]*len(distances), mode="lines", name="Avg Distance", line=dict(color="blue", dash="dash")))
    avg_fig.add_trace(go.Scatter(y=[avg_temp]*len(temperatures), mode="lines", name="Avg Temp", line=dict(color="green", dash="dash")))
    avg_fig.update_layout(title="Average Light, Distance & Temperature", xaxis_title="Time", yaxis_title="Average Values")

    # Update Alerts
    last_light = light_levels[-1] if len(light_levels) > 0 else 1024
    last_distance = distances[-1] if len(distances) > 0 else 1000
    last_temp = temperatures[-1] if len(temperatures) > 0 else 50

    light_alert = "Lighting Alert: ON" if last_light < lightThreshold else "Lighting Alert: OFF"
    heating_alert = "Heating Alert: ON" if last_temp < tempThreshold else "Heating Alert: OFF"
    intruder_alert = "Intruder Alarm: ON" if security_mode and last_distance < distanceThreshold else "Intruder Alarm: OFF"

    light_color = "red" if "ON" in light_alert else "gray"
    heat_color = "red" if "ON" in heating_alert else "gray"
    intruder_color = "red" if "ON" in intruder_alert else "gray"

    return (light_fig, distance_fig, temp_fig, avg_fig,
            html.Div(light_alert, style={'color': light_color}),
            html.Div(heating_alert, style={'color': heat_color}),
            html.Div(intruder_alert, style={'color': intruder_color}),
            security_status)


# Run Dash in a separate thread
def run_dash():
    app.run(debug=True, use_reloader=False)


thread = threading.Thread(target=run_dash, daemon=True)
thread.start()