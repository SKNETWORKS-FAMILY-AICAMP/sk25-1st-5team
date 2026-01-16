import os
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import create_engine

# .env 로드
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# DB 엔진
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# CSV
df = pd.read_csv("./data/kia_faq.csv") 

# DB INSERT
df.to_sql(
    name="FAQ",          
    con=engine,
    if_exists="append",      
    index=False              
)

print("DB INSERT 완료")
