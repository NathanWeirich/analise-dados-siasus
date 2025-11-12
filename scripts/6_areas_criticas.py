"""
Análise de Áreas Críticas da Saúde
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

def filtro_quimioterapia(df, df_proc):
    """Filtra procedimentos de quimioterapia"""
    codigos_quimio = df_proc[df_proc['ip_dscr'].str.contains('QUIMIO', case=False, na=False)]['ip_cod_padrao'].tolist()
    return df[df['PA_PROC_ID'].isin(codigos_quimio)]

def filtro_radioterapia(df, df_proc):
    """Filtra procedimentos de radioterapia"""
    codigos_radio = df_proc[df_proc['ip_dscr'].str.contains('RADIO', case=False, na=False)]['ip_cod_padrao'].tolist()
    return df[df['PA_PROC_ID'].isin(codigos_radio)]

def filtro_saude_mental(df, df_proc):
    """Filtra procedimentos de saúde mental"""
    palavras_chave = ['PSICO', 'MENTAL', 'PSIQUIAT', 'CAPS']
    mask = df_proc['ip_dscr'].str.contains('|'.join(palavras_chave), case=False, na=False)
    codigos_mental = df_proc[mask]['ip_cod_padrao'].tolist()
    return df[df['PA_PROC_ID'].isin(codigos_mental)]

def filtro_atencao_basica(df, df_proc):
    """Filtra procedimentos de atenção básica"""
    palavras_chave = ['CONSULTA', 'ATENDIMENTO', 'ACOMPANHAMENTO', 'PREVENTIV']
    mask = df_proc['ip_dscr'].str.contains('|'.join(palavras_chave), case=False, na=False)
    codigos_basica = df_proc[mask]['ip_cod_padrao'].tolist()
    return df[df['PA_PROC_ID'].isin(codigos_basica)]

def analisar_area(df, nome_area, filtro_func, df_proc, pasta_graficos):
    """Função genérica para analisar uma área crítica"""
    imprimir_subcabecalho(nome_area, 80)
    
    # Aplicar filtro
    df_filtrado = filtro_func(df, df_proc)
    
    if len(df_filtrado) == 0:
        print(f"\nNenhum procedimento encontrado para {nome_area}")
        return None
    
    # Estatísticas
    total = len(df_filtrado)
    aprovado = df_filtrado['PA_VALAPR'].sum()
    produzido = df_filtrado['PA_VALPRO'].sum()
    diferenca = produzido - aprovado
    perc = (diferenca / aprovado * 100) if aprovado > 0 else 0
    
    print(f"\nTotal de procedimentos: {total:,}")
    print(f"Valor Total Aprovado: {formatar_valor_monetario(aprovado)}")
    print(f"Valor Total Produzido: {formatar_valor_monetario(produzido)}")
    print(f"Diferença: {formatar_valor_monetario(diferenca)} ({perc:+.2f}%)")
    
    if total > 0:
        # Top 10 procedimentos da área
        top_proc = df_filtrado.groupby('PA_PROC_ID').agg({
            'PA_VALAPR': 'sum',
            'PA_CODUNI': 'count'
        }).reset_index()
        top_proc.columns = ['PA_PROC_ID', 'Valor_Total', 'Quantidade']
        top_proc = top_proc.sort_values('Quantidade', ascending=False)
        
        # Adicionar descrições
        top_proc = adicionar_descricoes(
            top_proc, df_proc,
            'PA_PROC_ID', 'ip_cod_padrao', 'ip_dscr'
        )
        
        print(f"\nTop 10 Procedimentos em {nome_area}:")
        print("-" * 110)
        print(f"{'#':<3} {'Código':<12} {'Descrição':<50} {'Quantidade':>12} {'Valor Total':>18}")
        print("-" * 110)
        
        for idx, (_, row) in enumerate(top_proc.head(10).iterrows(), 1):
            desc = truncar_texto(row['ip_dscr'], 50) if pd.notna(row['ip_dscr']) else 'Descrição não encontrada'
            print(f"{idx:<3} {row['PA_PROC_ID']:<12} {desc:<50} {row['Quantidade']:>12,} {row['Valor_Total']:>18,.2f}")
        
        # Evolução temporal
        df_filtrado_temp = preparar_competencia(df_filtrado)
        evolucao = df_filtrado_temp.groupby('Competencia').size().reset_index(name='quantidade')
        
        print(f"\nEvolução Mensal:")
        for _, row in evolucao.iterrows():
            print(f"  {row['Competencia']}: {row['quantidade']:,} procedimentos")
        
        # Gráfico: Top 10 procedimentos
        nome_arquivo = nome_area.lower().replace(' ', '_').replace('ç', 'c').replace('ã', 'a')
        top10 = top_proc.head(10)
        
        if len(top10) > 0:
            labels = [f"{row['PA_PROC_ID'][:6]}... - {truncar_texto(row['ip_dscr'], 30)}" 
                      for _, row in top10.iterrows()]
            
            criar_grafico_barras_horizontal(
                top10['Quantidade'].values,
                labels,
                f'Top 10 Procedimentos - {nome_area}',
                'Quantidade',
                f'{pasta_graficos}/top10_{nome_arquivo}.png',
                color='#9b59b6'
            )
    
    return df_filtrado

def main():
    # Configuração inicial
    configurar_estilo_graficos()
    pasta_graficos = criar_diretorio('graficos/6_areas_criticas')
    
    imprimir_cabecalho("ANÁLISE DE ÁREAS CRÍTICAS DA SAÚDE", 80)
    
    # ========== CARREGAR DADOS ==========
    df = carregar_csv()
    df_procedimentos = carregar_procedimentos()
    
    # Padronizar código de procedimento
    df = padronizar_codigo(df, 'PA_PROC_ID')
    
    print(f"\nTotal de registros no dataset: {len(df):,}")
    print(f"Total de procedimentos distintos: {df['PA_PROC_ID'].nunique():,}")
    
    # ========== ANÁLISE POR ÁREA ==========
    
    # 1. Quimioterapia
    df_quimio = analisar_area(df, "QUIMIOTERAPIA", filtro_quimioterapia, df_procedimentos, pasta_graficos)
    
    # 2. Radioterapia
    df_radio = analisar_area(df, "RADIOTERAPIA", filtro_radioterapia, df_procedimentos, pasta_graficos)
    
    # 3. Saúde Mental
    df_mental = analisar_area(df, "SAÚDE MENTAL", filtro_saude_mental, df_procedimentos, pasta_graficos)
    
    # 4. Atenção Básica
    df_basica = analisar_area(df, "ATENÇÃO BÁSICA", filtro_atencao_basica, df_procedimentos, pasta_graficos)
    
    # ========== COMPARAÇÃO ENTRE ÁREAS ==========
    imprimir_subcabecalho("COMPARAÇÃO ENTRE ÁREAS CRÍTICAS", 80)
    
    areas_dados = []
    
    if df_quimio is not None and len(df_quimio) > 0:
        areas_dados.append(('Quimioterapia', len(df_quimio), df_quimio['PA_VALAPR'].sum()))
    
    if df_radio is not None and len(df_radio) > 0:
        areas_dados.append(('Radioterapia', len(df_radio), df_radio['PA_VALAPR'].sum()))
    
    if df_mental is not None and len(df_mental) > 0:
        areas_dados.append(('Saúde Mental', len(df_mental), df_mental['PA_VALAPR'].sum()))
    
    if df_basica is not None and len(df_basica) > 0:
        areas_dados.append(('Atenção Básica', len(df_basica), df_basica['PA_VALAPR'].sum()))
    
    if areas_dados:
        print("\nResumo Comparativo:")
        print("-" * 80)
        print(f"{'Área':<20} {'Procedimentos':>15} {'Valor Total':>20} {'% do Total':>12}")
        print("-" * 80)
        
        total_geral = df['PA_VALAPR'].sum()
        
        for area, qtd, valor in areas_dados:
            perc = (valor / total_geral) * 100
            print(f"{area:<20} {qtd:>15,} {valor:>20,.2f} {perc:>11.2f}%")
        
        # Gráfico comparativo
        areas_nomes = [a[0] for a in areas_dados]
        areas_qtd = [a[1] for a in areas_dados]
        areas_valores = [a[2] for a in areas_dados]
        
        # Gráfico: Quantidade de procedimentos
        criar_grafico_barras_vertical(
            areas_nomes,
            areas_qtd,
            'Comparação: Quantidade de Procedimentos por Área',
            'Quantidade',
            f'{pasta_graficos}/comparacao_quantidade.png',
            color='#3498db'
        )
        
        # Gráfico: Valores por área
        criar_grafico_barras_vertical(
            areas_nomes,
            areas_valores,
            'Comparação: Valores por Área Crítica',
            'Valor Total (R$)',
            f'{pasta_graficos}/comparacao_valores.png',
            color='#e74c3c'
        )
    else:
        print("\nNenhuma área crítica encontrada com dados.")
    
    imprimir_cabecalho("ANÁLISE CONCLUÍDA!", 80)

if __name__ == "__main__":
    main()