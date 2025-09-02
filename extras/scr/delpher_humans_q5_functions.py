"""
Summarization utilities for Wikidata-derived person attributes.

This module provides helper functions for aggregating and summarizing
columns in tabular datasets (typically exported from Wikidata or related
data pipelines). Both functions return tidy summary DataFrames with
counts and lists of associated QIDs, useful for building dropdown
filters, statistics, or reports.

Functions:
----------
- summarize_list_column:
    Summarize a dataframe column containing lists of values (e.g.,
    occupations, genders, countries) or single strings. Produces one row
    per unique value, the list of QIDs having that value, and the count.

- summarize_year_column:
    Parse Wikidata-style timestamp strings, extract year (or decade),
    and count associated QIDs. Supports filtering by precision and
    optional decade binning.

Typical use cases:
------------------
- Preparing dropdown options for interactive galleries or dashboards.
- Building "occupation", "gender", or "citizenship" facets with counts.
- Aggregating by birth/death year (or decade) for timeline visualizations.

**Author:** Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
**Supported by:** ChatGPT
**Last updated:** 20 August 2025
"""


import re
import pandas as pd
from collections import defaultdict
from typing import Optional

def summarize_list_column(
    df: pd.DataFrame,
    list_col: str,
    qid_col: str = "WikidataQID",
    label_prefix: Optional[str] = None) -> pd.DataFrame:
    """
    Summarize a column that may contain lists (e.g., occupations) or single strings
    into one row per unique value, including:
      - a list of QIDs (from `qid_col`) that have that value,
      - and a count of those QIDs.

    Intended use-cases:
      - Occupations, genders, countries-of-citizenship, etc. where a person (QID) can
        have 0, 1, or many values.

    Args:
        df (pd.DataFrame): Source dataframe.
        list_col (str): Name of the column that contains either lists of strings or a single string.
        qid_col (str): Name of the column containing the person/entity QIDs. Defaults to 'WikidataQID'.
        label_prefix (str, optional): Prefix for the output column names. Defaults to `list_col`
            when not provided. The output columns are:
              - f"{label_prefix}QID"
              - f"PeopleWithThis{label_prefix}QIDs"
              - "NumPeople"

    Returns:
        pd.DataFrame: A dataframe with one row per unique value found in `list_col`, including:
          - <label_prefix>QID (the unique value found),
          - PeopleWithThis<label_prefix>QIDs (list of QIDs),
          - NumPeople (integer count).

    Raises:
        TypeError: If `df` is not a pandas DataFrame or column names are not strings.
        ValueError: If required columns are missing, or no valid data is found.

    Notes:
        - Rows with missing/NaN QIDs are ignored.
        - For list-like entries, only non-null items are collected.
        - Single-string entries are trimmed and ignored if empty.
    """
    # ---- Validate inputs early
    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"`df` must be a pandas DataFrame, got {type(df).__name__}")
        if not isinstance(list_col, str) or not list_col:
            raise TypeError("`list_col` must be a non-empty string")
        if not isinstance(qid_col, str) or not qid_col:
            raise TypeError("`qid_col` must be a non-empty string")

        # Column existence
        missing = [c for c in (list_col, qid_col) if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required column(s): {missing}")

        # Normalize prefix
        effective_prefix = label_prefix if (isinstance(label_prefix, str) and label_prefix.strip()) else list_col

        # ---- Build value -> [QIDs] mapping
        value_dict = defaultdict(list)

        # Iterate defensively (avoid KeyError; use .get with defaults)
        for _, row in df.iterrows():
            qid = row.get(qid_col)
            if pd.isna(qid):
                continue  # skip rows with missing QID

            values = row.get(list_col, None)

            # Case 1: values is a list-like
            if isinstance(values, list):
                for v in values:
                    if isinstance(v, str):
                        v_str = v.strip()
                        if v_str:
                            value_dict[v_str].append(qid)
                    elif pd.notna(v):
                        # If it's not a string but still a valid non-null, coerce to string
                        value_dict[str(v)].append(qid)

            # Case 2: values is a single string
            elif isinstance(values, str):
                v_str = values.strip()
                if v_str:
                    value_dict[v_str].append(qid)

            # Other types are ignored (None/NaN, numbers without meaning, etc.)

        if not value_dict:
            raise ValueError(f"No valid data found to summarize in column '{list_col}'.")

        # ---- Build summary DataFrame
        summary_rows = [
            {
                f"{effective_prefix}QID": value,
                f"PeopleWithThis{effective_prefix}QIDs": qids,
                "NumPeople": len(qids),
            }
            for value, qids in value_dict.items()
        ]

        summary_df = pd.DataFrame(summary_rows)

        # Sort by count desc, then value asc (case-insensitive where applicable)
        if not summary_df.empty:
            # Stable, case-insensitive sort for the value column
            value_col = f"{effective_prefix}QID"
            if summary_df[value_col].dtype == object:
                summary_df = summary_df.sort_values(
                    by=["NumPeople", value_col],
                    ascending=[False, True],
                    key=lambda s: s.str.lower() if s.dtype == "object" else s,
                )
            else:
                summary_df = summary_df.sort_values(by=["NumPeople", value_col], ascending=[False, True])

            summary_df = summary_df.reset_index(drop=True)

        return summary_df

    except (TypeError, ValueError) as e:
        # Known, user-fixable issues
        raise
    except Exception as e:
        # Unexpected failure → re-raise with more context
        raise RuntimeError(f"Failed to summarize column '{list_col}' with qid_col '{qid_col}': {e}") from e


def summarize_year_column(
    df: pd.DataFrame,
    timestamp_col: str,
    qid_col: str = "WikidataQID",
    label: str = "Year",
    bin_by_decade: bool = False,
    report_ignored: bool = True) -> pd.DataFrame:
    """
    Summarize a column of Wikidata-style timestamps (e.g. "+1875-03-11T00:00:00Z^^11")
    into counts per year (or decade), plus the list of QIDs for each bucket.

    A timestamp is considered valid if:
      - It matches the pattern: ^[+-]?(\\d{1,6})-.*\\^\\^(\\d+)$
        (leading sign optional; allows 1–6 digit year to handle BCE/early years)
      - Its precision integer is ≥ 9 (year-level or better in Wikidata).

    Args:
        df (pd.DataFrame):
            Source dataframe.
        timestamp_col (str):
            Name of the column with timestamp strings.
        qid_col (str):
            Name of the column containing entity/person QIDs. Default: "WikidataQID".
        label (str):
            Column label in the result for the year/decade bucket. Default: "Year".
        bin_by_decade (bool):
            If True, bucket by decade (e.g., 1870, 1880, ...). Default: False.
        report_ignored (bool):
            If True, prints the number of ignored rows (low precision, bad format, or missing). Default: True.

    Returns:
        pd.DataFrame:
            Columns:
              - <label> : int (year or decade)
              - PeopleWithThis<label>QIDs : list[str]
              - NumPeople : int

            Sorted by <label> ascending.

    Raises:
        TypeError:
            If `df` is not a DataFrame or any string parameters are not strings.
        ValueError:
            If required columns are missing, or if no valid years are found.
        RuntimeError:
            For unexpected internal errors (re-raised with context).
    """
    # ---- Validate inputs ------------------------------------------------------
    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"`df` must be a pandas DataFrame, got {type(df).__name__}")
        for name, val in {
            "timestamp_col": timestamp_col,
            "qid_col": qid_col,
            "label": label,
        }.items():
            if not isinstance(val, str) or not val.strip():
                raise TypeError(f"`{name}` must be a non-empty string")

        missing = [c for c in (timestamp_col, qid_col) if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required column(s): {missing}")

        if not isinstance(bin_by_decade, bool):
            raise TypeError("`bin_by_decade` must be a bool")
        if not isinstance(report_ignored, bool):
            raise TypeError("`report_ignored` must be a bool")

        # ---- Core logic -------------------------------------------------------
        year_dict = defaultdict(list)
        ignored_rows = []

        # Accept 1–6 digit years with optional sign, capture precision after ^^
        # Examples matched:
        #  "+1869-03-17T00:00:00Z^^11"
        #  "-0600-01-01T00:00:00Z^^7"
        pattern = re.compile(r'^[+-]?(\d{1,6})-.*\^\^(\d+)$')

        for idx, row in df.iterrows():
            ts_raw = row.get(timestamp_col)
            qid = row.get(qid_col)

            if pd.isna(qid):
                # No QID → skip
                continue

            ts = "" if ts_raw is None else str(ts_raw).strip()
            if not ts:
                # Empty timestamp → skip quietly
                continue

            m = pattern.match(ts)
            if not m:
                ignored_rows.append((idx, ts))
                continue

            try:
                year = int(m.group(1))
                precision = int(m.group(2))
            except Exception:
                ignored_rows.append((idx, ts))
                continue

            # Wikidata precision: 9 = year; ignore < 9
            if precision < 9:
                ignored_rows.append((idx, ts))
                continue

            if bin_by_decade:
                year = (year // 10) * 10

            year_dict[year].append(qid)

        if not year_dict:
            raise ValueError(
                f"No valid years found in column '{timestamp_col}' "
                f"(after precision and format checks)."
            )

        summary_rows = [
            {
                f"{label}": y,
                f"PeopleWithThis{label}QIDs": qids,
                "NumPeople": len(qids),
            }
            for y, qids in year_dict.items()
        ]
        out = pd.DataFrame(summary_rows).sort_values(by=label).reset_index(drop=True)

        if report_ignored:
            print(
                f"⚠️ Ignored {len(ignored_rows)} rows in '{timestamp_col}' "
                f"due to low precision (<9), invalid format, or missing value."
            )
            if ignored_rows:
                # Comment these lines out if you want quieter logs:
                print("Ignored examples (row_index, raw_value):")
                for idx, val in ignored_rows[:20]:  # cap to avoid flooding
                    print(f"  - Row {idx}: {val}")
                if len(ignored_rows) > 20:
                    print(f"  ... and {len(ignored_rows) - 20} more")

        return out

    except (TypeError, ValueError):
        # Propagate user-fixable errors as-is
        raise
    except Exception as e:
        # Unexpected issues → wrap in a RuntimeError with context
        raise RuntimeError(
            f"Failed to summarize years from '{timestamp_col}' "
            f"(qid_col='{qid_col}', label='{label}', bin_by_decade={bin_by_decade}): {e}"
        ) from e