import pandas as pd
from sqlalchemy import create_engine, text


currency_to_usd = {
    'USD': 1.0,
    'IDR': 0.000065,   
    'BSD': 1.0,       
    'ANG': 0.56,       
    'ILS': 0.27,      
    'KHR': 0.00025,    
    'CZK': 0.045,      
    'HKD': 0.13,      
    'QAR': 0.27,      
    'IMP': 1.0,       
    'DKK': 0.15,
    'BWP': 0.085,
    'LKR': 0.0032,
    'TZS': 0.00043,
    'GIP': 1.27,       
    'NGN': 0.0024,
    'BYN': 0.39,
    'KRW': 0.00075,
    'MGA': 0.00024,
    'INR': 0.012,
    'BMD': 1.0,
    'ERN': 0.066,
    'CRC': 0.00165,
    'SRD': 0.049,
    'GTQ': 0.13,
    'ZAR': 0.055,
    'BTN': 0.012,     
    'THB': 0.028,
    'XOF': 0.0016,
    'MWK': 0.00067,
    'GEL': 0.41,
    'CVE': 0.0095,
    'CAD': 0.73,
    'WST': 0.35,
    'JMD': 0.0065,
    'VND': 0.000042,
    'ALL': 0.0083,
    'OMR': 2.60,
    'MKD': 0.017,
    'BAM': 0.54,
    'GGP': 1.27,
    'KMF': 0.0024,
    'MOP': 0.12,
    'CNY': 0.14,
    'SZL': 0.055,
    'KZT': 0.0022,
    'TRY': 0.035,
    'HUF': 0.0027,
    'SDG': 0.0022,
    'TMT': 0.29,
    'CDF': 0.00045,
    'AMD': 0.0027,
    'HNL': 0.040,
    'COP': 0.00025,
    'LYD': 0.22,
    'RSD': 0.0093,
    'NPR': 0.0076,
    'DZD': 0.0076,
    'SAR': 0.27,
    'MDL': 0.056,
    'AUD': 0.67,
    'BBD': 0.50,
    'BIF': 0.00049,
    'TND': 0.34,
    'ARS': 0.0080,
    'TTD': 0.15,
    'KGS': 0.011,
    'IRR': 0.000024,
    'XPF': 0.0091,
    'NAD': 0.055,
    'UZS': 0.000087,
    'UGX': 0.00027,
    'BDT': 0.0094,
    'ETB': 0.020,
    'AED': 0.27,
    'SEK': 0.094,
    'MZN': 0.016,
    'JPY': 0.0068,
    'NIO': 0.028,
    'FKP': 1.27,
    'MYR': 0.21,
    'MAD': 0.10,
    'SHP': 1.27,
    'MNT': 0.00033,
    'TJS': 0.092,
    'KES': 0.0078,
    'ZMW': 0.052,
    'RUB': 0.013,
    'RWF': 0.00097,
    'CLP': 0.0012,
    'VES': 0.000067,
    'EGP': 0.032,
    'LBP': 0.000067,
    'BRL': 0.19,
    'PYG': 0.00014,
    'BOB': 0.14,
    'AZN': 0.59,
    'PHP': 0.018,
    'KYD': 1.20,
    'TWD': 0.032,
    'BND': 0.73,
    'RON': 0.23,
    'CHF': 1.10,
    'GHS': 0.090,
    'EUR': 1.09,
    'MVR': 0.065,
    'GBP': 1.28,
    'BGN': 0.56,
    'AOA': 0.00022,
    'SGD': 0.73,
    'UYU': 0.027,
    'IQD': 0.00069,
    'AFN': 0.011,
    'XCD': 0.37,
    'NZD': 0.62,
    'NOK': 0.092,
    'XDR': 1.40,
    'YER': 0.0040,
    'UAH': 0.027,
    'CUP': 0.038,
    'XAF': 0.0018,  # Центральноафриканский CFA франк
    'CFP': 0.0091,  # CFP franc (уже есть)
    'BHD': 2.65,    # Bahraini dinar
    'MRU': 0.027,   # Mauritanian ouguiya
    'PEN': 0.30,    # Peruvian sol
    'SOS': 0.0018,  # Somali shilling
    'FJD': 0.4459,  # 1 FJD ≈ 0.4459 USD :contentReference[oaicite:1]{index=1}
    'DOP': 0.0166,  # 1 DOP ≈ 0.0166 USD :contentReference[oaicite:2]{index=2}
    'ISK': 0.00826, # 1 ISK ≈ 0.00826 USD :contentReference[oaicite:3]{index=3}
    'PKR': 0.0036,  # Пакистанская рупия – приблизительно 0.0036 USD (ориентир)
    'JOD': 1.41,    # Иорданский динар — около 1.41 USD (ориентир)
    'GYD': 0.0048,  # Гайанский доллар ≈ 0.0048 USD
    'AWG': 0.56,    # Арубский флорин ≈ 0.56 USD
    'MXN': 0.057,   # Мексиканское песо ≈ 0.057 USD
    'MUR': 0.024,   # Маврикийская рупия ≈ 0.024 USD
    'KWD': 3.28,    # Кувейтский динар ≈ 3.28 USD
    'SLL': 0.000051,# Сьерра-Леоне леоне ≈ 0.000051 USD
    'MMK': 0.00049, # Мьянманский кьят ≈ 0.00049 USD
    "PLN": 0.25,   # Polish Zloty
    "SYP": 0.00040 # Syrian Pound (очень низкий курс)
}


df = pd.read_excel('Cleaned_SurveyData.xlsx', sheet_name='Main')

df['CompTotal'] = pd.to_numeric(df['CompTotal'], errors='coerce')


def conv_usd(curr, sal):
    if pd.isna(curr) or pd.isna(sal):
        return None
    rate = currency_to_usd.get(curr.strip())
    return round(sal * rate, 2) if rate else None

def extract_currency_code(currency_str):
    if not isinstance(currency_str, str):
        return None
    if "\t" in currency_str:
        return currency_str.split("\t")[0].strip()
    return currency_str.split(" ")[0].strip()

df['CurrencyCode'] = df['Currency'].apply(extract_currency_code)

df['salaryusd'] = df.apply(
    lambda r: conv_usd(r['CurrencyCode'],  r['CompTotal']),
    axis=1
)

df = df[df['salaryusd'].notna() & (df['salaryusd'] > 100) & (df['salaryusd'] < 500_000)]

print(df[['Currency', 'CurrencyCode', 'CompTotal', 'ConvertedCompYearly', 'salaryusd']].head(20))

engine = create_engine('postgresql+psycopg2://postgres:2281337@localhost:5432/stackoverflow')

update_data = [
    {"usd": row["salaryusd"], "rid": int(row["ResponseId"])}
    for _, row in df.iterrows()
    if pd.notnull(row["salaryusd"]) and pd.notnull(row["ResponseId"])
]

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE main ADD COLUMN IF NOT EXISTS salaryusd numeric"))

    conn.execute(text("""
        UPDATE main
        SET salaryusd = :usd
        WHERE "ResponseId" = :rid
    """), update_data)