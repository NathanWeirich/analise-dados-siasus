"""
Análise de Produção por Estabelecimento de Saúde
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
    pasta_graficos = criar_diretorio('graficos/2_producao_estabelecimentos')
    
    imprimir_cabecalho("ANÁLISE: PRODUÇÃO POR ESTABELECIMENTO DE SAÚDE\nMUNICÍPIO: IJUÍ - RS", 60)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    df_estabelecimentos = carregar_estabelecimentos()
    
    # Padronizar CNES
    df = padronizar_codigo(df, 'PA_CODUNI', tamanho=7)
    
    # ========== ANÁLISE 1: RANKING DE PRODUÇÃO ==========
    imprimir_subcabecalho("RANKING DE PRODUÇÃO DOS ESTABELECIMENTOS", 60)
    
    # Agrupar por estabelecimento
    producao_estab = df.groupby('PA_CODUNI').agg({
        'PA_QTDAPR': 'sum',
        'PA_QTDPRO': 'sum'
    }).reset_index()
    
    producao_estab.columns = ['cnes', 'aprovados', 'produzidos']
    
    # Calcular métricas
    producao_estab['taxa_producao'] = (producao_estab['produzidos'] / producao_estab['aprovados'] * 100)
    producao_estab['diferenca'] = producao_estab['produzidos'] - producao_estab['aprovados']
    
    # Adicionar informações dos estabelecimentos
    producao_com_nome = adicionar_descricoes(
        producao_estab, df_estabelecimentos,
        'cnes', 'cnes', 'fantasia'
    )
    
    # Adicionar razão social como fallback
    producao_com_nome = producao_com_nome.merge(
        df_estabelecimentos[['cnes', 'raz_soci', 'bairro']],
        on='cnes', how='left', suffixes=('', '_extra')
    )
    
    # Ordenar por produzidos
    producao_com_nome = producao_com_nome.sort_values('produzidos', ascending=False)
    
    print(f"\nTotal de estabelecimentos: {len(producao_com_nome)}")
    print("\nTop 15 Estabelecimentos por Volume de Produção:")
    print("-" * 120)
    print(f"{'#':<3} {'CNES':<10} {'Nome':<45} {'Aprovados':>12} {'Produzidos':>12} {'Taxa':>8} {'Diferença':>12}")
    print("-" * 120)
    
    for idx, (_, row) in enumerate(producao_com_nome.head(15).iterrows(), 1):
        nome = row['fantasia'] if pd.notna(row['fantasia']) else row['raz_soci'] if pd.notna(row['raz_soci']) else 'Nome não encontrado'
        nome = truncar_texto(nome, 45)
        
        print(f"{idx:<3} {row['cnes']:<10} {nome:<45} {row['aprovados']:>12,} {row['produzidos']:>12,} {row['taxa_producao']:>7.1f}% {row['diferenca']:>12,}")
    
    # ========== ANÁLISE 2: COMPARAÇÃO GERAL ==========
    imprimir_subcabecalho("COMPARAÇÃO: APROVADOS VS PRODUZIDOS", 60)
    
    total_aprovados = producao_com_nome['aprovados'].sum()
    total_produzidos = producao_com_nome['produzidos'].sum()
    taxa_geral = (total_produzidos / total_aprovados * 100)
    
    print(f"\nTotal Geral:")
    print(f"   Aprovados:  {total_aprovados:,}")
    print(f"   Produzidos: {total_produzidos:,}")
    print(f"   Taxa Geral: {taxa_geral:.2f}%")
    print(f"   Diferença:  {total_produzidos - total_aprovados:,}")
    
    # ========== ANÁLISE 3: AVALIAÇÃO DA TAXA DE PRODUÇÃO ==========
    imprimir_subcabecalho("AVALIAÇÃO DA TAXA DE PRODUÇÃO", 60)
    
    taxa_media = producao_com_nome['taxa_producao'].mean()
    taxa_mediana = producao_com_nome['taxa_producao'].median()
    
    print(f"\nEstatísticas das Taxas de Produção:")
    print(f"   Média:   {taxa_media:.2f}%")
    print(f"   Mediana: {taxa_mediana:.2f}%")
    
    # Estabelecimentos com baixa taxa (<80%)
    baixa_producao = producao_com_nome[producao_com_nome['taxa_producao'] < 80].sort_values('produzidos', ascending=False)
    
    if not baixa_producao.empty:
        print(f"\nEstabelecimentos com taxa < 80% ({len(baixa_producao)} estabelecimentos):")
        print("-" * 110)
        print(f"{'Nome':<45} {'Taxa':>8} {'Aprovados':>12} {'Produzidos':>12} {'Diferença':>12}")
        print("-" * 110)
        for _, row in baixa_producao.head(10).iterrows():
            nome = row['fantasia'] if pd.notna(row['fantasia']) else row['raz_soci'] if pd.notna(row['raz_soci']) else 'Nome não encontrado'
            nome = truncar_texto(nome, 45)
            print(f"{nome:<45} {row['taxa_producao']:>7.1f}% {row['aprovados']:>12,} {row['produzidos']:>12,} {row['diferenca']:>12,}")
    
    # Estabelecimentos com alta taxa (>100%)
    alta_producao = producao_com_nome[producao_com_nome['taxa_producao'] > 100].sort_values('produzidos', ascending=False)
    
    if not alta_producao.empty:
        print(f"\nEstabelecimentos com taxa > 100% ({len(alta_producao)} estabelecimentos):")
        print("-" * 110)
        print(f"{'Nome':<45} {'Taxa':>8} {'Aprovados':>12} {'Produzidos':>12} {'Diferença':>12}")
        print("-" * 110)
        for _, row in alta_producao.head(10).iterrows():
            nome = row['fantasia'] if pd.notna(row['fantasia']) else row['raz_soci'] if pd.notna(row['raz_soci']) else 'Nome não encontrado'
            nome = truncar_texto(nome, 45)
            print(f"{nome:<45} {row['taxa_producao']:>7.1f}% {row['aprovados']:>12,} {row['produzidos']:>12,} {row['diferenca']:>12,}")
    
    # Taxa ideal (90-110%)
    taxa_ideal = producao_com_nome[(producao_com_nome['taxa_producao'] >= 90) & 
                                   (producao_com_nome['taxa_producao'] <= 110)]
    
    if not taxa_ideal.empty:
        print(f"\nEstabelecimentos com taxa ideal (90-110%): {len(taxa_ideal)} estabelecimentos")
    
    # ========== GRÁFICOS ==========
    
    # Gráfico 1: Ranking - Aprovados vs Produzidos
    top15 = producao_com_nome.head(15)
    labels = [truncar_texto(row['fantasia'] if pd.notna(row['fantasia']) else row['raz_soci'], 35) 
              for _, row in top15.iterrows()]
    
    criar_grafico_barras_horizontal_agrupadas(
        labels,
        top15['aprovados'].values,
        top15['produzidos'].values,
        'Aprovados',
        'Produzidos',
        'Top 15 Estabelecimentos - Aprovados vs Produzidos',
        f'{pasta_graficos}/ranking_producao.png'
    )
    
    # Gráfico 2: Taxa de Produção
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(14, 8))
    
    # Cores baseadas na taxa
    cores = ['green' if 90 <= taxa <= 110 else 'orange' if taxa >= 80 else 'red' 
             for taxa in top15['taxa_producao']]
    
    plt.barh(range(len(top15)), top15['taxa_producao'], color=cores, alpha=0.7)
    plt.yticks(range(len(top15)), labels, fontsize=9)
    plt.axvline(x=100, color='blue', linestyle='--', linewidth=2, label='Meta 100%')
    plt.axvline(x=taxa_media, color='black', linestyle='--', linewidth=2, 
                label=f'Média ({taxa_media:.1f}%)')
    
    plt.xlabel('Taxa de Produção (%)', fontsize=12)
    plt.ylabel('Estabelecimento', fontsize=12)
    plt.title('Taxa de Produção dos Top 15 Estabelecimentos', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(axis='x', alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/taxa_producao.png')
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 60)

if __name__ == "__main__":
    main()