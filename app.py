# main runner
import pathlib
import pandas as pd
from typing import Dict
import os, dash

import ui
import backend

APP_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = APP_DIR / "data"
XLSX_PATH = DATA_DIR / "third_clean.xlsx"

_df = pd.read_excel(XLSX_PATH)
_df.columns = [str(c).strip() for c in _df.columns]

# ---- Regimens (keep stack by regimen) ----
TREATMENT_PREFIX_MAP: Dict[str, str] = {
    "1": "PD-1 alone",
    "2": "PD-1 + CTLA-4",
    "3": "Neither",
}

# ---- Base metrics (ORR, PFS, OVS) ----
BASE_METRICS = ["ORR", "PFS", "OVS"]

# Build UI options
cancer_options = [
    {"label": c, "value": c}
    for c in sorted(_df["cancer"].dropna().astype(str).unique())
]

LINE_LABELS = {
    1: "No prior treatment",
    "1": "No prior treatment",
    "2+": "At least one prior treatment",
}
line_options_raw = _df["line"].dropna().astype(str).unique().tolist()
line_options = [
    {"label": LINE_LABELS.get(v, v), "value": v}
    for v in sorted(line_options_raw, key=lambda x: (x != "1", x))
]

treatment_options = [
    {"label": label, "value": prefix}
    for prefix, label in TREATMENT_PREFIX_MAP.items()
]

# Metric (base) and Year (single-select)
metric_options = [{"label": m, "value": m} for m in BASE_METRICS]
year_options = [
    {"label": "1-year", "value": "1"},
    {"label": "2-year", "value": "2"}
]

# Colours = regimens
COLOUR_MAP = {
    "PD-1 + CTLA-4": "#07ac1d",
    "Neither": "#e00a0a",
    "PD-1 alone": "#22ee22",
}

CONFIG = {
    "LINE_LABELS": LINE_LABELS,
    "TREATMENT_PREFIX_MAP": TREATMENT_PREFIX_MAP,
    "COLOR_MAP": COLOUR_MAP,
    # Map a year to the month suffix used in columns for time-based metrics

    "YEAR_TO_MONTHS": {
        "1": "12",
        "2": "24"
    },
}

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Stage IV Checkpoint Inhibitor Outcome Visualiser"

app.layout = ui.build_layout(
    cancer_options=cancer_options,
    line_options=line_options,
    treatment_options=treatment_options,  # keep regimens
    metric_options=metric_options,        # base metric: ORR / PFS / OVS
    year_options=year_options,            # single year choice
)

backend.register_callbacks(app, _df, CONFIG)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)