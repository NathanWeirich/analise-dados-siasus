"""
Pacote de utilitários para análises do DATASUS
"""

# Importar pandas para usar nos scripts
import pandas as pd
import numpy as np

from .common import *
from .data_loader import *
from .data_processor import *
from .visualizacoes import *

__all__ = [
    # Exportar pandas
    'pd',
    'np',
    
    # common
    'criar_diretorio',
    'configurar_estilo_graficos',
    'salvar_grafico',
    'imprimir_cabecalho',
    'imprimir_subcabecalho',
    'formatar_valor_monetario',
    'formatar_percentual',
    
    # data_loader
    'carregar_csv',
    'carregar_tabela_db',
    'carregar_procedimentos',
    'carregar_municipios',
    'carregar_estabelecimentos',
    'carregar_cids',
    'carregar_dim_tempo',
    
    # data_processor
    'padronizar_codigo',
    'adicionar_descricoes',
    'preparar_competencia',
    'preparar_temporal',
    'calcular_estatisticas_basicas',
    'agrupar_por_categoria',
    'identificar_picos_quedas',
    'calcular_periodos_recentes',
    'truncar_texto',
    
    # visualizacoes
    'criar_grafico_barras_horizontal',
    'criar_grafico_barras_agrupadas',
    'criar_grafico_pizza',
    'criar_grafico_linha_temporal',
    'criar_grafico_barras_vertical',
    'criar_grafico_barras_horizontal_agrupadas',
]