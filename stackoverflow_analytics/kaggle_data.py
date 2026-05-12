"""Загрузка дополнительных годовых выгрузок Stack Overflow Developer Survey с Kaggle."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from stackoverflow_analytics.config import RAW_DATA_DIR


@dataclass(frozen=True)
class KaggleDataset:
    year: int
    slug: str
    source_url: str
    note: str


DATASETS: dict[int, KaggleDataset] = {
    2022: KaggleDataset(
        year=2022,
        slug="imshiva10/stack-overflow-developer-survey-2022",
        source_url="https://www.kaggle.com/datasets/imshiva10/stack-overflow-developer-survey-2022",
        note="Пользовательское зеркало официальной выгрузки Stack Overflow 2022.",
    ),
    2023: KaggleDataset(
        year=2023,
        slug="stackoverflow/stack-overflow-2023-developers-survey",
        source_url="https://www.kaggle.com/datasets/stackoverflow/stack-overflow-2023-developers-survey",
        note="Официальная публикация Stack Overflow на Kaggle.",
    ),
    2025: KaggleDataset(
        year=2025,
        slug="aliaslam25/stack-overflow-developer-survey-2025",
        source_url="https://www.kaggle.com/datasets/aliaslam25/stack-overflow-developer-survey-2025",
        note="Пользовательское зеркало официальной выгрузки Stack Overflow 2025.",
    ),
}


def _kaggle_token_exists() -> bool:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    kaggle_config_dir = Path(os.environ.get("KAGGLE_CONFIG_DIR", Path.home() / ".kaggle"))
    return (kaggle_config_dir / "kaggle.json").exists()


def _kaggle_command() -> list[str]:
    if shutil.which("kaggle"):
        return ["kaggle"]
    return ["uv", "run", "--with", "kaggle", "kaggle"]


def download_dataset(dataset: KaggleDataset, *, force: bool = False) -> Path:
    target_dir = RAW_DATA_DIR / str(dataset.year)
    target_dir.mkdir(parents=True, exist_ok=True)

    marker_path = target_dir / "kaggle_dataset.json"
    has_existing_files = any(path.name != marker_path.name for path in target_dir.iterdir())
    if has_existing_files and not force:
        print(
            f"{dataset.year}: файлы уже есть в {target_dir}; используйте --force для перезагрузки."
        )
        return target_dir

    command = [
        *_kaggle_command(),
        "datasets",
        "download",
        "-d",
        dataset.slug,
        "-p",
        str(target_dir),
        "--unzip",
    ]
    subprocess.run(command, check=True)

    marker_path.write_text(
        json.dumps(
            {
                "year": dataset.year,
                "slug": dataset.slug,
                "source_url": dataset.source_url,
                "note": dataset.note,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=sorted(DATASETS),
        choices=sorted(DATASETS),
        help="Годы для загрузки.",
    )
    parser.add_argument(
        "--force", action="store_true", help="Перезагрузить уже существующие файлы."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not _kaggle_token_exists():
        print(
            "Не найден Kaggle API token. Создайте token на Kaggle и положите kaggle.json "
            "в %USERPROFILE%\\.kaggle\\, задайте KAGGLE_CONFIG_DIR или переменные "
            "KAGGLE_USERNAME и KAGGLE_KEY.",
            file=sys.stderr,
        )
        return 2

    for year in args.years:
        download_dataset(DATASETS[year], force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
