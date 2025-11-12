import pandas as pd
from database_connection import *

conn = get_database_connection()

# Santa Rosa: 431720
# Cruz Alta: 430610
df = pd.read_sql("SELECT * FROM pars WHERE pa_ufmun = '430610';", conn)
df.to_csv('dados_pars_ca.csv', index=False, encoding='utf-8-sig')
len(df)

conn.close()