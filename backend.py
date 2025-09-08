# backend.py — helpers + callbacks
from typing import List, Dict
import pandas as pd
import plotly.express as px
from dash import Input, Output

def _filter_df(df: pd.DataFrame, cancers: List[str], lines: List[str]) -> pd.DataFrame:
    if cancers:
        df = df[df["cancer"].astype(str).isin(cancers)]
    if lines:
        df = df[df["line"].astype(str).isin([str(x) for x in lines])]
    return df.copy()

def _melt_for_plot(
    df: pd.DataFrame,
    metric: str,
    reg_prefixes: List[str],
    treatment_prefix_map: Dict[str, str],
    line_labels: Dict[str, str],
) -> pd.DataFrame:
    cols = [f"{p}{metric}" for p in reg_prefixes if f"{p}{metric}" in df.columns]
    if not cols:
        return pd.DataFrame(columns=["cancer", "line", "regimen", metric])

    tmp = df[["cancer", "line", *cols]].copy()
    tmp = tmp.melt(
        id_vars=["cancer", "line"],
        value_vars=cols,
        var_name="regimen_col",
        value_name=metric,
    )
    tmp["regimen"] = tmp["regimen_col"].str[0].map(treatment_prefix_map)
    tmp.drop(columns=["regimen_col"], inplace=True)

    # ensure numeric + drop NA so bars render
    tmp[metric] = pd.to_numeric(tmp[metric], errors="coerce")
    tmp.dropna(subset=[metric], inplace=True)

    tmp["line_label"] = tmp["line"].astype(str).map(line_labels).fillna(tmp["line"].astype(str))
    return tmp

def register_callbacks(app, df: pd.DataFrame, config: Dict):
    LINE_LABELS = config["LINE_LABELS"]
    TREATMENT_PREFIX_MAP = config["TREATMENT_PREFIX_MAP"]
    COLOR_MAP = config["COLOR_MAP"]

    @app.callback(
        Output("main-graph", "figure"),
        [
            Input("cancer-dd", "value"),
            Input("line-ck", "value"),
            Input("treat-ck", "value"),
            Input("metric-dd", "value"),
            Input("view-radio", "value"),
        ],
    )
    def update_graph(cancer_sel, line_sel, treat_sel, metric_sel, view_sel):
        # Guard conditions
        if not cancer_sel or not line_sel or not treat_sel or not metric_sel:
            fig = px.bar(title="Please make selections in all controls to view results.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        dff = _filter_df(df, cancers=cancer_sel, lines=line_sel)
        long = _melt_for_plot(
            dff,
            metric=metric_sel,
            reg_prefixes=[str(x) for x in treat_sel],
            treatment_prefix_map=TREATMENT_PREFIX_MAP,
            line_labels=LINE_LABELS,
        )

        if long.empty:
            fig = px.bar(title="No data available for the current selections.")
            fig.update_layout(paper_bgcolor="#ccf0e9", plot_bgcolor="#ccf0e9", font_color="black", template=None)
            return fig

        # Horizontal bars + facets
        if view_sel == "by_line":
            fig = px.bar(
                long,
                y="line_label",         # flipped
                x=metric_sel,           # flipped
                color="regimen",
                facet_row="cancer",     # row facets instead of columns
                category_orders={"line_label": [LINE_LABELS.get("1", "1"), LINE_LABELS.get("2+", "2+")]},
                color_discrete_map=COLOR_MAP,
                orientation="h",
                title=f"{metric_sel}",
            )
            facet_prefix_to_strip = "cancer="
        else:
            fig = px.bar(
                long,
                y="cancer",
                x=metric_sel,
                color="regimen",
                facet_row="line_label",
                color_discrete_map=COLOR_MAP,
                orientation="h",
                title=f"{metric_sel}",
            )
            facet_prefix_to_strip = "line_label="

        # Normalized stacked percent (compatible with older Plotly via update_layout)
        fig.update_layout(barmode="stack", barnorm="percent")

        # Base styling + legend at bottom
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            paper_bgcolor="#ccf0e9",
            plot_bgcolor="#ccf0e9",
            legend_title_text="Regimen",
            margin=dict(t=60, r=120, b=80, l=80),  # start with decent margins
            font_color="black",
            title_font_color="black",
            template=None,  # avoid dark template gridlines on light bg
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
            ),
        )

        # Axes (no bottom "ORR" etc.)
        fig.update_xaxes(title=None, rangemode="tozero", range=[0, 100], ticksuffix="%", color="black")
        fig.update_yaxes(title=None, color="black", automargin=True)

        # --- Clean & protect facet labels on the right ---
        labels = []
        for a in list(fig.layout.annotations or []):
            txt = a.text or ""
            if facet_prefix_to_strip in txt:
                label = txt.split("=", 1)[1]          # remove 'cancer=' or 'line_label='
                labels.append(label)
                a.text = label
                a.font.color = "black"
                a.textangle = 0
                a.xref = "paper"                      # anchor to the figure's right edge
                a.x = 1.0
                a.xanchor = "left"
                a.align = "left"

        # Increase right margin dynamically based on longest label length (~8 px per char)
        if labels:
            max_len = max(len(s) for s in labels)
            extra_right = 8 * max_len
            current = fig.layout.margin.r or 0
            fig.update_layout(margin=dict(
                t=fig.layout.margin.t,
                b=fig.layout.margin.b,
                l=fig.layout.margin.l,
                r=max(current, 100 + extra_right),
            ))

        return fig

