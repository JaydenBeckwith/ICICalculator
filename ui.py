# ui.py — layout & styling
from dash import dcc, html

# --- Colours ---
TEAL_BG = "#008080"   # page bg
CARD_BG = "#ccf0e9"   # card bg
BORDER = "#0b4f4a"

# --- Typography ---
LABEL_STYLE = {"color": "black", "fontSize": "14px", "marginBottom": "6px", "fontWeight": 700}  # bold labels
TITLE_STYLE = {"color": "#ecdd0b", "fontSize": "22px", "fontWeight": 700}
SUBTLE_STYLE = {"color": "#ecdd0b", "fontSize": "13px"}

# --- Layout ---
CONTROL_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
    "gap": "14px",
    "alignItems": "stretch",
}

CARD_STYLE = {
    "backgroundColor": CARD_BG,
    "border": f"1px solid {BORDER}",
    "borderRadius": "16px",
    "padding": "16px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "display": "flex",
    "flexDirection": "column",
    "minHeight": "180px",
}

# Scrollable inner area
SCROLL_AREA = {
    "flex": "1 1 auto",
    "overflowY": "auto",
    "maxHeight": "120px",
    "paddingRight": "6px",
}

def build_layout(*, cancer_options, line_options, treatment_options, metric_options):
    return html.Div(
        [
            # Title
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Stage IV Checkpoint Inhibitor Outcome Visualiser", style=TITLE_STYLE),
                            html.Div("Select cancer type, treatment setting, regimen, and outcome metric", style=SUBTLE_STYLE),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Img(
                        src="assets/mia-logo-colour-yellow.svg",
                        style={
                            "height": "60px",   # adjust size as needed
                            "marginLeft": "20px",
                            "alignSelf": "center",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "14px",
                },
            ),

            # Controls row
            html.Div(
                [
                    # Cancer(s)
                    html.Div(
                        [
                            html.Div("Cancer Type", style=LABEL_STYLE),
                            html.Div(
                                dcc.Dropdown(
                                    id="cancer-dd",
                                    options=cancer_options,
                                    multi=True,
                                    placeholder="Select one or more cancers...",
                                    style={"width": "100%", "zIndex": 1000, "position": "relative"},
                                ),
                                style={"flex": "1 1 auto"},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),

                    # Line of therapy
                    html.Div(
                        [
                            html.Div("Treatment Setting", style=LABEL_STYLE),
                            html.Div(
                                dcc.Checklist(
                                    id="line-ck",
                                    options=line_options,
                                    value=[opt["value"] for opt in line_options],
                                    inline=False,
                                    inputStyle={"marginRight": "6px"},
                                    labelStyle={"display": "block", "marginBottom": "6px", "color": "black"},
                                ),
                                style=SCROLL_AREA,
                            ),
                        ],
                        style=CARD_STYLE,
                    ),

                    # Regimens
                    html.Div(
                        [
                            html.Div("Therapy Regimen(s)", style=LABEL_STYLE),
                            html.Div(
                                dcc.Checklist(
                                    id="treat-ck",
                                    options=treatment_options,
                                    value=[opt["value"] for opt in treatment_options],
                                    inline=False,
                                    inputStyle={"marginRight": "6px"},
                                    labelStyle={"display": "block", "marginBottom": "6px", "color": "black"},
                                ),
                                style=SCROLL_AREA,
                            ),
                        ],
                        style=CARD_STYLE,
                    ),

                    # Metric + View (merged card)
                    html.Div(
                        [
                            html.Div("Outcome Metric", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="metric-dd",
                                options=metric_options,
                                value=metric_options[0]["value"] if metric_options else None,
                                clearable=False,
                                style={"width": "100%", "position": "relative", "zIndex": 900},
                            ),
                            html.Div(style={"height": "20px"}),  # spacing
                            html.Div("View", style=LABEL_STYLE),
                            dcc.RadioItems(
                                id="view-radio",
                                options=[
                                    {"label": "By treatment setting", "value": "by_line"},
                                    {"label": "By cancer type", "value": "by_cancer"},
                                ],
                                value="by_line",
                                inline=True,
                                labelStyle={"marginRight": "16px", "color": "black"},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                ],
                style=CONTROL_STYLE,
            ),

            html.Div(style={"height": "12px"}),

            # Plot
            html.Div(
                [dcc.Loading(dcc.Graph(id="main-graph", config={"displayModeBar": False}), type="cube", color="black")],
                style={**CARD_STYLE, "minHeight": "420px"},
            ),

            html.Div(style={"height": "8px"}),
            dcc.Store(id="note-modal-open", data=False),

        # Modal overlay (hidden by default; style controlled by callback)
        html.Div(
            id="note-modal",
            children=html.Div(
                [
                    html.Div("Heads up", style={"fontWeight": 800, "fontSize": "18px", "marginBottom": "8px"}),
                    html.P(
                        "Must select at least 1 option in each control (cancers, treatment setting, regimens, and outcome metric).",
                        style={"margin": 0, "lineHeight": "1.4"}
                    ),
                    html.Button(
                        "OK, got it",
                        id="close-note-modal",
                        n_clicks=0,
                        style={
                            "marginTop": "14px",
                            "padding": "8px 14px",
                            "borderRadius": "10px",
                            "border": "1px solid #0b4f4a",
                            "background": "#ccf0e9",
                            "cursor": "pointer",
                            "fontWeight": 600
                        },
                    ),
                ],
                style={
                    "width": "min(520px, 92vw)",
                    "background": "#e6faf5",
                    "border": "1px solid #0b4f4a",
                    "borderRadius": "16px",
                    "padding": "16px 18px",
                    "boxShadow": "0 10px 30px rgba(0,0,0,0.25)",
                },
            ),
            style={  # default hidden; backend toggles 'display'
                "display": "none",
                "position": "fixed",
                "inset": 0,
                "backgroundColor": "rgba(0,0,0,0.35)",
                "zIndex": 9999,
                "display": "none",
                "alignItems": "center",
                "justifyContent": "center",
            },
        ),
        ],
        style={
            "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'",
            "backgroundColor": TEAL_BG,
            "minHeight": "100vh",
            "padding": "20px",
        },
    )
