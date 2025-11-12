"""Funções para processar e enriquecer dados"""

import pandas as pd
from datetime import timedelta

def padronizar_codigo(df, coluna, tamanho=10):
    """Padroniza código com zeros à esquerda"""
    df = df.copy()
    df[coluna] = df[coluna].astype(str).str.strip().str.zfill(tamanho).str.upper()
    return df

def adicionar_descricoes(df, df_ref, col_codigo, col_ref, col_descricao):
    """Adiciona descrições através de merge"""
    return df.merge(
        df_ref[[col_ref, col_descricao]], 
        left_on=col_codigo, 
        right_on=col_ref, 
        how='left'
    )

def preparar_competencia(df, coluna='PA_CMP'):
    """Prepara coluna de competência (AAAAMM)"""
    df = df.copy()
    df['Competencia'] = df[coluna].astype(str).str[:4] + '-' + df[coluna].astype(str).str[4:6]
    return df

def preparar_temporal(df, coluna='PA_CMP'):
    """Prepara colunas temporais"""
    df = df.copy()
    df[coluna] = pd.to_datetime(df[coluna].astype(str), format='%Y%m', errors='coerce')
    df = df.dropna(subset=[coluna])
    df['ano'] = df[coluna].dt.year
    df['mes'] = df[coluna].dt.month
    df['anomes'] = (df['ano'] * 100 + df['mes']).astype(int)
    return df

def calcular_estatisticas_basicas(df, coluna_valor):
    """Calcula estatísticas básicas de uma coluna"""
    return {
        'total': df[coluna_valor].sum(),
        'media': df[coluna_valor].mean(),
        'mediana': df[coluna_valor].median(),
        'desvio': df[coluna_valor].std(),
        'min': df[coluna_valor].min(),
        'max': df[coluna_valor].max()
    }

def agrupar_por_categoria(df, coluna_categoria, coluna_valor='PA_VALAPR', incluir_contagem=True):
    """Agrupa dados por categoria"""
    agg_dict = {coluna_valor: 'sum'}
    if incluir_contagem:
        agg_dict['quantidade'] = (coluna_categoria, 'count')
    
    resultado = df.groupby(coluna_categoria).agg(**agg_dict).reset_index()
    return resultado.sort_values(coluna_valor, ascending=False)

def identificar_picos_quedas(df, coluna_valor, num_desvios=1):
    """Identifica picos e quedas em uma série temporal"""
    media = df[coluna_valor].mean()
    desvio = df[coluna_valor].std()
    
    limite_superior = media + (num_desvios * desvio)
    limite_inferior = media - (num_desvios * desvio)
    
    picos = df[df[coluna_valor] > limite_superior].copy()
    quedas = df[df[coluna_valor] < limite_inferior].copy()
    
    return {
        'media': media,
        'desvio': desvio,
        'limite_superior': limite_superior,
        'limite_inferior': limite_inferior,
        'picos': picos,
        'quedas': quedas
    }

def calcular_periodos_recentes(df, coluna_data):
    """Calcula subconjuntos de dados para períodos recentes"""
    data_recente = df[coluna_data].max()
    
    return {
        'ultimo_mes': df[df[coluna_data] >= data_recente - timedelta(days=30)],
        'ultimo_trimestre': df[df[coluna_data] >= data_recente - timedelta(days=90)],
        'ultimo_ano': df[df[coluna_data] >= data_recente - timedelta(days=365)]
    }

def truncar_texto(texto, tamanho=50):
    """Trunca texto se exceder tamanho"""
    if pd.isna(texto):
        return "Não informado"
    texto = str(texto)
    return texto if len(texto) <= tamanho else texto[:tamanho-3] + '...'