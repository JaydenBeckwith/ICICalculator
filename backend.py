# backend.py — helpers + callbacks
# backend.py — helpers + callbacks
from typing import List, Dict
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, callback_context

def _filter_df(df: pd.DataFrame, cancers: List[str], lines: List[str]) -> pd.DataFrame:
    if cancers:
        df = df[df["cancer"].astype(str).isin(cancers)]
    if lines:
        df = df[df["line"].astype(str).isin([str(x) for x in lines])]
    return df.copy()

def _resolve_metric_suffix(base_metric: str, year: str, year_to_months: Dict[str, str]) -> str:
    """
    Convert (ORR|PFS|OVS, selected_year) -> column suffix used in the sheet.
    ORR ignores year.
    """
    b = (base_metric or "").upper()
    if b == "ORR":
        return "ORR"
    if b in {"PFS", "OVS"}:
        months = year_to_months.get(str(year))
        if not months:
            return ""  # will yield no data
        return f"{b}{months}"  # e.g., PFS12, OVS24
    return ""

def _melt_for_plot(
    df: pd.DataFrame,
    metric_suffix: str,
    reg_prefixes: List[str],
    treatment_prefix_map: Dict[str, str],
    line_labels: Dict[str, str],
) -> pd.DataFrame:
    cols = [f"{p}{metric_suffix}" for p in reg_prefixes if f"{p}{metric_suffix}" in df.columns]
    if not cols:
        return pd.DataFrame(columns=["cancer", "line", "regimen", metric_suffix])

    tmp = df[["cancer", "line", *cols]].copy()
    tmp = tmp.melt(id_vars=["cancer", "line"], value_vars=cols,
                   var_name="regimen_col", value_name=metric_suffix)
    tmp["regimen"] = tmp["regimen_col"].str[0].map(treatment_prefix_map)
    tmp.drop(columns=["regimen_col"], inplace=True)

    tmp[metric_suffix] = pd.to_numeric(tmp[metric_suffix], errors="coerce")
    tmp.dropna(subset=[metric_suffix], inplace=True)

    tmp["line_label"] = tmp["line"].astype(str).map(line_labels).fillna(tmp["line"].astype(str))
    return tmp

def register_callbacks(app, df: pd.DataFrame, config: Dict):
    LINE_LABELS = config["LINE_LABELS"]
    TREATMENT_PREFIX_MAP = config["TREATMENT_PREFIX_MAP"]
    COLOR_MAP = config["COLOR_MAP"]
    YEAR_TO_MONTHS = config["YEAR_TO_MONTHS"]

    @app.callback(
        Output("main-graph", "figure"),
        [
            Input("cancer-dd", "value"),
            Input("line-ck", "value"),
            Input("treat-ck", "value"),
            Input("metric-dd", "value"),   # ORR / PFS / OVS
            Input("year-dd", "value"),     # 1 / 2 / 3
            Input("view-radio", "value"),
        ],
    )
    def update_graph(cancer_sel, line_sel, treat_sel, metric_base, year_sel, view_sel):
        if not cancer_sel or not line_sel or not treat_sel or not metric_base or not year_sel:
            fig = px.bar(title="Please make selections in all controls to view results.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        suffix = _resolve_metric_suffix(metric_base, year_sel, YEAR_TO_MONTHS)
        if not suffix:
            fig = px.bar(title="No data available for this metric/year.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        dff = _filter_df(df, cancers=cancer_sel, lines=line_sel)
        long = _melt_for_plot(
            dff,
            metric_suffix=suffix,
            reg_prefixes=[str(x) for x in treat_sel],
            treatment_prefix_map=TREATMENT_PREFIX_MAP,
            line_labels=LINE_LABELS,
        )

        if long.empty:
            fig = px.bar(title="No data available for the current selections.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        # Horizontal normalized stacked bars by regimen
        if view_sel == "by_line":
            fig = px.bar(
                long,
                y="line_label",
                x=suffix,
                color="regimen",
                facet_row="cancer",
                category_orders={"line_label": [LINE_LABELS.get("1", "1"), LINE_LABELS.get("2+", "2+")]},
                color_discrete_map=COLOR_MAP,
                orientation="h",
                title=f"{metric_base} ({'Year ' + str(year_sel) if metric_base!='ORR' else 'Overall'})",
            )
            facet_prefix_to_strip = "cancer="
        else:
            fig = px.bar(
                long,
                y="cancer",
                x=suffix,
                color="regimen",
                facet_row="line_label",
                color_discrete_map=COLOR_MAP,
                orientation="h",
                title=f"{metric_base} ({'Year ' + str(year_sel) if metric_base!='ORR' else 'Overall'})",
            )
            facet_prefix_to_strip = "line_label="

        fig.update_layout(barmode="stack", barnorm="percent")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            paper_bgcolor="#ccf0e9",
            plot_bgcolor="#ccf0e9",
            legend_title_text="Regimen",
            margin=dict(t=60, r=120, b=80, l=80),
            font_color="black",
            title_font_color="black",
            template=None,
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        )
        fig.update_xaxes(title=None, rangemode="tozero", range=[0, 100], ticksuffix="%", color="black")
        fig.update_yaxes(title=None, color="black", automargin=True)

        # Clean facet labels on right
        labels = []
        for a in list(fig.layout.annotations or []):
            txt = a.text or ""
            if facet_prefix_to_strip in txt:
                label = txt.split("=", 1)[1]
                labels.append(label)
                a.text = label
                a.font.color = "black"
                a.textangle = 0
                a.xref = "paper"
                a.x = 1.0
                a.xanchor = "left"
                a.align = "left"
        if labels:
            max_len = max(len(s) for s in labels)
            extra_right = 8 * max_len
            current = fig.layout.margin.r or 0
            fig.update_layout(margin=dict(
                t=fig.layout.margin.t, b=fig.layout.margin.b, l=fig.layout.margin.l,
                r=max(current, 100 + extra_right),
            ))
        return fig

    # Modal controller (include year-dd)
    @app.callback(
        [Output("note-modal", "style"), Output("note-modal-open", "data")],
        [
            Input("cancer-dd", "value"),
            Input("line-ck", "value"),
            Input("treat-ck", "value"),
            Input("metric-dd", "value"),
            Input("year-dd", "value"),
            Input("close-note-modal", "n_clicks"),
        ],
        [State("note-modal-open", "data")],
    )
    def toggle_note_modal(cancers, lines, regimens, metric, year, close_clicks, is_open):
        missing = not cancers or not lines or not regimens or not metric or not year
        trig = (callback_context.triggered[0]["prop_id"] if callback_context.triggered else "")
        open_now = False if "close-note-modal" in trig else bool(missing)
        overlay_style = {
            "position": "fixed",
            "inset": 0,
            "backgroundColor": "rgba(0,0,0,0.35)",
            "zIndex": 9999,
            "alignItems": "center",
            "justifyContent": "center",
            "display": "flex" if open_now else "none",
        }
        return overlay_style, open_now
