"""Funções para criar visualizações padronizadas"""

import matplotlib.pyplot as plt
import pandas as pd
from .common import salvar_grafico

def criar_grafico_barras_horizontal(dados, labels, titulo, xlabel, output_path, 
                                    color='#3498db', mostrar_valores=True, figsize=(14, 10)):
    """Cria gráfico de barras horizontal padronizado"""
    plt.figure(figsize=figsize)
    y_pos = range(len(dados))
    
    plt.barh(y_pos, dados, color=color, alpha=0.8)
    plt.yticks(y_pos, labels, fontsize=9)
    plt.xlabel(xlabel, fontsize=12)
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3)
    
    if mostrar_valores:
        for i, v in enumerate(dados):
            plt.text(v, i, f" {v:,.0f}", va='center', fontsize=9)
    
    salvar_grafico(output_path)

def criar_grafico_barras_vertical(categorias, valores, titulo, ylabel, output_path,
                                  color='#3498db', mostrar_valores=True, figsize=(12, 6)):
    """Cria gráfico de barras vertical"""
    plt.figure(figsize=figsize)
    x_pos = range(len(categorias))
    
    bars = plt.bar(x_pos, valores, color=color, alpha=0.8)
    plt.xticks(x_pos, categorias, rotation=45, ha='right')
    plt.ylabel(ylabel, fontsize=12)
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3)
    
    if mostrar_valores:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=9)
    
    salvar_grafico(output_path)

def criar_grafico_barras_agrupadas(categorias, valores1, valores2, 
                                   label1, label2, titulo, output_path,
                                   color1='#3498db', color2='#2ecc71', figsize=(12, 6)):
    """Cria gráfico de barras agrupadas"""
    plt.figure(figsize=figsize)
    x = range(len(categorias))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], valores1, width, label=label1, 
            color=color1, alpha=0.8)
    plt.bar([i + width/2 for i in x], valores2, width, label=label2, 
            color=color2, alpha=0.8)
    
    plt.xlabel('Categoria', fontsize=12)
    plt.ylabel('Valor', fontsize=12)
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, categorias, rotation=15, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    salvar_grafico(output_path)

def criar_grafico_pizza(valores, labels, titulo, output_path, 
                       colors=None, explode=None, figsize=(10, 8)):
    """Cria gráfico de pizza padronizado"""
    plt.figure(figsize=figsize)
    
    if colors is None:
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    
    plt.pie(valores, labels=labels, autopct='%1.1f%%', colors=colors, 
            explode=explode, startangle=90, 
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title(titulo, fontsize=16, fontweight='bold', pad=20)
    
    salvar_grafico(output_path)

def criar_grafico_linha_temporal(df_temporal, coluna_tempo, coluna_valor, 
                                titulo, output_path, media_linha=True,
                                mostrar_limites=True, figsize=(16, 6)):
    """Cria gráfico de linha temporal"""
    plt.figure(figsize=figsize)
    
    media = df_temporal[coluna_valor].mean() if media_linha else None
    desvio = df_temporal[coluna_valor].std() if mostrar_limites else None
    
    plt.plot(range(len(df_temporal)), df_temporal[coluna_valor], 
            marker='o', linewidth=2, markersize=5, color='steelblue', 
            label='Valores')
    
    if media_linha and media is not None:
        plt.axhline(y=media, color='green', linestyle='--', linewidth=2, 
                   label=f'Média ({media:.0f})')
    
    if mostrar_limites and desvio is not None:
        plt.axhline(y=media + desvio, color='red', linestyle='--', 
                   linewidth=1, alpha=0.7, label='Limite Superior')
        plt.axhline(y=media - desvio, color='orange', linestyle='--', 
                   linewidth=1, alpha=0.7, label='Limite Inferior')
    
    # Preparar labels do eixo X
    if isinstance(df_temporal[coluna_tempo].iloc[0], str):
        labels_x = df_temporal[coluna_tempo].tolist()
    else:
        labels_x = [str(x) for x in df_temporal[coluna_tempo]]
    
    plt.xticks(range(len(df_temporal)), labels_x, rotation=45, ha='right')
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Período', fontsize=12)
    plt.ylabel('Quantidade', fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    salvar_grafico(output_path)

def criar_grafico_barras_horizontal_agrupadas(categorias, valores1, valores2,
                                              label1, label2, titulo, output_path,
                                              color1='lightcoral', color2='steelblue',
                                              figsize=(14, 10)):
    """Cria gráfico de barras horizontal agrupadas"""
    plt.figure(figsize=figsize)
    y_pos = range(len(categorias))
    width = 0.35
    
    plt.barh([i - width/2 for i in y_pos], valores1, width, 
            label=label1, color=color1, alpha=0.8)
    plt.barh([i + width/2 for i in y_pos], valores2, width, 
            label=label2, color=color2, alpha=0.8)
    
    plt.yticks(y_pos, categorias, fontsize=9)
    plt.xlabel('Valor', fontsize=12)
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(axis='x', alpha=0.3)
    
    salvar_grafico(output_path)