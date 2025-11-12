"""
Análise de Comparações e Tendências Regionais
Comparação entre Ijuí, Santa Rosa e Cruz Alta - RS
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
import matplotlib.pyplot as plt

def carregar_dados_municipios():
    """Carrega dados dos três municípios"""
    df_ijui = carregar_csv('dados_limpos.csv')
    df_ijui['Municipio'] = 'Ijuí'
    
    df_sr = carregar_csv('dados_limpos_sr.csv')
    df_sr['Municipio'] = 'Santa Rosa'
    
    df_ca = carregar_csv('dados_limpos_ca.csv')
    df_ca['Municipio'] = 'Cruz Alta'
    
    return df_ijui, df_sr, df_ca

def preparar_dados_comparacao(df_ijui, df_sr, df_ca):
    """Prepara e combina dados para comparação"""
    # Combinar todos os dados
    df_completo = pd.concat([df_ijui, df_sr, df_ca], ignore_index=True)
    
    # Preparar competência para todos
    df_completo = preparar_competencia(df_completo)
    
    # Padronizar código de procedimento
    df_completo = padronizar_codigo(df_completo, 'PA_PROC_ID')
    
    return df_completo

def analisar_volume_comparativo(df_completo, pasta_graficos):
    """Análise comparativa de volume entre municípios"""
    imprimir_subcabecalho("VOLUME COMPARATIVO DE PROCEDIMENTOS", 80)
    
    volume_por_municipio = df_completo.groupby('Municipio').size().reset_index(name='quantidade')
    volume_por_municipio = volume_por_municipio.sort_values('quantidade', ascending=False)
    
    print("\nVolume total de procedimentos:")
    print("-" * 60)
    for _, row in volume_por_municipio.iterrows():
        perc = (row['quantidade'] / len(df_completo)) * 100
        print(f"  {row['Municipio']:<15}: {row['quantidade']:>10,} ({perc:>5.2f}%)")
    
    # Gráfico: Volume comparativo
    criar_grafico_barras_vertical(
        volume_por_municipio['Municipio'].tolist(),
        volume_por_municipio['quantidade'].values,
        'Volume Total de Procedimentos por Município',
        'Quantidade',
        f'{pasta_graficos}/01_volume_comparativo.png',
        color='#3498db'
    )
    
    return volume_por_municipio

def analisar_evolucao_temporal_comparativa(df_completo, pasta_graficos):
    """Análise da evolução temporal comparativa"""
    imprimir_subcabecalho("EVOLUÇÃO TEMPORAL COMPARATIVA", 80)
    
    # Evolução mensal por município
    evolucao = df_completo.groupby(['Competencia', 'Municipio']).size().reset_index(name='quantidade')
    evolucao = evolucao.sort_values(['Competencia', 'Municipio'])
    
    # Calcular média mensal por município
    media_mensal = evolucao.groupby('Municipio')['quantidade'].mean()
    
    print("\nMédia mensal de procedimentos:")
    print("-" * 60)
    for municipio, media in media_mensal.items():
        print(f"  {municipio:<15}: {media:>10,.0f} procedimentos/mês")
    
    # Gráfico: Evolução temporal
    plt.figure(figsize=(16, 8))
    
    cores = {'Ijuí': '#3498db', 'Santa Rosa': '#e74c3c', 'Cruz Alta': '#2ecc71'}
    
    for municipio in evolucao['Municipio'].unique():
        dados_mun = evolucao[evolucao['Municipio'] == municipio]
        plt.plot(dados_mun['Competencia'], dados_mun['quantidade'], 
                marker='o', linewidth=2, label=municipio, color=cores.get(municipio, '#95a5a6'))
    
    plt.xlabel('Competência', fontsize=12)
    plt.ylabel('Quantidade de Procedimentos', fontsize=12)
    plt.title('Evolução Temporal Comparativa dos Procedimentos', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/02_evolucao_temporal_comparativa.png')
    
    return evolucao

def calcular_taxa_crescimento(evolucao):
    """Calcula taxa de crescimento para cada município"""
    imprimir_subcabecalho("TAXA DE CRESCIMENTO", 80)
    
    print("\nTaxa de crescimento (primeiro vs último mês):")
    print("-" * 80)
    
    taxas = {}
    
    for municipio in evolucao['Municipio'].unique():
        dados_mun = evolucao[evolucao['Municipio'] == municipio].sort_values('Competencia')
        
        if len(dados_mun) >= 2:
            primeiro = dados_mun.iloc[0]['quantidade']
            ultimo = dados_mun.iloc[-1]['quantidade']
            
            crescimento_abs = ultimo - primeiro
            crescimento_perc = ((ultimo / primeiro) - 1) * 100 if primeiro > 0 else 0
            
            taxas[municipio] = {
                'primeiro': primeiro,
                'ultimo': ultimo,
                'crescimento_abs': crescimento_abs,
                'crescimento_perc': crescimento_perc
            }
            
            print(f"\n  {municipio}:")
            print(f"    Primeiro mês: {primeiro:,} procedimentos")
            print(f"    Último mês:   {ultimo:,} procedimentos")
            print(f"    Crescimento:  {crescimento_abs:+,} ({crescimento_perc:+.2f}%)")
    
    return taxas

def analisar_valores_comparativos(df_completo, pasta_graficos):
    """Análise comparativa de valores financeiros"""
    imprimir_subcabecalho("VALORES FINANCEIROS COMPARATIVOS", 80)
    
    valores = df_completo.groupby('Municipio').agg({
        'PA_VALAPR': 'sum',
        'PA_VALPRO': 'sum'
    }).reset_index()
    
    valores.columns = ['Municipio', 'Valor_Aprovado', 'Valor_Produzido']
    valores['Valor_Medio_Proc'] = valores['Valor_Aprovado'] / df_completo.groupby('Municipio').size().values
    valores = valores.sort_values('Valor_Aprovado', ascending=False)
    
    print("\nValores financeiros por município:")
    print("-" * 100)
    print(f"{'Município':<15} {'Aprovado':>18} {'Produzido':>18} {'Valor Médio/Proc':>20}")
    print("-" * 100)
    
    for _, row in valores.iterrows():
        print(f"{row['Municipio']:<15} {row['Valor_Aprovado']:>18,.2f} "
              f"{row['Valor_Produzido']:>18,.2f} {row['Valor_Medio_Proc']:>20,.2f}")
    
    # Gráfico: Valores comparativos
    criar_grafico_barras_horizontal_agrupadas(
        valores['Municipio'].tolist(),
        valores['Valor_Aprovado'].values,
        valores['Valor_Produzido'].values,
        'Aprovado',
        'Produzido',
        'Valores Financeiros Comparativos',
        f'{pasta_graficos}/03_valores_comparativos.png'
    )
    
    return valores

def analisar_perfil_etario_comparativo(df_completo, pasta_graficos):
    """Análise comparativa do perfil etário"""
    imprimir_subcabecalho("PERFIL ETÁRIO COMPARATIVO", 80)
    
    # Estatísticas de idade por município
    stats_idade = df_completo.groupby('Municipio')['PA_IDADE'].agg(['mean', 'median', 'std']).reset_index()
    stats_idade.columns = ['Municipio', 'Idade_Media', 'Idade_Mediana', 'Desvio_Padrao']
    
    print("\nEstatísticas de idade por município:")
    print("-" * 80)
    print(f"{'Município':<15} {'Idade Média':>15} {'Mediana':>12} {'Desvio Padrão':>18}")
    print("-" * 80)
    
    for _, row in stats_idade.iterrows():
        print(f"{row['Municipio']:<15} {row['Idade_Media']:>15.2f} "
              f"{row['Idade_Mediana']:>12.1f} {row['Desvio_Padrao']:>18.2f}")
    
    # Criar faixas etárias amplas
    df_completo['Faixa_Etaria_Ampla'] = pd.cut(
        df_completo['PA_IDADE'],
        bins=[0, 18, 40, 60, 150],
        labels=['0-17', '18-39', '40-59', '60+']
    )
    
    # Distribuição por faixa etária ampla
    dist_etaria = df_completo.groupby(['Municipio', 'Faixa_Etaria_Ampla'], observed=True).size().reset_index(name='quantidade')
    
    print("\nDistribuição por faixa etária (%):")
    print("-" * 80)
    
    for municipio in df_completo['Municipio'].unique():
        print(f"\n  {municipio}:")
        dados_mun = dist_etaria[dist_etaria['Municipio'] == municipio]
        total_mun = dados_mun['quantidade'].sum()
        
        for _, row in dados_mun.iterrows():
            perc = (row['quantidade'] / total_mun) * 100
            print(f"    {row['Faixa_Etaria_Ampla']}: {row['quantidade']:>6,} ({perc:>5.2f}%)")
    
    # Gráfico: Distribuição etária comparativa
    plt.figure(figsize=(14, 8))
    
    pivot_etario = dist_etaria.pivot(index='Faixa_Etaria_Ampla', columns='Municipio', values='quantidade')
    pivot_etario.plot(kind='bar', color=['#3498db', '#e74c3c', '#2ecc71'])
    
    plt.title('Distribuição Etária Comparativa', fontsize=14, fontweight='bold')
    plt.xlabel('Faixa Etária', fontsize=12)
    plt.ylabel('Quantidade de Procedimentos', fontsize=12)
    plt.legend(title='Município', fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/04_perfil_etario_comparativo.png')
    
    return stats_idade

def analisar_areas_especializadas(df_completo, df_procedimentos, pasta_graficos):
    """Análise de áreas especializadas (cardiologia, oncologia)"""
    imprimir_subcabecalho("ANÁLISE DE ÁREAS ESPECIALIZADAS", 80)
    
    # Identificar procedimentos cardiológicos
    palavras_cardio = ['CARDIO', 'CORAÇÃO', 'CORONAR', 'VASCULAR']
    mask_cardio = df_procedimentos['ip_dscr'].str.contains('|'.join(palavras_cardio), case=False, na=False)
    codigos_cardio = df_procedimentos[mask_cardio]['ip_cod_padrao'].tolist()
    
    # Identificar procedimentos oncológicos
    palavras_onco = ['ONCO', 'CANCER', 'TUMOR', 'QUIMIO', 'RADIO']
    mask_onco = df_procedimentos['ip_dscr'].str.contains('|'.join(palavras_onco), case=False, na=False)
    codigos_onco = df_procedimentos[mask_onco]['ip_cod_padrao'].tolist()
    
    # Filtrar dados
    df_completo['Area'] = 'Outros'
    df_completo.loc[df_completo['PA_PROC_ID'].isin(codigos_cardio), 'Area'] = 'Cardiologia'
    df_completo.loc[df_completo['PA_PROC_ID'].isin(codigos_onco), 'Area'] = 'Oncologia'
    
    # Análise por área e município
    analise_areas = df_completo.groupby(['Municipio', 'Area']).size().reset_index(name='quantidade')
    
    print("\nProcedimentos especializados por município:")
    print("-" * 80)
    
    for municipio in df_completo['Municipio'].unique():
        print(f"\n  {municipio}:")
        dados_mun = analise_areas[analise_areas['Municipio'] == municipio]
        total_mun = dados_mun['quantidade'].sum()
        
        for _, row in dados_mun.iterrows():
            perc = (row['quantidade'] / total_mun) * 100
            print(f"    {row['Area']:<15}: {row['quantidade']:>7,} ({perc:>5.2f}%)")
    
    # Gráfico: Áreas especializadas
    plt.figure(figsize=(14, 8))
    
    # Filtrar apenas cardiologia e oncologia
    analise_espec = analise_areas[analise_areas['Area'].isin(['Cardiologia', 'Oncologia'])]
    
    if not analise_espec.empty:
        pivot_areas = analise_espec.pivot(index='Municipio', columns='Area', values='quantidade')
        pivot_areas.plot(kind='bar', color=['#e74c3c', '#9b59b6'])
        
        plt.title('Procedimentos Especializados por Município', fontsize=14, fontweight='bold')
        plt.xlabel('Município', fontsize=12)
        plt.ylabel('Quantidade de Procedimentos', fontsize=12)
        plt.legend(title='Área', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        salvar_grafico(f'{pasta_graficos}/05_areas_especializadas.png')
    
    return analise_areas

def analisar_tendencias_envelhecimento(df_completo, pasta_graficos):
    """Análise de tendências relacionadas ao envelhecimento"""
    imprimir_subcabecalho("TENDÊNCIAS DE ENVELHECIMENTO POPULACIONAL", 80)
    
    # Evolução da proporção de idosos (60+) ao longo do tempo
    df_completo['Idoso'] = df_completo['PA_IDADE'] >= 60
    
    prop_idosos = df_completo.groupby(['Competencia', 'Municipio', 'Idoso']).size().reset_index(name='quantidade')
    
    # Calcular proporção
    total_por_comp = df_completo.groupby(['Competencia', 'Municipio']).size().reset_index(name='total')
    prop_idosos = prop_idosos.merge(total_por_comp, on=['Competencia', 'Municipio'])
    prop_idosos['proporcao'] = (prop_idosos['quantidade'] / prop_idosos['total']) * 100
    
    # Filtrar apenas idosos
    prop_idosos_filtro = prop_idosos[prop_idosos['Idoso'] == True]
    
    print("\nProporção de procedimentos para idosos (60+) por município:")
    print("-" * 80)
    
    for municipio in df_completo['Municipio'].unique():
        dados_mun = prop_idosos_filtro[prop_idosos_filtro['Municipio'] == municipio]
        if not dados_mun.empty:
            media_prop = dados_mun['proporcao'].mean()
            primeira_prop = dados_mun.iloc[0]['proporcao']
            ultima_prop = dados_mun.iloc[-1]['proporcao']
            variacao = ultima_prop - primeira_prop
            
            print(f"\n  {municipio}:")
            print(f"    Proporção média: {media_prop:.2f}%")
            print(f"    Primeira competência: {primeira_prop:.2f}%")
            print(f"    Última competência: {ultima_prop:.2f}%")
            print(f"    Variação: {variacao:+.2f} pontos percentuais")
    
    # Gráfico: Evolução da proporção de idosos
    plt.figure(figsize=(16, 8))
    
    cores = {'Ijuí': '#3498db', 'Santa Rosa': '#e74c3c', 'Cruz Alta': '#2ecc71'}
    
    for municipio in prop_idosos_filtro['Municipio'].unique():
        dados_mun = prop_idosos_filtro[prop_idosos_filtro['Municipio'] == municipio]
        plt.plot(dados_mun['Competencia'], dados_mun['proporcao'], 
                marker='o', linewidth=2, label=municipio, color=cores.get(municipio, '#95a5a6'))
    
    plt.xlabel('Competência', fontsize=12)
    plt.ylabel('Proporção de Procedimentos para Idosos (%)', fontsize=12)
    plt.title('Evolução da Proporção de Procedimentos para Idosos (60+)', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    salvar_grafico(f'{pasta_graficos}/06_tendencia_envelhecimento.png')
    
    return prop_idosos_filtro

def gerar_relatorio_conclusoes(volume_por_municipio, taxas, valores, stats_idade):
    """Gera relatório com conclusões da análise"""
    imprimir_subcabecalho("CONCLUSÕES E INSIGHTS", 80)
    
    print("\n🔍 PRINCIPAIS CONCLUSÕES:\n")
    
    # 1. Volume
    maior_volume = volume_por_municipio.iloc[0]
    print(f"1. VOLUME DE ATENDIMENTOS:")
    print(f"   • {maior_volume['Municipio']} lidera com {maior_volume['quantidade']:,} procedimentos")
    
    # 2. Crescimento
    print(f"\n2. TAXA DE CRESCIMENTO:")
    if taxas:
        crescimento_ordenado = sorted(taxas.items(), key=lambda x: x[1]['crescimento_perc'], reverse=True)
        for municipio, dados in crescimento_ordenado:
            sinal = "📈" if dados['crescimento_perc'] > 0 else "📉"
            print(f"   {sinal} {municipio}: {dados['crescimento_perc']:+.2f}%")
    
    # 3. Valores
    print(f"\n3. RECURSOS FINANCEIROS:")
    maior_valor = valores.iloc[0]
    print(f"   • {maior_valor['Municipio']} tem o maior valor total: R$ {maior_valor['Valor_Aprovado']:,.2f}")
    
    # 4. Perfil etário
    print(f"\n4. PERFIL ETÁRIO:")
    for _, row in stats_idade.iterrows():
        print(f"   • {row['Municipio']}: idade média {row['Idade_Media']:.1f} anos")
    
    municipio_mais_velho = stats_idade.loc[stats_idade['Idade_Media'].idxmax(), 'Municipio']
    print(f"   ⚠️  {municipio_mais_velho} tem a população atendida mais envelhecida")
    
    print("\n" + "="*80)

def main():
    # Configuração inicial
    configurar_estilo_graficos()
    pasta_graficos = criar_diretorio('graficos/7_comparacoes_tendencias')
    
    imprimir_cabecalho("ANÁLISE COMPARATIVA E TENDÊNCIAS REGIONAIS\nIJUÍ, SANTA ROSA E CRUZ ALTA - RS", 80)
    
    # Carregar dados
    df_ijui, df_sr, df_ca = carregar_dados_municipios()
    df_completo = preparar_dados_comparacao(df_ijui, df_sr, df_ca)
    df_procedimentos = carregar_procedimentos()
    
    # Análises
    analisar_volume_comparativo(df_completo, pasta_graficos)
    analisar_evolucao_temporal_comparativa(df_completo, pasta_graficos)
    calcular_taxa_crescimento(df_completo.groupby(['Competencia', 'Municipio']).size().reset_index(name='quantidade'))
    analisar_valores_comparativos(df_completo, pasta_graficos)
    analisar_perfil_etario_comparativo(df_completo, pasta_graficos)
    analisar_areas_especializadas(df_completo, df_procedimentos, pasta_graficos)
    analisar_tendencias_envelhecimento(df_completo, pasta_graficos)
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 80)

if __name__ == "__main__":
    main()