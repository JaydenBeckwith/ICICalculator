# app.py — main runner
import pathlib
import pandas as pd
from typing import List, Dict

import dash

# Local modules
import ui
import backend

# -----------------------------
# Paths & Data
# -----------------------------
APP_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = APP_DIR / "data"
XLSX_PATH = DATA_DIR / "third_clean.xlsx"

# Load the data once at startup
_df = pd.read_excel(XLSX_PATH)
_df.columns = [str(c).strip() for c in _df.columns]

# Map the numeric prefixes to readable treatment labels
TREATMENT_PREFIX_MAP: Dict[str, str] = {
    "1": "PD-1 alone",
    "2": "PD-1 + CTLA-4",
    "3": "Neither",
}

# Identify available metrics by stripping the prefix from any column that starts with a known prefix
all_cols = list(_df.columns)
metric_suffixes = set()
for c in all_cols:
    for p in TREATMENT_PREFIX_MAP.keys():
        if c.startswith(p) and len(c) > 1:
            metric_suffixes.add(c[len(p):])

PREFERRED_METRIC_ORDER = ["ORR", "PFS12", "OVS12", "PFS24", "OVS24"]
metrics_available = [m for m in PREFERRED_METRIC_ORDER if m in metric_suffixes] + [
    m for m in sorted(metric_suffixes) if m not in PREFERRED_METRIC_ORDER
]

# Build options from data
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
    if any(f"{prefix}{m}" in _df.columns for m in metrics_available)
]

metric_options = [{"label": m, "value": m} for m in metrics_available]

# Colours to match dark theme
COLOUR_MAP = {
    "PD-1 + CTLA-4": "#07ac1d",  # violet-500
    "Neither": "#e00a0a",        # orange-500
    "PD-1 alone": "#22ee22",    # cyan-400
}

# Shared config passed to UI and callbacks
CONFIG = {
    "LINE_LABELS": LINE_LABELS,
    "TREATMENT_PREFIX_MAP": TREATMENT_PREFIX_MAP,
    "COLOR_MAP": COLOUR_MAP,
}

# -----------------------------
# App & Layout
# -----------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Stage IV Checkpoint Inhibitor Outcome Visualiser"

app.layout = ui.build_layout(
    cancer_options=cancer_options,
    line_options=line_options,
    treatment_options=treatment_options,
    metric_options=metric_options,
)

# -----------------------------
# Callbacks
# -----------------------------
backend.register_callbacks(app, _df, CONFIG)

# -----------------------------
# Entrypoint
# -----------------------------
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
