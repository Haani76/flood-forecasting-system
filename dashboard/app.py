import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Flood Forecasting System", layout="wide")

# Title
st.title(" Real-Time Flood Forecasting System")
st.markdown("**Basin-scale Hydrological Model with ML Enhancement**")

# Sidebar
st.sidebar.header("Model Information")
st.sidebar.markdown("""
**Models Used:**
- GR4J (Conceptual rainfall-runoff)
- XGBoost (Machine Learning)

**Features:**
- Precipitation
- Temperature
- 7-day averages
""")

# Load data
@st.cache_data
def load_data():
    val_results = pd.read_csv('data/processed/validation_results.csv', parse_dates=['date'])
    ml_results = pd.read_csv('data/processed/ml_predictions.csv', parse_dates=['date'])
    params = pd.read_csv('data/processed/calibrated_parameters.csv')
    return val_results, ml_results, params

val_df, ml_df, params = load_data()

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("GR4J NSE", f"{params[params['parameter']=='NSE']['value'].values[0]:.3f}")

with col2:
    # Calculate ML NSE
    obs = ml_df['observed'].values
    pred = ml_df['predicted_ml'].values
    ml_nse = 1 - np.sum((obs - pred)**2) / np.sum((obs - np.mean(obs))**2)
    st.metric("ML R²", f"{ml_nse:.3f}")

with col3:
    st.metric("Basin Area", "2000 km²")

with col4:
    st.metric("Data Period", "2012-2014")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Model Comparison", "🔧 Calibrated Parameters", "📈 Time Series"])

with tab1:
    st.subheader("GR4J vs ML Model Performance")
    
    # Create comparison plot
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=("GR4J Model", "XGBoost ML Model"),
                        vertical_spacing=0.15)
    
    # GR4J
    fig.add_trace(
        go.Scatter(x=val_df['date'], y=val_df['observed'], 
                   name='Observed', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=val_df['date'], y=val_df['simulated'], 
                   name='GR4J Simulated', line=dict(color='red', width=2, dash='dash')),
        row=1, col=1
    )
    
    # ML
    fig.add_trace(
        go.Scatter(x=ml_df['date'], y=ml_df['observed'], 
                   name='Observed', line=dict(color='blue', width=2), showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=ml_df['date'], y=ml_df['predicted_ml'], 
                   name='ML Predicted', line=dict(color='green', width=2, dash='dash')),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Streamflow (mm/day)", row=1, col=1)
    fig.update_yaxes(title_text="Streamflow (mm/day)", row=2, col=1)
    
    fig.update_layout(height=700, showlegend=True)
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Calibrated GR4J Parameters")
    
    param_display = params[params['parameter'] != 'NSE'].copy()
    param_display['description'] = [
        'Production store capacity (mm)',
        'Groundwater exchange coefficient (mm)',
        'Routing store capacity (mm)',
        'Unit hydrograph time base (days)'
    ]
    
    st.dataframe(
        param_display[['parameter', 'value', 'description']],
        hide_index=True,
        use_container_width=True
    )
    
    # Parameter visualization
    fig = go.Figure(data=[
        go.Bar(x=param_display['parameter'], 
               y=param_display['value'],
               text=param_display['value'].round(2),
               textposition='auto',
               marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    ])
    
    fig.update_layout(
        title="GR4J Parameter Values",
        xaxis_title="Parameter",
        yaxis_title="Value",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Detailed Time Series Analysis")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=val_df['date'].min())
    with col2:
        end_date = st.date_input("End Date", value=val_df['date'].max())
    
    # Filter data
    mask = (val_df['date'] >= pd.to_datetime(start_date)) & (val_df['date'] <= pd.to_datetime(end_date))
    filtered_df = val_df[mask]
    
    # Plot with precipitation
    fig = make_subplots(rows=2, cols=1, 
                        row_heights=[0.7, 0.3],
                        subplot_titles=("Streamflow", "Precipitation"),
                        vertical_spacing=0.1)
    
    fig.add_trace(
        go.Scatter(x=filtered_df['date'], y=filtered_df['observed'], 
                   name='Observed', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=filtered_df['date'], y=filtered_df['simulated'], 
                   name='Simulated', line=dict(color='red', width=2, dash='dash')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=filtered_df['date'], y=filtered_df['precipitation'], 
               name='Precipitation', marker_color='lightblue'),
        row=2, col=1
    )
    
    fig.update_yaxes(title_text="Streamflow (mm/day)", row=1, col=1)
    fig.update_yaxes(title_text="Precip (mm/day)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    fig.update_layout(height=600, showlegend=True)
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Hydrological Modeling Project** | GR4J + XGBoost | 2005-2014")