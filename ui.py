# ui.py — layout & styling
from dash import dcc, html

LABEL_STYLE = {"color": "#d1d5db", "fontSize": "14px", "marginBottom": "6px"}
TITLE_STYLE = {"color": "#e5e7eb", "fontSize": "22px", "fontWeight": 700}
SUBTLE_STYLE = {"color": "#9ca3af", "fontSize": "13px"}
CONTROL_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(4, minmax(220px, 1fr))",
    "gap": "12px",
    "alignItems": "end",
}
CARD_STYLE = {
    "backgroundColor": "#111318",
    "border": "1px solid #1f2630",
    "borderRadius": "14px",
    "padding": "16px",
}

def build_layout(*, cancer_options, line_options, treatment_options, metric_options):
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Stage IV Checkpoint Inhibitor Outcome Visualiser", style=TITLE_STYLE),
                    html.Div("Select cancers, treatment setting, regimen, and outcome metric.", style=SUBTLE_STYLE),
                ],
                style={"marginBottom": "14px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Cancer(s)", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="cancer-dd",
                                options=cancer_options,
                                multi=True,
                                placeholder="Select one or more cancers...",
                                style={"width": "100%"},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div("Treatment setting (line)", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="line-dd",
                                options=line_options,
                                multi=True,
                                placeholder="Select line(s) of therapy...",
                                style={"width": "100%"},
                            ),
                            html.Div(
                                "Note: 1 = No prior treatment; 2+ = At least one prior treatment",
                                style={"marginTop": "6px", **SUBTLE_STYLE},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div("Regimen(s)", style=LABEL_STYLE),
                            dcc.Checklist(
                                id="treat-ck",
                                options=treatment_options,
                                value=[opt["value"] for opt in treatment_options],
                                inline=False,
                                inputStyle={"marginRight": "6px"},
                                labelStyle={"display": "block", "marginBottom": "4px", "color": "#e5e7eb"},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div("Outcome metric", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="metric-dd",
                                options=metric_options,
                                value=metric_options[0]["value"] if metric_options else None,
                                clearable=False,
                                style={"width": "100%"},
                            ),
                            html.Div(
                                "Tip: Add more metrics in the data file to unlock more views.",
                                style={"marginTop": "6px", **SUBTLE_STYLE},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                ],
                style=CONTROL_STYLE,
            ),
            html.Div(style={"height": "14px"}),
            html.Div(
                [
                    html.Div("View", style=LABEL_STYLE),
                    dcc.RadioItems(
                        id="view-radio",
                        options=[
                            {"label": "By treatment setting", "value": "by_line"},
                            {"label": "By cancer", "value": "by_cancer"},
                        ],
                        value="by_line",
                        inline=True,
                        labelStyle={"marginRight": "16px", "color": "#e5e7eb"},
                    ),
                ],
                style=CARD_STYLE,
            ),
            html.Div(style={"height": "14px"}),
            html.Div(
                [dcc.Loading(dcc.Graph(id="main-graph", config={"displayModeBar": False}), type="cube", color="#9ca3af")],
                style=CARD_STYLE,
            ),
            html.Div(style={"height": "8px"}),
            html.Div("Note: Must select at least 1 option in each control.", style=SUBTLE_STYLE),
        ],
        style={
            "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'",
            "backgroundColor": "#0b0f16",
            "minHeight": "100vh",
            "padding": "20px",
        },
    )
