"""
Análise de Fluxos Regionais e Acesso aos Serviços
Município: Ijuí - RS
"""

import sys
from pathlib import Path
import warnings

# Suprimir warnings do pandas
warnings.filterwarnings('ignore', category=UserWarning)

# Adicionar pasta raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils import *

CODIGO_IJUI = '431020'

def main():
    # Configuração inicial
    configurar_estilo_graficos()
    pasta_graficos = criar_diretorio('graficos/4_fluxos_regionais_acessos')
    
    imprimir_cabecalho("FLUXOS REGIONAIS E ACESSO AOS SERVIÇOS DE SAÚDE", 80)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    df_municipios = carregar_municipios()
    df_estabelecimentos = carregar_estabelecimentos()
    
    # Padronizar códigos
    df = padronizar_codigo(df, 'PA_CODUNI', tamanho=7)
    df = padronizar_codigo(df, 'PA_MUNPCN', tamanho=6)
    
    # Adicionar informações dos municípios
    df = adicionar_descricoes(df, df_municipios, 'PA_MUNPCN', 'co_municip', 'ds_nome')
    
    # Adicionar informações dos estabelecimentos
    df = adicionar_descricoes(df, df_estabelecimentos, 'PA_CODUNI', 'cnes', 'fantasia')
    
    # Identificar origem (Ijuí ou outros)
    df['origem_ijui'] = df['PA_MUNPCN'] == CODIGO_IJUI
    
    # ========== ANÁLISE 1: MUNICÍPIOS DE ORIGEM ==========
    imprimir_subcabecalho("MUNICÍPIOS DE ORIGEM DOS PACIENTES", 80)
    
    origem_counts = df.groupby(['PA_MUNPCN', 'ds_nome']).size().reset_index(name='quantidade')
    origem_counts = origem_counts.sort_values('quantidade', ascending=False)
    
    print(f"\nTotal de atendimentos: {len(df):,}")
    print(f"Total de municípios distintos: {df['PA_MUNPCN'].nunique():,}\n")
    
    print("Top 20 municípios de origem:")
    for idx, (_, row) in enumerate(origem_counts.head(20).iterrows(), 1):
        nome = row['ds_nome'] if pd.notna(row['ds_nome']) else 'Nome não encontrado'
        perc = (row['quantidade'] / len(df)) * 100
        marcador = "*" if row['PA_MUNPCN'] == CODIGO_IJUI else " "
        print(f"{marcador} {idx:2}. {nome:<30} ({row['PA_MUNPCN']}): {row['quantidade']:>7,} ({perc:>5.2f}%)")
    
    # ========== ANÁLISE 2: ATENDIMENTOS POR ORIGEM ==========
    imprimir_subcabecalho("ATENDIMENTOS POR ORIGEM (IJUÍ vs OUTROS MUNICÍPIOS)", 80)
    
    atend_ijui = df[df['origem_ijui']].shape[0]
    atend_outros = df[~df['origem_ijui']].shape[0]
    total_atend = len(df)
    
    perc_ijui = (atend_ijui / total_atend) * 100
    perc_outros = (atend_outros / total_atend) * 100
    
    print(f"\nAtendimentos de moradores de Ijuí: {atend_ijui:,} ({perc_ijui:.2f}%)")
    print(f"Atendimentos de outros municípios: {atend_outros:,} ({perc_outros:.2f}%)")
    
    # Gráfico 1: Pizza - Origem dos Pacientes
    criar_grafico_pizza(
        [atend_ijui, atend_outros],
        ['Ijuí', 'Outros Municípios'],
        'Origem dos Pacientes Atendidos',
        f'{pasta_graficos}/origem_pacientes.png',
        colors=['#3498db', '#e74c3c']
    )
    
    # ========== ANÁLISE 3: ESTABELECIMENTOS MAIS PROCURADOS ==========
    imprimir_subcabecalho("ESTABELECIMENTOS MAIS PROCURADOS", 80)
    
    estab_counts = df.groupby(['PA_CODUNI', 'fantasia']).size().reset_index(name='quantidade')
    estab_counts = estab_counts.sort_values('quantidade', ascending=False)
    
    print("\nTop 10 estabelecimentos:")
    for idx, (_, row) in enumerate(estab_counts.head(10).iterrows(), 1):
        nome = truncar_texto(row['fantasia'], 50) if pd.notna(row['fantasia']) else 'Nome não encontrado'
        perc = (row['quantidade'] / len(df)) * 100
        print(f"{idx:2}. {nome:<50} {row['quantidade']:>7,} ({perc:>5.2f}%)")
    
    # Gráfico 2: Top 10 Estabelecimentos
    top10_estab = estab_counts.head(10)
    labels = [truncar_texto(row['fantasia'], 40) if pd.notna(row['fantasia']) else 'Sem nome'
              for _, row in top10_estab.iterrows()]
    
    criar_grafico_barras_horizontal(
        top10_estab['quantidade'].values,
        labels,
        'Top 10 Estabelecimentos Mais Procurados',
        'Quantidade de Atendimentos',
        f'{pasta_graficos}/top_estabelecimentos.png',
        color='steelblue'
    )
    
    # ========== ANÁLISE 4: FLUXO POR ESTABELECIMENTO E ORIGEM ==========
    imprimir_subcabecalho("FLUXO POR ESTABELECIMENTO E ORIGEM", 80)
    
    # Top 5 estabelecimentos - analisar origem
    top5_estab_cnes = estab_counts.head(5)['PA_CODUNI'].tolist()
    
    print("\nDistribuição Ijuí vs Outros nos Top 5 estabelecimentos:")
    print("-" * 90)
    print(f"{'Estabelecimento':<50} {'Ijuí':>10} {'Outros':>10} {'Total':>10}")
    print("-" * 90)
    
    for cnes in top5_estab_cnes:
        df_estab = df[df['PA_CODUNI'] == cnes]
        nome = df_estab['fantasia'].iloc[0] if pd.notna(df_estab['fantasia'].iloc[0]) else 'Sem nome'
        nome = truncar_texto(nome, 50)
        
        ijui_count = df_estab[df_estab['origem_ijui']].shape[0]
        outros_count = df_estab[~df_estab['origem_ijui']].shape[0]
        total = len(df_estab)
        
        print(f"{nome:<50} {ijui_count:>10,} {outros_count:>10,} {total:>10,}")
    
    # ========== ANÁLISE 5: TOP MUNICÍPIOS EXTERNOS ==========
    imprimir_subcabecalho("MUNICÍPIOS EXTERNOS QUE MAIS UTILIZAM IJUÍ", 80)
    
    df_externos = df[~df['origem_ijui']]
    externos_counts = df_externos.groupby(['PA_MUNPCN', 'ds_nome']).size().reset_index(name='quantidade')
    externos_counts = externos_counts.sort_values('quantidade', ascending=False)
    
    print("\nTop 15 municípios externos:")
    for idx, (_, row) in enumerate(externos_counts.head(15).iterrows(), 1):
        nome = row['ds_nome'] if pd.notna(row['ds_nome']) else 'Nome não encontrado'
        perc = (row['quantidade'] / len(df_externos)) * 100
        print(f"{idx:2}. {nome:<30} ({row['PA_MUNPCN']}): {row['quantidade']:>6,} ({perc:>5.2f}%)")
    
    # Gráfico 3: Top 10 Municípios Externos
    top10_externos = externos_counts.head(10)
    labels = [row['ds_nome'] if pd.notna(row['ds_nome']) else 'Não informado'
              for _, row in top10_externos.iterrows()]
    
    criar_grafico_barras_horizontal(
        top10_externos['quantidade'].values,
        labels,
        'Top 10 Municípios Externos que Mais Utilizam Ijuí',
        'Quantidade de Atendimentos',
        f'{pasta_graficos}/top_municipios_externos.png',
        color='#e74c3c'
    )
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 80)

if __name__ == "__main__":
    main()