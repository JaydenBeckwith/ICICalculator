import pandas as pd
import pytest

from backend import _melt_for_plot, _resolve_metric_suffix, _filter_df

# ------------------------------- Fixtures -------------------------------

@pytest.fixture
def sample_df():
    # Wide data with three regimen prefixes: A, B, C
    return pd.DataFrame(
        {
            "cancer": ["Melanoma", "NSCLC", "Melanoma"],
            "line": [1, 2, 3],
            "A_ORR": [45, "N/A", 30],     # includes a non-numeric that should be dropped
            "B_ORR": [50, 40, None],      # includes NaN that should be dropped
            "C_ORR": [10, 20, 30],
            "A_PFS6": [5.5, 3.2, 2.1],    # for illustration if needed elsewhere
        }
    )

@pytest.fixture
def reg_config():
    reg_prefixes = ["A_", "B_", "C_"]
    treatment_prefix_map = {"A": "Atezo", "B": "BRAFi", "C": "Combo"}
    line_labels = {"1": "1L", "2": "2L"}  # 3 is intentionally missing to test fallback
    return reg_prefixes, treatment_prefix_map, line_labels

# ----------------------------- _filter_df function -------------------------------

def test_filter_df_by_cancer(sample_df):
    out = _filter_df(sample_df, cancers=["Melanoma"], lines=[])
    assert set(out["cancer"].unique()) == {"Melanoma"}
    # returns a copy (changing out shouldn't change original)
    out.loc[out.index[0], "cancer"] = "Changed"
    assert sample_df.loc[0, "cancer"] == "Melanoma"

def test_filter_df_by_line_(sample_df):
    # Lines can be provided as ints or strings; they are coerced to str in function
    out1 = _filter_df(sample_df, cancers=[], lines=[1, "2"])
    assert set(out1["line"]) == {1, 2}

def test_filter_df_by_both(sample_df):
    out = _filter_df(sample_df, cancers=["NSCLC"], lines=[2])
    assert len(out) == 1
    assert out.iloc[0]["cancer"] == "NSCLC"
    assert out.iloc[0]["line"] == 2

def test_filter_df_no_filters_returns_copy(sample_df):
    out = _filter_df(sample_df, cancers=[], lines=[])
    assert out.equals(sample_df)
    # ensure it's not the same object
    assert id(out) != id(sample_df)

# ------------------------ _resolve_metric_suffix fx ------------------------

@pytest.mark.parametrize(
    "base_metric,year,year_to_months,expected",
    [
        ("ORR", "2024", {"2024": "6"}, "ORR"),        # ORR ignores year
        ("PFS", "2024", {"2024": "6"}, "PFS6"),
        ("OVS", "2023", {"2023": "12"}, "OVS12"),
        ("PFS", "2022", {"2023": "6"}, ""),           # missing mapping -> ""
        ("", "2024", {"2024": "6"}, ""),              # invalid base metric
        (None, "2024", {"2024": "6"}, ""),            # None -> ""
        ("pfS", "2024", {"2024": "6"}, "PFS6"),       # case-insensitive
    ],
)
def test_resolve_metric_suffix(base_metric, year, year_to_months, expected):
    assert _resolve_metric_suffix(base_metric, year, year_to_months) == expected

# --------------------------- _melt_for_plot fx -----------------------------

def test_melt_for_plot_basic(sample_df, reg_config):
    reg_prefixes, tmap, line_labels = reg_config
    out = _melt_for_plot(sample_df, "ORR", reg_prefixes, tmap, line_labels)

    # Expected columns present
    assert {"cancer", "line", "regimen", "line_label", "ORR"} <= set(out.columns)

    # Non-numeric and NaN rows should be dropped
    # Starting df has 3 rows x 3 regimen cols = 9 rows; two invalid values -> 7 remain
    assert len(out) == 7

    # Regimen mapping by first letter works
    assert set(out["regimen"].unique()) <= {"Atezo", "BRAFi", "Combo"}

    # line_label mapped for 1 and 2; fallback to "3" as string
    row_line3 = out[out["line"] == 3].iloc[0]
    assert row_line3["line_label"] == "3"

    # ORR column is numeric
    assert pd.api.types.is_numeric_dtype(out["ORR"])

def test_melt_for_plot_no_matching_columns(sample_df, reg_config):
    reg_prefixes, tmap, line_labels = reg_config
    out = _melt_for_plot(sample_df, "DOR", reg_prefixes, tmap, line_labels)
    # Should return empty df with expected headings
    assert out.empty
    assert list(out.columns) == ["cancer", "line", "regimen", "DOR"]

def test_melt_for_plot_subset_prefixes(sample_df):
    # Only use A_ and C_ to ensure selective inclusion
    reg_prefixes = ["A_", "C_"]
    tmap = {"A": "Atezo", "C": "Combo"}
    line_labels = {"1": "1L"}

    out = _melt_for_plot(sample_df, "ORR", reg_prefixes, tmap, line_labels)
    assert set(out["regimen"].unique()) <= {"Atezo", "Combo"}
    # B_ regimen should not appear
    assert "BRAFi" not in set(out["regimen"].unique())

def test_melt_for_plot_respects_numeric_coercion(sample_df, reg_config):
    reg_prefixes, tmap, line_labels = reg_config
    out = _melt_for_plot(sample_df, "ORR", reg_prefixes, tmap, line_labels)
    # There should be no NaNs in metric column after dropna
    assert out["ORR"].isna().sum() == 0