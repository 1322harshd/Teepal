import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Path to your .db file (SQLite)
sqlite_conn = sqlite3.connect('TeePal.db')  # Replace with actual file name

# Connect to PostgreSQL (replace with your credentials)
pg_engine = create_engine('postgresql+psycopg2://postgres:13Dhillon%40nz@localhost:5432/TeePal')

# List of tables to migrate
tables = ['Users', 'Products', 'Orders', 'OrderDetails', 'CartItems', 'SavedItems']
schema_name = 'teepal'

# Migrate each table
for table in tables:
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
        df.to_sql(table, pg_engine, schema=schema_name, if_exists='replace', index=False)
        print(f"✅ {table}: {len(df)} records migrated.")
    except Exception as e:
        print(f"❌ {table}: Error - {str(e)}")
