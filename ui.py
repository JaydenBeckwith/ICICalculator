# ui.py — layout & styling
from dash import dcc, html

TEAL_BG = "#008080"
CARD_BG = "#ccf0e9"
BORDER = "#0b4f4a"

LABEL_STYLE = {"color": "black", "fontSize": "14px", "marginBottom": "6px", "fontWeight": 700}
TITLE_STYLE = {"color": "#ecdd0b", "fontSize": "24px", "fontWeight": 700}
SUBTLE_STYLE = {"color": "#ecdd0b", "fontSize": "16px"}

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

SCROLL_AREA = {"flex": "1 1 auto", "overflowY": "auto", "maxHeight": "120px", "paddingRight": "6px"}

def build_layout(*, cancer_options, line_options, treatment_options, metric_options, year_options):
    return html.Div(
        [
            # Header
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Stage IV Checkpoint Inhibitor Outcome Visualiser", style=TITLE_STYLE),
                            html.Div(
                                "Select cancer type, treatment setting, regimen, year, and outcome metric",
                                style=SUBTLE_STYLE,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Img(
                        src="assets/mia-logo-colour-yellow.svg",
                        style={"height": "60px", "marginLeft": "20px", "alignSelf": "center"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "14px",
                },
            ),

            # Controls
            html.Div(
                [
                    # Cancer
                    html.Div(
                        [
                            html.Div("Cancer Type", style=LABEL_STYLE),
                            html.Div(
                                dcc.Dropdown(
                                    id="cancer-dd",
                                    options=cancer_options,
                                    multi=True,
                                    value=["melanoma"],  # preselect melanoma
                                    placeholder="Select one or more cancers...",
                                    style={"width": "100%", "zIndex": 1000, "position": "relative"},
                                ),
                                style={"flex": "1 1 auto"},
                            ),
                        ],
                        style=CARD_STYLE,
                    ),

                    # Treatment setting
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

                    # Metric + Year + View
                    html.Div(
                        [
                            html.Div("Outcome Metric", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="metric-dd",
                                options=metric_options,   # ORR / PFS / OVS
                                value=metric_options[0]["value"] if metric_options else None,
                                clearable=False,
                                style={"width": "100%", "position": "relative", "zIndex": 900},
                            ),
                            html.Div(style={"height": "12px"}),
                            html.Div("Year", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="year-dd",
                                options=year_options,    # 1 / 2 / 3
                                value=year_options[0]["value"] if year_options else "1",
                                clearable=False,
                                style={"width": "100%"},
                            ),
                            html.Div(style={"height": "12px"}),
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

            # Plot (fills remaining height; no overflow past the card)
            html.Div(
                [
                    dcc.Loading(
                        dcc.Graph(
                            id="main-graph",
                            config={"displayModeBar": False, "responsive": True},
                            style={
                                "flex": "1 1 auto",
                                "height": "100%",          # stretch fully
                                "width": "100%",
                            },
                        ),
                        type="cube",
                        color=TEAL_BG,
                    )
                ],
                style={
                    **CARD_STYLE,
                    "flex": "1 1 auto",
                    "minHeight": "400px",      # increased baseline height
                    "height": "70vh",          # scale with viewport
                    "overflow": "hidden",
                    "paddingTop": "8px",       # tighter top padding
                    "paddingBottom": "12px",   # room for legend if at bottom
                },
            ),
            # Modal
            dcc.Store(id="note-modal-open", data=False),
            html.Div(
                id="note-modal",
                children=html.Div(
                    [
                        html.Div("Heads up", style={"fontWeight": 800, "fontSize": "18px", "marginBottom": "8px"}),
                        html.P(
                            "Must select at least 1 option in each control (cancers, treatment setting, regimens, year, and outcome metric).",
                            style={"margin": 0, "lineHeight": "1.4"},
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
                                "fontWeight": 600,
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
                style={
                    "display": "none",
                    "position": "fixed",
                    "inset": 0,
                    "backgroundColor": "rgba(0,0,0,0.35)",
                    "zIndex": 9999,
                    "alignItems": "center",
                    "justifyContent": "center",
                },
            ),
        ],
        style={
            "fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'",
            "backgroundColor": TEAL_BG,
            "height": "100vh",      # full viewport height
            "padding": "20px",
            "display": "flex",      # flex column
            "flexDirection": "column",
            "gap": "12px",
        },
    )

