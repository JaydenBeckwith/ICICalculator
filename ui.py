# ui.py — layout & styling
from dash import dcc, html

# --- Colours ---
TEAL_BG = "#008080"   # page bg
CARD_BG = "#ccf0e9"   # card bg
BORDER = "#0b4f4a"

# --- Typography ---
LABEL_STYLE = {"color": "black", "fontSize": "14px", "marginBottom": "6px"}
TITLE_STYLE = {"color": "#ecdd0b", "fontSize": "22px", "fontWeight": 700}
SUBTLE_STYLE = {"color": "#ecdd0b", "fontSize": "13px"}

# --- Layout ---
CONTROL_STYLE = {
    "display": "grid",
    # Responsive: auto-fit wraps to the next line as screen narrows
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
    # Fix card height so layout doesn't jump when chips wrap
    "minHeight": "180px",
}

# A scrollable content area inside each card
SCROLL_AREA = {
    "flex": "1 1 auto",
    "overflowY": "auto",
    "maxHeight": "120px",  # adjust to taste
    "paddingRight": "6px",
}

def build_layout(*, cancer_options, line_options, treatment_options, metric_options):
    return html.Div(
        [
            # Title
            html.Div(
                [
                    html.Div("Stage IV Checkpoint Inhibitor Outcome Visualiser", style=TITLE_STYLE),
                    html.Div("Select cancers, treatment setting, regimen, and outcome metric.", style=SUBTLE_STYLE),
                ],
                style={"marginBottom": "14px"},
            ),

            # Controls row
            html.Div(
                [
                    # Cancer(s)
                    html.Div(
                        [
                            html.Div("Cancer(s)", style=LABEL_STYLE),
                            html.Div(
                                dcc.Dropdown(
                                    id="cancer-dd",
                                    options=cancer_options,
                                    multi=True,
                                    placeholder="Select one or more cancers...",
                                    style={"width": "100%"},
                                ),
                                style=SCROLL_AREA,  # scroll inside, not the whole page
                            ),
                        ],
                        style=CARD_STYLE,
                    ),

                    # Line of therapy
                    html.Div(
                        [
                            html.Div("Treatment setting (line)", style=LABEL_STYLE),
                            html.Div(
                                dcc.Checklist(
                                    id="line-ck",
                                    options=line_options,                    # [{"label": "...", "value": "1"}, {"label": "...", "value": "2+"}]
                                    value=[opt["value"] for opt in line_options],  # preselect all
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
                            html.Div("Regimen(s)", style=LABEL_STYLE),
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

                    # Metric
                    html.Div(
                        [
                            html.Div("Outcome metric", style=LABEL_STYLE),
                            html.Div(
                                dcc.Dropdown(
                                    id="metric-dd",
                                    options=metric_options,
                                    value=metric_options[0]["value"] if metric_options else None,
                                    clearable=False,
                                    style={"width": "100%"},
                                ),
                                style=SCROLL_AREA,
                            ),
                        ],
                        style=CARD_STYLE,
                    ),
                ],
                style=CONTROL_STYLE,
            ),

            html.Div(style={"height": "12px"}),

            # View toggle
            html.Div(
                [
                    html.Div("View", style=LABEL_STYLE),
                    html.Div(
                        dcc.RadioItems(
                            id="view-radio",
                            options=[
                                {"label": "By treatment setting", "value": "by_line"},
                                {"label": "By cancer", "value": "by_cancer"},
                            ],
                            value="by_line",
                            inline=True,
                            labelStyle={"marginRight": "16px", "color": "black"},
                        ),
                        style={"marginTop": "2px"},
                    ),
                ],
                style={**CARD_STYLE, "minHeight": "auto"},
            ),

            html.Div(style={"height": "12px"}),

            # Plot
            html.Div(
                [dcc.Loading(dcc.Graph(id="main-graph", config={"displayModeBar": False}), type="cube", color="black")],
                style={**CARD_STYLE, "minHeight": "420px"},
            ),

            html.Div(style={"height": "8px"}),
            html.Div("Note: Must select at least 1 option in each control.", style=SUBTLE_STYLE),
        ],
        style={
            "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'",
            "backgroundColor": TEAL_BG,
            "minHeight": "100vh",
            "padding": "20px",
        },
    )
