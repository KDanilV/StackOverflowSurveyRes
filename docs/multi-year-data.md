# Multi-Year Data

Проект можно расширять сырыми выгрузками Stack Overflow Developer Survey за соседние годы,
чтобы сравнивать динамику по зарплатам, технологиям, удаленной работе и отношению к AI.

## Источники Kaggle

| Год | Kaggle dataset | Статус |
| --- | --- | --- |
| 2022 | `imshiva10/stack-overflow-developer-survey-2022` | зеркало официальной выгрузки |
| 2023 | `stackoverflow/stack-overflow-2023-developers-survey` | официальная публикация Stack Overflow |
| 2025 | `aliaslam25/stack-overflow-developer-survey-2025` | зеркало официальной выгрузки |

## Загрузка

Kaggle API требует токен:

1. В профиле Kaggle создайте API token.
2. Положите `kaggle.json` в `%USERPROFILE%\.kaggle\kaggle.json` или задайте
   `KAGGLE_USERNAME` и `KAGGLE_KEY`.
3. Запустите загрузку:

```powershell
uv run python -m stackoverflow_analytics.kaggle_data
```

Для одного года:

```powershell
uv run python -m stackoverflow_analytics.kaggle_data --years 2023
```

Файлы сохраняются в:

```text
data/raw/2022/
data/raw/2023/
data/raw/2025/
```

## Что анализировать в динамике

- изменение популярности языков, баз данных, платформ и фреймворков;
- изменение медианных зарплат по странам и опыту;
- долю удаленного, гибридного и офисного формата;
- структуру ролей и уровня опыта;
- появление и развитие вопросов про AI в 2023-2025 годах.

Перед общей витриной нужно нормализовать различия схем: названия колонок и варианты ответов
между годами меняются.

## Базовый EDA и отбор полей

```powershell
uv run python -m stackoverflow_analytics.multiyear_eda
```

Скрипт оставляет две компактные таблицы:

- `core_survey.csv`: год, страна, возраст, образование, занятость, формат работы, роль,
  опыт, нормализованный профессиональный опыт, индустрия, зарплата, AI-поля,
  нормализованное использование AI и удовлетворенность работой;
- `technology_counts.csv`: агрегированная популярность worked/wanted/admired технологий по
  категориям и годам.

Для 2025 дополнительно нормализуются новые блоки:

- `WorkExp` используется как fallback для отсутствующего `YearsCodePro`;
- `JobSatPoints_*` сворачиваются в `JobSatNormalized`;
- новые AI tool/model/agent поля сворачиваются в `AIAdoption` и категорию `ai_search_or_dev`;
- `DevEnvs*`, `CommPlatform*`, `SOTags*` и `*Admired` попадают в агрегаты технологий.

Остальные raw-колонки не удаляются из источников, но не попадают в аналитическую витрину,
потому что они либо нестабильны между годами, либо слишком детальны для сравнения динамики.

