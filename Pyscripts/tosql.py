import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv('C:\Users\user\Desktop\SO_powerbi\.env')
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


excel_file_path = 'Cleaned_SurveyData.xlsx'
engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
excel_data = pd.read_excel(excel_file_path, sheet_name=None)

for sheet_name, df in excel_data.items():
    table_name = sheet_name.lower().replace(' ', '_')
    print(f"Загружается таблица: {table_name} ({len(df)} строк)")

    df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

print("✅ Все таблицы успешно загружены")