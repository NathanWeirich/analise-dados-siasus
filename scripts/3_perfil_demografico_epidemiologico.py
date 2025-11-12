"""
Análise do Perfil Demográfico e Epidemiológico
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

def preparar_faixas_etarias(df):
    """Cria faixas etárias de 5 em 5 anos"""
    bins = list(range(0, 101, 5)) + [150]
    labels = [f'{i}-{i+4}' for i in range(0, 100, 5)] + ['100+']
    df['Faixa_Etaria'] = pd.cut(df['PA_IDADE'], bins=bins, labels=labels, right=False)
    return df

def preparar_sexo(df):
    """Mapeia valores de sexo"""
    sexo_map = {'M': 'Masculino', 'F': 'Feminino', 0: 'Não Informado', '0': 'Não Informado'}
    df['Sexo_Label'] = df['PA_SEXO'].map(sexo_map)
    return df

def main():
    # Configuração inicial
    configurar_estilo_graficos()
    pasta_graficos = criar_diretorio('graficos/3_perfil_demografico_epidemiologico')
    
    imprimir_cabecalho("PERFIL DEMOGRÁFICO E EPIDEMIOLÓGICO DA POPULAÇÃO ATENDIDA", 80)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    
    # Preparar dados
    df = preparar_sexo(df)
    df = preparar_faixas_etarias(df)
    
    # ========== ANÁLISE 1: DISTRIBUIÇÃO POR SEXO ==========
    imprimir_subcabecalho("DISTRIBUIÇÃO POR SEXO", 80)
    
    sexo_counts = df['Sexo_Label'].value_counts()
    sexo_percentual = df['Sexo_Label'].value_counts(normalize=True) * 100
    
    print(f"\nTotal de registros: {len(df):,}")
    print("\nDistribuição:")
    for sexo, count in sexo_counts.items():
        perc = sexo_percentual[sexo]
        print(f"  {sexo}: {count:,} ({perc:.2f}%)")
    
    # Gráfico 1: Pizza - Distribuição por Sexo
    criar_grafico_pizza(
        sexo_counts.values,
        sexo_counts.index.tolist(),
        'Distribuição por Sexo',
        f'{pasta_graficos}/01_distribuicao_sexo.png',
        colors=['#3498db', '#e74c3c', '#95a5a6']
    )
    
    # ========== ANÁLISE 2: DISTRIBUIÇÃO POR FAIXA ETÁRIA ==========
    imprimir_subcabecalho("DISTRIBUIÇÃO POR FAIXA ETÁRIA (5 em 5 anos)", 80)
    
    faixa_etaria_counts = df['Faixa_Etaria'].value_counts().sort_index()
    faixa_etaria_percentual = df['Faixa_Etaria'].value_counts(normalize=True).sort_index() * 100
    
    print("\nDistribuição por faixa etária:")
    for faixa, count in faixa_etaria_counts.items():
        perc = faixa_etaria_percentual[faixa]
        print(f"  {faixa} anos: {count:,} ({perc:.2f}%)")
    
    # Gráfico 2: Barras - Distribuição por Faixa Etária
    criar_grafico_barras_vertical(
        faixa_etaria_counts.index.tolist(),
        faixa_etaria_counts.values,
        'Distribuição por Faixa Etária (5 em 5 anos)',
        'Quantidade',
        f'{pasta_graficos}/02_distribuicao_faixa_etaria.png',
        color='#2ecc71'
    )
    
    # ========== ANÁLISE 3: ESTATÍSTICAS DESCRITIVAS DA IDADE ==========
    imprimir_subcabecalho("ESTATÍSTICAS DESCRITIVAS DA IDADE", 80)
    
    stats_idade = calcular_estatisticas_basicas(df, 'PA_IDADE')
    
    print(f"\nIdade média: {stats_idade['media']:.2f} anos")
    print(f"Mediana: {stats_idade['mediana']:.2f} anos")
    print(f"Desvio padrão: {stats_idade['desvio']:.2f} anos")
    print(f"Idade mínima: {stats_idade['min']:.0f} anos")
    print(f"Idade máxima: {stats_idade['max']:.0f} anos")
    
    print("\nIdade média por sexo:")
    idade_por_sexo = df.groupby('Sexo_Label')['PA_IDADE'].mean()
    for sexo, idade_media in idade_por_sexo.items():
        print(f"  {sexo}: {idade_media:.2f} anos")
    
    # ========== ANÁLISE 4: SEXO POR FAIXA ETÁRIA ==========
    imprimir_subcabecalho("DISTRIBUIÇÃO POR SEXO E FAIXA ETÁRIA", 80)
    
    # Gráfico 3: Barras agrupadas - Sexo por Faixa Etária
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(14, 8))
    crosstab_plot = pd.crosstab(df['Faixa_Etaria'], df['Sexo_Label'])
    crosstab_plot.plot(kind='bar', color=['#3498db', '#95a5a6', '#e74c3c'])
    plt.title('Distribuição por Sexo e Faixa Etária', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Faixa Etária (anos)', fontsize=12)
    plt.ylabel('Quantidade', fontsize=12)
    plt.legend(title='Sexo', fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/03_sexo_faixa_etaria.png')
    
    # ========== ANÁLISE 5: IDENTIFICAR GRUPOS PREDOMINANTES ==========
    imprimir_subcabecalho("GRUPOS PREDOMINANTES", 80)
    
    # Top 5 faixas etárias - CORRIGIDO: ordenar por quantidade
    faixa_etaria_por_qtd = df['Faixa_Etaria'].value_counts()  # Já ordena por quantidade decrescente
    top5_faixas = faixa_etaria_por_qtd.head(5)
    
    print("\nTop 5 Faixas Etárias mais atendidas:")
    for i, (faixa, count) in enumerate(top5_faixas.items(), 1):
        perc = (count / len(df)) * 100
        print(f"  {i}. {faixa} anos: {count:,} ({perc:.2f}%)")
    
    # Distribuição por sexo nas top 5 faixas
    print("\nDistribuição por sexo nas faixas etárias predominantes:")
    for faixa in top5_faixas.index[:3]:  # Top 3 apenas para detalhar
        df_faixa = df[df['Faixa_Etaria'] == faixa]
        sexo_dist = df_faixa['Sexo_Label'].value_counts()
        print(f"\n  {faixa} anos:")
        for sexo, count in sexo_dist.items():
            perc = (count / len(df_faixa)) * 100
            print(f"    {sexo}: {count:,} ({perc:.2f}%)")
    
    imprimir_cabecalho("✓ ANÁLISE CONCLUÍDA!", 80)

if __name__ == "__main__":
    main()