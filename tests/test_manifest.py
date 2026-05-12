import json

from stackoverflow_analytics.main import write_tables_to_excel
from stackoverflow_analytics.validate import read_cleaned_workbook, read_sheet_manifest


def test_write_tables_to_excel_creates_sheet_manifest(tmp_path):
    output_file = tmp_path / "cleaned.xlsx"
    manifest_file = tmp_path / "cleaned.manifest.json"
    long_name = "OfficeStackAsyncHaveWorkedWith"

    import pandas as pd

    write_tables_to_excel(
        {"Main": pd.DataFrame([{"ResponseId": 1}]), long_name: pd.DataFrame([{"ResponseId": 1}])},
        output_file,
        manifest_file,
    )

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    assert output_file.exists()
    assert manifest["sheets"]["Main"] == "Main"
    assert long_name in manifest["sheets"].values()


def test_read_sheet_manifest_returns_empty_mapping_when_file_is_missing(tmp_path):
    assert read_sheet_manifest(tmp_path / "missing.json") == {}


def test_read_cleaned_workbook_uses_manifest_logical_names(tmp_path):
    output_file = tmp_path / "cleaned.xlsx"
    manifest_file = tmp_path / "cleaned.manifest.json"

    import pandas as pd

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        pd.DataFrame([{"ResponseId": 1}]).to_excel(writer, sheet_name="Main", index=False)
        pd.DataFrame([{"ResponseId": 1}]).to_excel(
            writer, sheet_name="OfficeStackAsyncHaveWorkedWit", index=False
        )

    manifest_file.write_text(
        json.dumps(
            {
                "sheets": {
                    "Main": "Main",
                    "OfficeStackAsyncHaveWorkedWit": "OfficeStackAsyncHaveWorkedWith",
                }
            }
        ),
        encoding="utf-8",
    )

    tables = read_cleaned_workbook(output_file, manifest_file)

    assert "OfficeStackAsyncHaveWorkedWith" in tables
