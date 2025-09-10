# backend - helpers + callbacks

from typing import List, Dict
import pandas as pd
import plotly.express as px
from dash import Input, Output, State

def _filter_df(df: pd.DataFrame, cancers: List[str], lines: List[str]) -> pd.DataFrame:

    if cancers:
        df = df[df["cancer"].astype(str).isin(cancers)]
    if lines:
        df = df[df["line"].astype(str).isin([str(x) for x in lines])]

    return df.copy()

def _resolve_metric_suffix(base_metric: str, year: str, year_to_months: Dict[str, str]) -> str:
    """
    Convert (ORR|PFS|OVS, selected year) -> column suffix used in the sheet.
    ORR ignores year.
    """
    b = (base_metric or "").upper()
    if b == "ORR":
        return "ORR"
    if b in {"PFS", "OVS"}:
        months = year_to_months.get(str(year))
        if not months:
            return ""  # will yield no data
        return f"{b}{months}" 
    
    return ""

def _melt_for_plot(df: pd.DataFrame, metric_suffix: str, reg_prefixes: List[str],treatment_prefix_map: Dict[str, str], line_labels: Dict[str, str], ) -> pd.DataFrame:
    """
    Reshape a wide-format df into a long format suitable for plotting treatment regimens.

    This function selects columns from the input DataFrame whose names are constructed It then melts these columns 
    into a long format, maps regimen prefixes to human-readable treatment names, 
    ensures numeric values for the selected metric, and applies custom line labels.

    Args:
        df (pd.DataFrame): Input DataFrame containing cancer type, line, and regimen metrics.
        metric_suffix (str): Suffix used to identify metric columns (e.g., "_ORR").
        reg_prefixes (List[str]): List of column prefixes corresponding to different regimens.
        treatment_prefix_map (Dict[str, str]): Mapping from regimen column prefix 
            (first character of the column name) to treatment name.
        line_labels (Dict[str, str]): Mapping from line values to human-readable labels.

    Returns:
        pd.DataFrame: A melted DataFrame with the following columns:
            - cancer: Cancer type (from input).
            - line: Line of therapy (from input).
            - regimen: Mapped regimen name.
            - metric_suffix: Numeric metric value (e.g., ORR, DOR).
            - line_label: Human-readable label for line of therapy.

        If no matching regimen columns are found, returns an empty df
        with the expected column names.
    """

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
            Input("metric-dd", "value"),
            Input("year-dd", "value"),
            Input("view-radio", "value"),
        ],
    )
    def update_graph(cancer_sel, line_sel, metric_base, year_sel, view_sel):
   
        if not cancer_sel or not line_sel or not metric_base or not year_sel:
            fig = px.bar(title="Please make selections in all controls to view results.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        suffix = _resolve_metric_suffix(metric_base, year_sel, YEAR_TO_MONTHS)
        if not suffix:
            fig = px.bar(title="No data available for this metric/year.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        dff = _filter_df(df, cancers=cancer_sel, lines=line_sel)

        # Dynamically discover regimen prefixes that exist for this suffix
        reg_prefixes = sorted({
            col[:-len(suffix)]
            for col in dff.columns
            if col.endswith(suffix) and len(col) > len(suffix)
        })

        long = _melt_for_plot(
            dff,
            metric_suffix=suffix,
            reg_prefixes=reg_prefixes,
            treatment_prefix_map=TREATMENT_PREFIX_MAP,
            line_labels=LINE_LABELS,
        )

        if long.empty:
            fig = px.bar(title="No data available for the current selections.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        # Build figure + facet context
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
                title=f"{metric_base} ({'Year ' + str(year_sel) if metric_base != 'ORR' else 'Overall'})",
            )
            facet_prefix = "cancer="
            facet_count = long["cancer"].nunique() or 1
            left_labels  = [LINE_LABELS.get("1", "1"), LINE_LABELS.get("2+", "2+")]
            right_labels = sorted(long["cancer"].astype(str).unique().tolist())
        else:
            fig = px.bar(
                long,
                y="cancer",
                x=suffix,
                color="regimen",
                facet_row="line_label",
                color_discrete_map=COLOR_MAP,
                orientation="h",
                title=f"{metric_base} ({'Year ' + str(year_sel) if metric_base != 'ORR' else 'Overall'})",
            )
            facet_prefix = "line_label="
            facet_count = long["line_label"].nunique() or 1
            left_labels  = sorted(long["cancer"].astype(str).unique().tolist())
            right_labels = [LINE_LABELS.get("1", "1"), LINE_LABELS.get("2+", "2+")]

        # Core styling + legend at bottom
        fig.update_layout(
            barmode="stack",
            barnorm="percent",
            autosize=True,
            paper_bgcolor="#ccf0e9",
            plot_bgcolor="#ccf0e9",
            legend_title_text="Regimen",
            font_color="black",
            title_font_color="black",
            template=None,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,          # below plot
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        fig.update_traces(marker_line_width=0)
        fig.update_xaxes(title=None, rangemode="tozero", range=[0, 100], ticksuffix="%", color="black")
        fig.update_yaxes(title=None, color="black", automargin=True)

        # Make facet row labels horizontal on the right edge
        for ann in list(fig.layout.annotations or []):
            txt = ann.text or ""
            if facet_prefix in txt:
                ann.text = txt.split("=", 1)[1]  # strip "cancer=" / "line_label="
                ann.textangle = 0                # horizontal
                ann.font.color = "black"
                ann.xref = "paper"
                ann.x = 1.0                      # right edge of plotting area
                ann.xanchor = "left"
                ann.align = "left"

        # Dynamic margins: left for y ticks, right for (now horizontal) facet labels
        max_left_len = max((len(str(s)) for s in left_labels), default=1)
        left_margin = max(90, int(7.5 * max_left_len))

        max_right_len = max((len(str(s)) for s in right_labels), default=1)
        right_margin = max(120, int(9.0 * max_right_len))

        bottom_margin = 140  # room for bottom legend
        fig.update_layout(margin=dict(t=130, r=right_margin, b=bottom_margin, l=left_margin))

        # Dynamic height per facet row — prevents crowding as facets increase
        BASE_H = 320
        ROW_H  = 160
        MIN_H  = 550
        fig.update_layout(height=max(MIN_H, BASE_H + ROW_H * facet_count))

        return fig


    # Modal (unchanged except no regimen input)
    @app.callback(
        [Output("note-modal", "style"), Output("note-modal-open", "data")],
        [
            Input("cancer-dd", "value"),
            Input("line-ck", "value"),
            Input("metric-dd", "value"),
            Input("year-dd", "value"),
            Input("close-note-modal", "n_clicks"),
        ],
        [State("note-modal-open", "data")],
    )
    def toggle_note_modal(cancers, lines, metric, year, close_clicks, is_open):
        from dash import callback_context
        missing = not cancers or not lines or not metric or not year
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
