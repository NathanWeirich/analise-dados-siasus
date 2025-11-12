import pandas as pd
from database_connection import *

conn = get_database_connection()

df = pd.read_sql("SELECT * FROM pars WHERE pa_ufmun = '431020';", conn)
df.to_csv('dados_pars.csv', index=False, encoding='utf-8-sig')
print(df)

conn.close()