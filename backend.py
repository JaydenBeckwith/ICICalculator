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
            Input("line-dd", "value"),
            Input("treat-ck", "value"),
            Input("metric-dd", "value"),
            Input("view-radio", "value"),
        ],
    )
    def update_graph(cancer_sel, line_sel, treat_sel, metric_sel, view_sel):
        # Guard conditions
        if not cancer_sel or not line_sel or not treat_sel or not metric_sel:
            fig = px.bar(title="Please make selections in all controls to view results.")
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0b0f16", plot_bgcolor="#0b0f16")
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
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0b0f16", plot_bgcolor="#0b0f16")
            return fig

        # Normalized stacked bars (percent) — set via update_layout for older Plotly
        if view_sel == "by_line":
            fig = px.bar(
                long,
                x="line_label",
                y=metric_sel,
                color="regimen",
                facet_col="cancer",
                category_orders={"line_label": [LINE_LABELS.get("1", "1"), LINE_LABELS.get("2+", "2+")]},
                color_discrete_map=COLOR_MAP,
            )
            fig.update_layout(title=f"{metric_sel} — normalized by treatment setting (line)")
        else:
            fig = px.bar(
                long,
                x="cancer",
                y=metric_sel,
                color="regimen",
                facet_col="line_label",
                color_discrete_map=COLOR_MAP,
            )
            fig.update_layout(title=f"{metric_sel} — normalized by cancer")

        # make it normalized stacked percent here
        fig.update_layout(barmode="stack", barnorm="percent")

        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0f16",
            plot_bgcolor="#0b0f16",
            legend_title_text="Regimen",
            margin=dict(t=60, r=20, b=40, l=40),
            yaxis_ticksuffix="%",
        )
        fig.update_yaxes(title=metric_sel, rangemode="tozero", range=[0, 100])
        fig.update_xaxes(title=None)
        return fig
