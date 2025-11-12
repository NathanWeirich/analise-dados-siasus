"""
Análise de Recursos Financeiros
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
    pasta_graficos = criar_diretorio('graficos/5_recursos_financeiros')
    
    imprimir_cabecalho("ANÁLISE DE RECURSOS FINANCEIROS", 80)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    df_procedimentos = carregar_procedimentos()
    df_dim_tempo = carregar_dim_tempo()
    
    # Padronizar código de procedimento
    df = padronizar_codigo(df, 'PA_PROC_ID')
    
    # ========== ANÁLISE 1: TOTAL DE VALORES APROVADOS E PRODUZIDOS ==========
    imprimir_subcabecalho("VALORES TOTAIS APROVADOS VS PRODUZIDOS", 80)
    
    total_aprovado = df['PA_VALAPR'].sum()
    total_produzido = df['PA_VALPRO'].sum()
    diferenca = total_produzido - total_aprovado
    percentual_diferenca = (diferenca / total_aprovado) * 100
    
    print(f"\nTotal de registros analisados: {len(df):,}")
    print(f"\nValor Total Aprovado (SUS): {formatar_valor_monetario(total_aprovado)}")
    print(f"Valor Total Produzido:      {formatar_valor_monetario(total_produzido)}")
    print(f"Diferença:                  {formatar_valor_monetario(diferenca)}")
    print(f"Percentual da diferença:    {percentual_diferenca:+.2f}%")
    
    if diferenca > 0:
        print(f"\nO valor produzido SUPEROU o valor aprovado em {formatar_valor_monetario(diferenca)}")
    elif diferenca < 0:
        print(f"\nO valor produzido ficou ABAIXO do aprovado em {formatar_valor_monetario(abs(diferenca))}")
    else:
        print("\nValores aprovado e produzido estão EQUILIBRADOS")
    
    # Gráfico 1: Comparação Aprovado vs Produzido
    criar_grafico_barras_vertical(
        ['Aprovado', 'Produzido'],
        [total_aprovado, total_produzido],
        'Valores Totais: Aprovado vs Produzido',
        'Valor (R$)',
        f'{pasta_graficos}/01_valores_totais.png',
        color='#3498db'
    )
    
    # ========== ANÁLISE 2: EVOLUÇÃO MENSAL DOS VALORES ==========
    imprimir_subcabecalho("EVOLUÇÃO MENSAL DOS VALORES", 80)
    
    # Preparar competência
    df = preparar_competencia(df)
    
    # Agrupar por competência
    evolucao_mensal = df.groupby('Competencia').agg({
        'PA_VALAPR': 'sum',
        'PA_VALPRO': 'sum',
        'PA_CODUNI': 'count'
    }).reset_index()
    
    evolucao_mensal.columns = ['Competencia', 'Valor_Aprovado', 'Valor_Produzido', 'Quantidade_Procedimentos']
    evolucao_mensal['Diferenca'] = evolucao_mensal['Valor_Produzido'] - evolucao_mensal['Valor_Aprovado']
    evolucao_mensal['Percentual_Diferenca'] = (evolucao_mensal['Diferenca'] / evolucao_mensal['Valor_Aprovado']) * 100
    
    print("\nEvolução por competência:")
    print("-" * 120)
    print(f"{'Competência':<12} {'Aprovado':>15} {'Produzido':>15} {'Diferença':>15} {'%':>8} {'Procedimentos':>15}")
    print("-" * 120)
    for _, row in evolucao_mensal.iterrows():
        print(f"{row['Competencia']:<12} {row['Valor_Aprovado']:>15,.2f} {row['Valor_Produzido']:>15,.2f} "
              f"{row['Diferenca']:>15,.2f} {row['Percentual_Diferenca']:>7.2f}% {row['Quantidade_Procedimentos']:>15,}")
    
    # Gráfico 2: Evolução Temporal dos Valores
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(16, 8))
    x = range(len(evolucao_mensal))
    
    plt.plot(x, evolucao_mensal['Valor_Aprovado'], marker='o', linewidth=2, 
             label='Aprovado', color='#3498db')
    plt.plot(x, evolucao_mensal['Valor_Produzido'], marker='s', linewidth=2, 
             label='Produzido', color='#2ecc71')
    
    plt.xticks(x, evolucao_mensal['Competencia'], rotation=45, ha='right')
    plt.xlabel('Competência', fontsize=12)
    plt.ylabel('Valor (R$)', fontsize=12)
    plt.title('Evolução Temporal dos Valores (Aprovado vs Produzido)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/02_evolucao_valores.png')
    
    # ========== ANÁLISE 3: GASTO MÉDIO POR PROCEDIMENTO ==========
    imprimir_subcabecalho("GASTO MÉDIO POR PROCEDIMENTO", 80)
    
    evolucao_mensal['Gasto_Medio_Aprovado'] = evolucao_mensal['Valor_Aprovado'] / evolucao_mensal['Quantidade_Procedimentos']
    evolucao_mensal['Gasto_Medio_Produzido'] = evolucao_mensal['Valor_Produzido'] / evolucao_mensal['Quantidade_Procedimentos']
    
    print("\nGasto médio por procedimento por mês:")
    print("-" * 80)
    print(f"{'Competência':<12} {'Gasto Médio Aprovado':>25} {'Gasto Médio Produzido':>25}")
    print("-" * 80)
    for _, row in evolucao_mensal.iterrows():
        print(f"{row['Competencia']:<12} {row['Gasto_Medio_Aprovado']:>24,.2f} {row['Gasto_Medio_Produzido']:>24,.2f}")
    
    gasto_medio_geral_aprovado = df['PA_VALAPR'].sum() / len(df)
    gasto_medio_geral_produzido = df['PA_VALPRO'].sum() / len(df)
    
    print(f"\nGASTO MÉDIO GERAL POR PROCEDIMENTO:")
    print(f"  Aprovado:  {formatar_valor_monetario(gasto_medio_geral_aprovado)}")
    print(f"  Produzido: {formatar_valor_monetario(gasto_medio_geral_produzido)}")
    
    # Gráfico 3: Gasto Médio Mensal
    plt.figure(figsize=(16, 6))
    
    plt.plot(x, evolucao_mensal['Gasto_Medio_Aprovado'], marker='o', linewidth=2, 
             label='Gasto Médio Aprovado', color='#3498db')
    plt.plot(x, evolucao_mensal['Gasto_Medio_Produzido'], marker='s', linewidth=2, 
             label='Gasto Médio Produzido', color='#2ecc71')
    
    plt.axhline(y=gasto_medio_geral_aprovado, color='blue', linestyle='--', 
                linewidth=1, alpha=0.7, label='Média Geral Aprovado')
    plt.axhline(y=gasto_medio_geral_produzido, color='green', linestyle='--', 
                linewidth=1, alpha=0.7, label='Média Geral Produzido')
    
    plt.xticks(x, evolucao_mensal['Competencia'], rotation=45, ha='right')
    plt.xlabel('Competência', fontsize=12)
    plt.ylabel('Gasto Médio (R$)', fontsize=12)
    plt.title('Evolução do Gasto Médio por Procedimento', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/03_gasto_medio.png')
    
    # ========== ANÁLISE 4: TOP PROCEDIMENTOS MAIS CAROS ==========
    imprimir_subcabecalho("TOP 10 PROCEDIMENTOS MAIS CAROS", 80)
    
    # Agrupar por procedimento
    custo_por_proc = df.groupby('PA_PROC_ID').agg({
        'PA_VALAPR': 'sum',
        'PA_VALPRO': 'sum',
        'PA_CODUNI': 'count'
    }).reset_index()
    
    custo_por_proc.columns = ['PA_PROC_ID', 'Total_Aprovado', 'Total_Produzido', 'Quantidade']
    custo_por_proc['Custo_Medio_Aprovado'] = custo_por_proc['Total_Aprovado'] / custo_por_proc['Quantidade']
    custo_por_proc = custo_por_proc.sort_values('Total_Aprovado', ascending=False)
    
    # Adicionar descrições
    custo_por_proc = adicionar_descricoes(
        custo_por_proc, df_procedimentos,
        'PA_PROC_ID', 'ip_cod_padrao', 'ip_dscr'
    )
    
    print("\nTop 10 Procedimentos pelo Valor Total Aprovado:")
    print("-" * 130)
    print(f"{'#':<3} {'Código':<12} {'Descrição':<50} {'Total Aprovado':>18} {'Quantidade':>12} {'Custo Médio':>15}")
    print("-" * 130)
    
    for idx, (_, row) in enumerate(custo_por_proc.head(10).iterrows(), 1):
        desc = truncar_texto(row['ip_dscr'], 50) if pd.notna(row['ip_dscr']) else 'Descrição não encontrada'
        print(f"{idx:<3} {row['PA_PROC_ID']:<12} {desc:<50} {row['Total_Aprovado']:>18,.2f} "
              f"{row['Quantidade']:>12,} {row['Custo_Medio_Aprovado']:>15,.2f}")
    
    # Gráfico 4: Top 10 Procedimentos Mais Caros
    top10_caros = custo_por_proc.head(10)
    labels = [f"{row['PA_PROC_ID'][:6]}... - {truncar_texto(row['ip_dscr'], 30)}" 
              for _, row in top10_caros.iterrows()]
    
    criar_grafico_barras_horizontal(
        top10_caros['Total_Aprovado'].values,
        labels,
        'Top 10 Procedimentos Mais Caros (Valor Total Aprovado)',
        'Valor Total (R$)',
        f'{pasta_graficos}/04_top10_procedimentos_caros.png',
        color='#e74c3c'
    )
    
    # ========== ANÁLISE 5: DISTRIBUIÇÃO DE VALORES ==========
    imprimir_subcabecalho("DISTRIBUIÇÃO DE VALORES POR FAIXA", 80)
    
    # Criar faixas de valor
    faixas = [0, 10, 50, 100, 500, 1000, float('inf')]
    labels_faixas = ['Até R$ 10', 'R$ 10-50', 'R$ 50-100', 'R$ 100-500', 'R$ 500-1000', 'Acima R$ 1000']
    
    df['Faixa_Valor'] = pd.cut(df['PA_VALAPR'], bins=faixas, labels=labels_faixas, right=False)
    
    dist_faixas = df.groupby('Faixa_Valor', observed=True).agg({
        'PA_VALAPR': 'sum',
        'PA_CODUNI': 'count'
    }).reset_index()
    
    dist_faixas.columns = ['Faixa', 'Total_Valor', 'Quantidade']
    dist_faixas['Percentual_Valor'] = (dist_faixas['Total_Valor'] / total_aprovado) * 100
    dist_faixas['Percentual_Qtd'] = (dist_faixas['Quantidade'] / len(df)) * 100
    
    print("\nDistribuição por faixa de valor:")
    print("-" * 100)
    print(f"{'Faixa':<20} {'Total Valor':>18} {'% Valor':>10} {'Quantidade':>12} {'% Qtd':>10}")
    print("-" * 100)
    
    for _, row in dist_faixas.iterrows():
        print(f"{row['Faixa']:<20} {row['Total_Valor']:>18,.2f} {row['Percentual_Valor']:>9.2f}% "
              f"{row['Quantidade']:>12,} {row['Percentual_Qtd']:>9.2f}%")
    
    # Gráfico 5: Distribuição por Faixa de Valor
    criar_grafico_pizza(
        dist_faixas['Total_Valor'].values,
        dist_faixas['Faixa'].tolist(),
        'Distribuição do Valor Total por Faixa de Preço',
        f'{pasta_graficos}/05_distribuicao_faixas.png',
        colors=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c']
    )
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 80)

if __name__ == "__main__":
    main()