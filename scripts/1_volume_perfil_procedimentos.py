"""
Análise de Volume e Perfil dos Procedimentos
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

def main():
    # Configuração inicial
    configurar_estilo_graficos()
    pasta_graficos = criar_diretorio('graficos/1_volume_perfil_procedimentos')
    
    imprimir_cabecalho("ANÁLISE: VOLUME E PERFIL DOS PROCEDIMENTOS\nMUNICÍPIO: IJUÍ - RS", 60)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    df_procedimentos = carregar_procedimentos()
    df_dim_tempo = carregar_dim_tempo()
    
    # Preparar dados temporais
    df = preparar_temporal(df)
    
    data_recente = df['PA_CMP'].max()
    data_antiga = df['PA_CMP'].min()
    
    # ========== ANÁLISE 1: VOLUME POR PERÍODOS ==========
    imprimir_subcabecalho("VOLUME DE PROCEDIMENTOS", 60)
    
    print(f"Período: {data_antiga:%d-%m-%Y} a {data_recente:%d-%m-%Y}\n")
    
    periodos = calcular_periodos_recentes(df, 'PA_CMP')
    
    print(f"Último mês:      {len(periodos['ultimo_mes']):>10,} procedimentos")
    print(f"Último trimestre: {len(periodos['ultimo_trimestre']):>10,} procedimentos")
    print(f"Último ano:      {len(periodos['ultimo_ano']):>10,} procedimentos")
    print(f"Total:           {len(df):>10,} procedimentos")
    
    # ========== ANÁLISE 2: DISTRIBUIÇÃO POR PROCEDIMENTO ==========
    imprimir_subcabecalho("DISTRIBUIÇÃO POR PROCEDIMENTO", 60)
    
    # Padronizar código
    df = padronizar_codigo(df, 'PA_PROC_ID')
    
    # Agrupar por procedimento
    dist_proc = df.groupby('PA_PROC_ID').size().reset_index(name='quantidade')
    dist_proc = dist_proc.sort_values('quantidade', ascending=False)
    
    # Adicionar descrições
    dist_proc = adicionar_descricoes(
        dist_proc, df_procedimentos, 
        'PA_PROC_ID', 'ip_cod_padrao', 'ip_dscr'
    )
    
    # Exibir top 15
    print(f"\nTotal de procedimentos diferentes: {len(dist_proc)}\n")
    print("Top 15 Procedimentos:")
    print("-" * 60)
    
    for i, (_, row) in enumerate(dist_proc.head(15).iterrows(), 1):
        perc = (row['quantidade']/len(df)*100)
        desc = row['ip_dscr'] if pd.notna(row['ip_dscr']) else 'Descrição não encontrada'
        print(f"{i:2}. {row['PA_PROC_ID']}: {row['quantidade']:,} ({perc:.2f}%)")
        print(f"    {truncar_texto(desc, 55)}")
    
    # Gráfico 1: Top 15 Procedimentos
    top15 = dist_proc.head(15)
    labels = [f"{row['PA_PROC_ID']} - {truncar_texto(row['ip_dscr'], 50)}" 
             for _, row in top15.iterrows()]
    
    criar_grafico_barras_horizontal(
        top15['quantidade'].values,
        labels,
        'Top 15 Procedimentos Ambulatoriais em Ijuí',
        'Quantidade',
        f'{pasta_graficos}/distribuicao_especialidades.png',
        color='steelblue'
    )
    
    # ========== ANÁLISE 3: EVOLUÇÃO TEMPORAL ==========
    imprimir_subcabecalho("EVOLUÇÃO TEMPORAL", 60)
    
    # Merge com dimensão tempo
    df_temporal = df.merge(df_dim_tempo, on='anomes', how='left', suffixes=('', '_dim'))
    
    # Evolução mensal (remover duplicatas)
    evolucao_mensal = df_temporal.groupby(['ano_dim', 'mes', 'mesext']).size().reset_index(name='quantidade')
    evolucao_mensal = evolucao_mensal.sort_values(['ano_dim', 'mes']).drop_duplicates()
    
    print("\nÚltimos 12 meses:")
    print("-" * 60)
    for _, row in evolucao_mensal.tail(12).iterrows():
        ano_str = f"{int(row['ano_dim'])}"
        print(f"  {row['mesext']}/{ano_str}: {row['quantidade']:>8,} procedimentos")
    
    # Evolução trimestral
    evolucao_trimestral = df_temporal.groupby(['anotri', 'triex_t']).size().reset_index(name='quantidade')
    evolucao_trimestral = evolucao_trimestral.sort_values('anotri').drop_duplicates()
    
    print("\n\nÚltimos trimestres:")
    print("-" * 60)
    for _, row in evolucao_trimestral.tail(8).iterrows():
        print(f"  {row['triex_t']} ({row['anotri']}): {row['quantidade']:>8,} procedimentos")
    
    # Identificar picos e quedas
    analise_temporal = identificar_picos_quedas(evolucao_mensal, 'quantidade')
    
    imprimir_subcabecalho("PICOS E QUEDAS NA DEMANDA", 60)
    print(f"\nMédia mensal: {analise_temporal['media']:,.0f} procedimentos")
    print(f"Desvio padrão: {analise_temporal['desvio']:,.0f} procedimentos\n")
    
    if not analise_temporal['picos'].empty:
        print("PICOS (acima da média + 1 desvio padrão):")
        print("-" * 60)
        for _, row in analise_temporal['picos'].iterrows():
            var = ((row['quantidade']/analise_temporal['media'] - 1) * 100)
            ano_str = f"{int(row['ano_dim'])}"
            print(f"  {row['mesext']}/{ano_str}: {row['quantidade']:>8,} (+{var:.1f}%)")
    
    if not analise_temporal['quedas'].empty:
        print("\nQUEDAS (abaixo da média - 1 desvio padrão):")
        print("-" * 60)
        for _, row in analise_temporal['quedas'].iterrows():
            var = ((1 - row['quantidade']/analise_temporal['media']) * 100)
            ano_str = f"{int(row['ano_dim'])}"
            print(f"  {row['mesext']}/{ano_str}: {row['quantidade']:>8,} (-{var:.1f}%)")
    
    # Gráfico 2: Evolução Temporal
    evolucao_mensal['label_periodo'] = evolucao_mensal.apply(
        lambda row: f"{row['mesext'][:3]}/{str(int(row['ano_dim']))[-2:]}", axis=1
    )
    
    criar_grafico_linha_temporal(
        evolucao_mensal,
        'label_periodo',
        'quantidade',
        'Evolução Temporal dos Procedimentos Ambulatoriais',
        f'{pasta_graficos}/evolucao_temporal.png',
        media_linha=True,
        mostrar_limites=True
    )
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 60)

if __name__ == "__main__":
    main()