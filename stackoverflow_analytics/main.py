import json
import re

import numpy as np
import pandas as pd

from stackoverflow_analytics.config import (
    CLEANED_SURVEY_FILE,
    CLEANED_SURVEY_MANIFEST_FILE,
    RAW_SURVEY_FILE,
)

ID_COLUMN = "ResponseId"


def extract_age_range(age_str):
    if not isinstance(age_str, str):
        return None, None

    numbers = [int(value) for value in re.findall(r"\d+", age_str)]
    lowered = age_str.lower()

    if "under" in lowered and numbers:
        return 0, numbers[0] - 1
    if ("older" in lowered or "over" in lowered or ">" in lowered) and numbers:
        return numbers[0], 100
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    if "<" in age_str and numbers:
        return 0, numbers[0]

    return None, None


def max_reasonable_experience(row):
    _, age_max = extract_age_range(row["Age"])
    if age_max is None or pd.isna(row["YearsCode"]):
        return True

    try:
        exp = float(row["YearsCode"])
    except (TypeError, ValueError):
        return True

    return exp <= (age_max - 10)


def convert_years(val):
    if pd.isna(val):
        return np.nan

    if isinstance(val, str):
        val = val.strip()
        if "Less than" in val:
            return 0.5
        if "More than" in val:
            return 51
        try:
            return float(val)
        except ValueError:
            return np.nan

    return val


def get_multi_select_columns(df):
    return [col for col in df.columns if df[col].astype(str).str.contains(";").any()]


def make_excel_sheet_name(name, used_names):
    base_name = str(name).strip()[:31] or "Sheet"
    sheet_name = base_name
    suffix = 1

    while sheet_name in used_names:
        suffix_text = f"_{suffix}"
        sheet_name = f"{base_name[: 31 - len(suffix_text)]}{suffix_text}"
        suffix += 1

    used_names.add(sheet_name)
    return sheet_name


def clean_survey_data(df):
    required_columns = {ID_COLUMN, "Age", "YearsCode", "YearsCodePro"}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df = df.copy()
    df["YearsCode"] = df["YearsCode"].apply(convert_years)
    df["YearsCodePro"] = df["YearsCodePro"].apply(convert_years)
    df = df[df.apply(max_reasonable_experience, axis=1)]

    multi_select_columns = get_multi_select_columns(df)
    output_tables = {"Main": df.drop(columns=multi_select_columns)}

    for col in multi_select_columns:
        temp_df = df[[ID_COLUMN, col]].dropna(subset=[col]).copy()
        temp_df[col] = temp_df[col].astype(str).str.split(";")
        temp_df = temp_df.explode(col)
        temp_df[col] = temp_df[col].str.strip()
        output_tables[col.strip()] = temp_df

    return output_tables


def write_tables_to_excel(output_tables, output_file, manifest_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    used_sheet_names = set()
    manifest = {"sheets": {}}

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for logical_name, table in output_tables.items():
            safe_sheet_name = make_excel_sheet_name(logical_name, used_sheet_names)
            table.to_excel(writer, sheet_name=safe_sheet_name, index=False)
            manifest["sheets"][safe_sheet_name] = logical_name

    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    if not RAW_SURVEY_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {RAW_SURVEY_FILE}")

    df = pd.read_excel(RAW_SURVEY_FILE)
    output_tables = clean_survey_data(df)
    write_tables_to_excel(output_tables, CLEANED_SURVEY_FILE, CLEANED_SURVEY_MANIFEST_FILE)

    print(f"Done. Cleaned data saved to {CLEANED_SURVEY_FILE}")


if __name__ == "__main__":
    main()
