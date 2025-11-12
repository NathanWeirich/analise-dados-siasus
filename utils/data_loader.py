"""Funções para carregar e preparar dados"""

import pandas as pd
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_connection import get_database_connection

def carregar_csv(caminho='dados_limpos.csv'):
    """Carrega dados do CSV"""
    df = pd.read_csv(caminho, low_memory=False)
    return df

def carregar_tabela_db(nome_tabela, colunas='*', condicao=''):
    """Carrega tabela do banco de dados"""
    conn = get_database_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = f"SELECT {colunas} FROM {nome_tabela}"
        if condicao:
            query += f" WHERE {condicao}"
        
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def carregar_procedimentos():
    """Carrega tabela de procedimentos (tb_sigtaw)"""
    df = carregar_tabela_db('tb_sigtaw', 'ip_cod, ip_dscr')
    if not df.empty:
        df['ip_cod'] = df['ip_cod'].astype(str).str.strip()
        df['ip_cod_padrao'] = df['ip_cod'].str.zfill(10).str.upper()
    return df

def carregar_municipios():
    """Carrega tabela de municípios"""
    df = carregar_tabela_db('tb_municip', 'co_municip, ds_nome', "co_status = 'ATIVO'")
    if not df.empty:
        df['co_municip'] = df['co_municip'].astype(str).str.strip()
    return df

def carregar_estabelecimentos():
    """Carrega tabela de estabelecimentos (CNES)"""
    df = carregar_tabela_db('cadgerrs', 'cnes, fantasia, raz_soci, codufmun, bairro', 'excluido = 0')
    if not df.empty:
        df['cnes'] = df['cnes'].astype(str).str.strip()
    return df

def carregar_cids():
    """Carrega tabela de CIDs"""
    df = carregar_tabela_db('s_cid', 'cd_cod, cd_descr')
    if not df.empty:
        df['cd_cod'] = df['cd_cod'].astype(str).str.strip().str.upper()
    return df

def carregar_dim_tempo():
    """Carrega dimensão tempo"""
    df = carregar_tabela_db('dimtempo', 'Id, mes, mesext, ano, anomes, MAExt, trimestre, triex_t, anotri')
    if not df.empty:
        df['anomes'] = df['anomes'].astype(int)
    return df