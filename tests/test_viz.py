import pytest
import pandas as pd
from src.viz import VizGenerator
import plotly.graph_objects as go

def test_create_forest_plot():
    viz = VizGenerator()
    data = [
        {"name": "T1", "effect_size": 0.1, "lower_ci": 0.05, "upper_ci": 0.15},
        {"name": "T2", "effect_size": -0.2, "lower_ci": -0.3, "upper_ci": -0.1},
    ]
    
    fig = viz.create_forest_plot(data)
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Forest Plot of Trial Outcomes"

def test_create_funnel_plot():
    viz = VizGenerator()
    data = [
        {"name": "T1", "effect_size": 0.1, "enrollment": 100},
        {"name": "T2", "effect_size": -0.2, "enrollment": 400},
    ]
    
    fig = viz.create_funnel_plot(data)
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Funnel Plot for Publication Bias Assessment"

def test_viz_empty_data():
    viz = VizGenerator()
    assert viz.create_forest_plot([]) is None
    assert viz.create_funnel_plot([]) is None
