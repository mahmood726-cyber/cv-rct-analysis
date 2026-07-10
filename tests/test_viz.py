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

def test_funnel_plot_yaxis_reversed():
    # Regression (F1): SE axis must be reversed so precise/large studies (low SE)
    # sit at the top, per the standard funnel convention (metafor/RevMan).
    viz = VizGenerator()
    data = [
        {"name": "A", "effect_size": 0.1, "enrollment": 100},
        {"name": "B", "effect_size": 0.1, "enrollment": 10000},
    ]
    fig = viz.create_funnel_plot(data)
    assert fig.layout.yaxis.autorange == "reversed"

def test_funnel_plot_standard_error_branch():
    # Regression (F2): explicit standard_error column path.
    viz = VizGenerator()
    data = [{"name": "A", "effect_size": 0.1, "standard_error": 0.2}]
    fig = viz.create_funnel_plot(data)
    assert isinstance(fig, go.Figure)
    assert fig.layout.yaxis.title.text == "Standard Error"

def test_funnel_plot_no_se_or_enrollment_returns_none():
    # Regression (F2): neither standard_error nor enrollment -> None guard.
    viz = VizGenerator()
    assert viz.create_funnel_plot([{"name": "A", "effect_size": 0.1}]) is None

def test_viz_empty_data():
    viz = VizGenerator()
    assert viz.create_forest_plot([]) is None
    assert viz.create_funnel_plot([]) is None
