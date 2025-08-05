import psycopg2
from dotenv import load_dotenv
import os

load_dotenv('C:\Users\user\Desktop\SO_powerbi\.env')
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_HOST
)
cursor = conn.cursor()

# Названия всех таблиц, кроме main
child_tables = [
    'Employment', 'CodingActivities', 'LearnCode', 'LearnCodeOnline', 'TechDoc', 'BuyNewTool', 'TechEndorse',
    'LanguageHaveWorkedWith', 'LanguageWantToWorkWith', 'LanguageAdmired',
    'DatabaseHaveWorkedWith', 'DatabaseWantToWorkWith', 'DatabaseAdmired',
    'PlatformHaveWorkedWith', 'PlatformWantToWorkWith', 'PlatformAdmired',
    'WebframeHaveWorkedWith', 'WebframeWantToWorkWith', 'WebframeAdmired',
    'EmbeddedHaveWorkedWith', 'EmbeddedWantToWorkWith', 'EmbeddedAdmired',
    'MiscTechHaveWorkedWith', 'MiscTechWantToWorkWith', 'MiscTechAdmired',
    'ToolsTechHaveWorkedWith', 'ToolsTechWantToWorkWith', 'ToolsTechAdmired',
    'NEWCollabToolsHaveWorkedWith', 'NEWCollabToolsWantToWorkWith', 'NEWCollabToolsAdmired',
    'OpSysPersonal use', 'OpSysProfessional use',
    'OfficeStackAsyncHaveWorkedWith', 'OfficeStackAsyncWantToWorkWith', 'OfficeStackAsyncAdmired',
    'OfficeStackSyncHaveWorkedWith', 'OfficeStackSyncWantToWorkWith', 'OfficeStackSyncAdmired',
    'AISearchDevHaveWorkedWith', 'AISearchDevWantToWorkWith', 'AISearchDevAdmired',
    'NEWSOSites', 'SOHow', 'AIBen',
    'AIToolCurrently Using', 'AIToolInterested in Using', 'AIToolNot interested in Using',
    'AINextMuch more integrated', 'AINextNo change', 'AINextMore integrated',
    'AINextLess integrated', 'AINextMuch less integrated',
    'AIEthics', 'AIChallenges', 'ProfessionalTech'
]

for i in range(len(child_tables)):
    child_tables[i] = child_tables[i].lower().replace(" ", "_")

for table in child_tables:
    try:
        query = f"""
        ALTER TABLE "{table}"
        ADD CONSTRAINT fk_{table}_responseid
        FOREIGN KEY ("ResponseId")
        REFERENCES main("ResponseId")
        ON DELETE CASCADE;
        """
        cursor.execute(query)
        print(f"[+] Foreign key added for table: {table}")
    except Exception as e:
        print(f"[!] Failed for table {table}: {e}")

conn.commit()
cursor.close()
conn.close()