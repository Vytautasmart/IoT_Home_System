import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime
from data_processing import (
    light_levels, distances, temperatures,
    get_eda_summary, get_trends,
    export_to_csv
)

app = dash.Dash(__name__)
server = app.server
boot_time = datetime.now()

app.layout = html.Div(
    style={'fontFamily': 'Segoe UI, sans-serif', 'backgroundColor': '#f8f9fa', 'padding': '20px'},
    children=[
        html.H1("IoT Sensor Dashboard", style={'textAlign': 'center', 'color': '#343a40'}),

        # Threshold Inputs and Buttons
        html.Div([
            html.Div([
                html.Label("Light Threshold:"),
                dcc.Input(id='light-threshold-input', type='number', value=200, className='input-box'),
                html.Label("Distance Threshold:"),
                dcc.Input(id='distance-threshold-input', type='number', value=200, className='input-box'),
                html.Label("Temperature Threshold:"),
                dcc.Input(id='temp-threshold-input', type='number', value=20, className='input-box'),
                html.Button("📤 Export to CSV", id='export-btn', n_clicks=0, className='export-btn'),
                html.Button("🔒 Security: OFF", id='security-toggle', n_clicks=0, className='export-btn')
            ], className='card')
        ], style={'display': 'flex', 'gap': '20px'}),

        # Status Lights
        html.Div([
            html.Div("🔴 Light OFF", id='light-status', className='status-light'),
            html.Div("🔴 Heating OFF", id='heating-status', className='status-light'),
            html.Div("🔴 Alarm OFF", id='alarm-status', className='status-light')
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),

        html.Div(id='insight-panel', style={'textAlign': 'center', 'fontSize': '16px', 'color': '#0069d9', 'marginBottom': '20px'}),

        # First row: Temperature and Light & Distance graphs side by side
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between'},
            children=[
                dcc.Graph(id='temperature-graph', style={'flex': '1', 'marginRight': '10px'}),
                dcc.Graph(id='light-distance-graph', style={'flex': '1', 'marginLeft': '10px'})
            ]
        ),

        # Second row: Four graphs in one row - Min/Max, Trend, Average (last 30 sec), and Cumulative Average
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'},
            children=[
                dcc.Graph(id='minmax-bar', style={'flex': '1', 'marginRight': '10px'}),
                dcc.Graph(id='trend-bar', style={'flex': '1', 'margin': '0 10px'}),
                dcc.Graph(id='avg-bar-graph', style={'flex': '1', 'margin': '0 10px'}),
                dcc.Graph(id='cumulative-avg-graph', style={'flex': '1', 'marginLeft': '10px'})
            ]
        ),

        html.Div(id='uptime-display', style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '14px', 'color': '#6c757d'}),

        dcc.Interval(id='interval-component', interval=1500, n_intervals=0),
        # Update the Average Sensor Values (Last 30 seconds) graph every 10 seconds
        dcc.Interval(id='interval-avg', interval=10000, n_intervals=0),
        # Update the Cumulative Average Sensor Values graph every 1 second
        dcc.Interval(id='interval-cum', interval=1000, n_intervals=0)
    ]
)

