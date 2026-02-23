import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class VizGenerator:
    """
    Generates interactive plots for meta-analysis results using Plotly.
    """

    def create_forest_plot(self, trial_data):
        """
        Creates a Forest plot for a list of trials.
        Expects a list of dicts with 'name', 'effect_size', 'lower_ci', 'upper_ci'.
        """
        if not trial_data:
            return None
            
        df = pd.DataFrame(trial_data)
        
        fig = go.Figure()

        # Add error bars for CIs
        fig.add_trace(go.Scatter(
            x=df['effect_size'],
            y=df['name'],
            mode='markers',
            error_x=dict(
                type='data',
                symmetric=False,
                array=df['upper_ci'] - df['effect_size'],
                arrayminus=df['effect_size'] - df['lower_ci']
            ),
            marker=dict(size=10, symbol='square', color='navy'),
            name='Individual Trials'
        ))

        # Add vertical line at 0 (or 1 for Odds Ratio)
        fig.add_shape(type="line", x0=0, y0=-1, x1=0, y1=len(df),
                      line=dict(color="black", width=2, dash="dash"))

        fig.update_layout(
            title="Forest Plot of Trial Outcomes",
            xaxis_title="Effect Size (e.g., Mean Difference)",
            yaxis_title="Trial",
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            height=400 + (len(df) * 20)
        )
        
        return fig

    def create_funnel_plot(self, trial_data):
        """
        Creates a Funnel plot to assess publication bias.
        Expects 'effect_size' and 'standard_error' (or 1/sqrt(enrollment)).
        """
        if not trial_data:
            return None
            
        df = pd.DataFrame(trial_data)
        
        # If precision isn't provided, estimate from enrollment
        if 'precision' not in df.columns and 'enrollment' in df.columns:
            import numpy as np
            df['precision'] = np.sqrt(df['enrollment'])

        fig = px.scatter(
            df, x="effect_size", y="precision",
            hover_name="name",
            title="Funnel Plot for Publication Bias Assessment",
            labels={"effect_size": "Effect Size", "precision": "Precision (1/SE)"}
        )
        
        fig.update_layout(template="plotly_white")
        fig.update_yaxes(autorange="reversed") # Standard funnel plot convention
        
        return fig
