"""Funções utilitárias comuns para análises"""

import matplotlib.pyplot as plt
import seaborn as sns
import os

def criar_diretorio(caminho):
    """Cria diretório se não existir"""
    os.makedirs(caminho, exist_ok=True)
    return caminho

def configurar_estilo_graficos():
    """Configura estilo padrão dos gráficos"""
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10

def salvar_grafico(caminho, dpi=300):
    """Salva gráfico com configurações padrão"""
    plt.tight_layout()
    plt.savefig(caminho, dpi=dpi, bbox_inches='tight')
    print(f"✓ Gráfico salvo: {caminho}")
    plt.close()

def imprimir_cabecalho(titulo, largura=80):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * largura)
    print(titulo)
    print("=" * largura)

def imprimir_subcabecalho(titulo, largura=80):
    """Imprime subcabeçalho formatado"""
    print("\n" + "-" * largura)
    print(titulo)
    print("-" * largura)

def formatar_valor_monetario(valor):
    """Formata valor monetário"""
    return f"R$ {valor:,.2f}"

def formatar_percentual(valor):
    """Formata percentual"""
    return f"{valor:.2f}%"