@app.callback(
    Output('temperature-graph', 'figure'),
    Output('light-distance-graph', 'figure'),
    Output('minmax-bar', 'figure'),
    Output('trend-bar', 'figure'),
    Output('uptime-display', 'children'),
    Output('insight-panel', 'children'),
    Output('light-status', 'children'),
    Output('light-status', 'style'),
    Output('heating-status', 'children'),
    Output('heating-status', 'style'),
    Output('alarm-status', 'children'),
    Output('alarm-status', 'style'),
    Input('interval-component', 'n_intervals'),
    State('light-threshold-input', 'value'),
    State('distance-threshold-input', 'value'),
    State('temp-threshold-input', 'value'),
    State('security-toggle', 'n_clicks')
)
def update_dashboard(_, light_thresh, distance_thresh, temp_thresh, security_clicks):
    if not temperatures:
        fig = go.Figure()
        fig.update_layout(title="Waiting for Data...")
        return fig, fig, fig, fig, "", "Awaiting sensor input...", "🔴 Light OFF", {'color': 'red'}, "🔴 Heating OFF", {'color': 'red'}, "🔴 Alarm OFF", {'color': 'red'}

    temp_fig = go.Figure(go.Scatter(
        y=list(temperatures),
        mode='lines+markers',
        line=dict(color='crimson')
    ))
    temp_fig.update_layout(title="Temperature (°C)", yaxis_title='°C')

    ld_fig = go.Figure()
    ld_fig.add_trace(go.Scatter(y=list(light_levels), name='Light', line=dict(color='orange')))
    ld_fig.add_trace(go.Scatter(y=list(distances), name='Distance', line=dict(color='blue')))
    ld_fig.update_layout(title="Light & Distance", yaxis_title='Sensor Value')

    eda = get_eda_summary()
    sensors = ['Temperature', 'Distance', 'Light']
    min_vals = [eda[s]['min'] for s in sensors]
    max_vals = [eda[s]['max'] for s in sensors]

    minmax_fig = go.Figure()
    minmax_fig.add_trace(go.Bar(name='Min', x=sensors, y=min_vals, marker_color='skyblue'))
    minmax_fig.add_trace(go.Bar(name='Max', x=sensors, y=max_vals, marker_color='salmon'))
    minmax_fig.update_layout(
        barmode='group',
        title='Min/Max Sensor Values',
        height=400
    )

    trends = get_trends()
    trend_map = {'↑': 1, '→': 0, '↓': -1}
    trend_colors = ['green' if v == '↑' else 'gray' if v == '→' else 'red' for v in trends.values()]
    trend_fig = go.Figure(go.Bar(
        x=list(trends.keys()),
        y=[trend_map[v] for v in trends.values()],
        text=[v for v in trends.values()],
        textposition='outside',
        marker_color=trend_colors
    ))
    trend_fig.update_layout(
        title='Sensor Trends (Smoothed)',
        yaxis=dict(title='Direction', tickvals=[-1, 0, 1], ticktext=['↓', '→', '↑']),
        height=400
    )

    current_light = light_levels[-1]
    current_dist = distances[-1]
    current_temp = temperatures[-1]

    # Light ON only if room is dark AND someone is nearby
    if current_light < light_thresh and current_dist < distance_thresh:
        light_status = "🟢 Light ON"
        light_style = {'color': 'green'}
    else:
        light_status = "🔴 Light OFF"
        light_style = {'color': 'red'}

    # Heating ON if temperature is below threshold
    heating_status = "🟢 Heating ON" if current_temp < temp_thresh else "🔴 Heating OFF"
    heating_style = {'color': 'green'} if current_temp < temp_thresh else {'color': 'red'}

    # Alarm ON if intruder detected and security is enabled
    security_on = security_clicks % 2 == 1
    if security_on and current_dist < distance_thresh:
        alarm_status = "🚨 Alarm ON"
        alarm_style = {'color': 'red'}
    else:
        alarm_status = "🟢 Alarm OFF"
        alarm_style = {'color': 'gray'}

    uptime = f"Uptime: {str(datetime.now() - boot_time).split('.')[0]}"
    return temp_fig, ld_fig, minmax_fig, trend_fig, uptime, "System running smoothly.", light_status, light_style, heating_status, heating_style, alarm_status, alarm_style

@app.callback(
    Output('avg-bar-graph', 'figure'),
    Input('interval-avg', 'n_intervals')
)
def update_avg_bar(n):
    if not temperatures:
        fig = go.Figure()
        fig.update_layout(title="Waiting for Data...")
        return fig

    # Approximate the last 30 seconds by using the last 20 samples (assuming a 1.5 sec sampling interval)
    num_samples = min(20, len(temperatures), len(light_levels), len(distances))
    avg_temp = sum(list(temperatures)[-num_samples:]) / num_samples
    avg_light = sum(list(light_levels)[-num_samples:]) / num_samples
    avg_distance = sum(list(distances)[-num_samples:]) / num_samples

    fig = go.Figure(data=[
        go.Bar(
            x=["Temperature (°C)", "Light", "Distance"],
            y=[avg_temp, avg_light, avg_distance],
            marker_color=['crimson', 'orange', 'blue']
        )
    ])
    fig.update_layout(title="Average Sensor Values (Last 30 seconds)", yaxis_title="Average Value", height=400)
    return fig

@app.callback(
    Output('cumulative-avg-graph', 'figure'),
    Input('interval-cum', 'n_intervals')
)
def update_cumulative_avg(n):
    if not temperatures:
        fig = go.Figure()
        fig.update_layout(title="Waiting for Data...")
        return fig

    # Calculate cumulative average over all available data
    avg_temp = sum(temperatures) / len(temperatures)
    avg_light = sum(light_levels) / len(light_levels)
    avg_distance = sum(distances) / len(distances)

    fig = go.Figure(data=[
        go.Bar(
            x=["Temperature (°C)", "Light", "Distance"],
            y=[avg_temp, avg_light, avg_distance],
            marker_color=['crimson', 'orange', 'blue']
        )
    ])
    fig.update_layout(title="Cumulative Average Sensor Values", yaxis_title="Average Value", height=400)
    return fig

@app.callback(
    Output('security-toggle', 'children'),
    Input('security-toggle', 'n_clicks')
)
def toggle_security(n_clicks):
    return "🔒 Security: ON" if n_clicks % 2 == 1 else "🔓 Security: OFF"

@app.callback(
    Output('export-btn', 'children'),
    Input('export-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    export_to_csv()
    return "✅ CSV Exported!"

if __name__ == "__main__":
    app.run(debug=False)
