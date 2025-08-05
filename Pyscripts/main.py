import pandas as pd
import numpy as np


input_file = 'survey_results_public.xlsx'
id_column = 'ResponseId'  
df = pd.read_excel(input_file)

def extract_age_range(age_str):
    if isinstance(age_str, str):
        if "<" in age_str:
            return 0, int(age_str.replace("<", ""))
        elif ">" in age_str:
            return int(age_str.replace(">", "")), 100
        elif "-" in age_str:
            parts = age_str.split("-")
            return int(parts[0]), int(parts[1])
    return None, None


def max_reasonable_experience(row):
    age_min, age_max = extract_age_range(row['Age'])
    if pd.isna(row['YearsCode']):
        return True 
    try:
        exp = float(row['YearsCode'])
        return exp <= (age_max - 10)
    except:
        return True
    return True


def convert_years(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, str):
        val = val.strip()
        if 'Less than' in val:
            return 0.5
        elif 'More than' in val:
            return 51
        else:
            try:
                return float(val)
            except:
                return np.nan
    return val

df['YearsCode'] = df['YearsCode'].apply(convert_years)
df['YearsCodePro'] = df['YearsCodePro'].apply(convert_years)

df = df[df.apply(max_reasonable_experience, axis=1)]

# Столбцы с множественным выбором
multi_select_columns = [
    col for col in df.columns
    if df[col].astype(str).str.contains(';').any()
]

output_tables = {}

main_df = df.drop(columns=multi_select_columns)
output_tables['Main'] = main_df

# Обработка множественных выборов в отдельные таблицы
for col in multi_select_columns:
    temp_df = (
        df[[id_column, col]]
        .dropna(subset=[col])
        .assign(**{col: df[col].astype(str).str.split(';')})
        .explode(col)
        .rename(columns={col: col.strip()})
    )
    temp_df[col] = temp_df[col].str.strip()
    output_tables[col] = temp_df

output_file = 'Cleaned_SurveyData.xlsx'

with pd.ExcelWriter(output_tables, engine='xlsxwriter') as writer:
    for sheet_name, table in output_tables.items():
        sheet_name = sheet_name[:31]
        table.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Готово! Данные сохранены в {'Cleaned_SurveyData.xlsx'}")