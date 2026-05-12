import argparse

from stackoverflow_analytics.main import main as clean_data
from stackoverflow_analytics.validate import main as validate_cleaned_data


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Stack Overflow survey ETL pipeline.")
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Reuse the existing Cleaned_SurveyData.xlsx file.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip cleaned Excel validation after generation.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.skip_clean:
        clean_data()

    if not args.skip_validation:
        validate_cleaned_data()

    print("Done. Pipeline completed successfully.")


if __name__ == "__main__":
    main()
