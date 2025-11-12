import pandas as pd
from database_connection import get_database_connection
import warnings

warnings.filterwarnings('ignore')

print("="*60)
print("VALIDAÇÃO E VERIFICAÇÃO DOS DADOS LIMPOS")
print("="*60)

# Carregar dados limpos
df = pd.read_csv('dados_limpos.csv', low_memory=False)

# ============================================================
# 1. DIMENSÕES DO DATASET
# ============================================================
print("\n" + "="*60)
print("1. DIMENSÕES DO DATASET")
print("="*60)
print(f"📊 Linhas: {df.shape[0]:,}")
print(f"📊 Colunas: {df.shape[1]}")
print(f"📊 Total de células: {df.shape[0] * df.shape[1]:,}")
print(f"💾 Memória utilizada: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# ============================================================
# 2. TIPOS DE VARIÁVEIS
# ============================================================
print("\n" + "="*60)
print("2. TIPOS DE VARIÁVEIS")
print("="*60)

# Contar tipos
tipo_count = df.dtypes.value_counts()
print("\n📋 Resumo dos tipos:")
for tipo, count in tipo_count.items():
    print(f"   {tipo}: {count} colunas")

# Separar por categoria
numericas = df.select_dtypes(include=['number']).columns.tolist()
categoricas = df.select_dtypes(include=['object']).columns.tolist()

print(f"\n📈 Colunas numéricas ({len(numericas)}):")
for col in numericas:
    print(f"   • {col}")

print(f"\n📝 Colunas categóricas/textuais ({len(categoricas)}):")
for col in categoricas:
    print(f"   • {col}")

# ============================================================
# 3. ESTATÍSTICAS DESCRITIVAS
# ============================================================
print("\n" + "="*60)
print("3. ESTATÍSTICAS DESCRITIVAS")
print("="*60)

# Estatísticas para numéricas
if numericas:
    print("\n📊 VARIÁVEIS NUMÉRICAS:")
    print(df[numericas].describe())
    
    print("\n📊 Detalhamento por coluna:")
    for col in numericas:
        print(f"\n   {col}:")
        print(f"      Média: {df[col].mean():.2f}")
        print(f"      Mediana: {df[col].median():.2f}")
        print(f"      Mínimo: {df[col].min():.2f}")
        print(f"      Máximo: {df[col].max():.2f}")
        print(f"      Desvio padrão: {df[col].std():.2f}")

# Estatísticas para categóricas
if categoricas:
    print("\n📊 VARIÁVEIS CATEGÓRICAS:")
    for col in categoricas:
        print(f"\n   {col}:")
        print(f"      Valores únicos: {df[col].nunique()}")
        print(f"      Top 5 valores:")
        top5 = df[col].value_counts().head(5)
        for valor, freq in top5.items():
            percentual = (freq / len(df)) * 100
            print(f"         • {valor}: {freq:,} ({percentual:.2f}%)")

# ============================================================
# 4. VALORES AUSENTES
# ============================================================
print("\n" + "="*60)
print("4. VALORES AUSENTES")
print("="*60)

missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100

missing_df = pd.DataFrame({
    'Coluna': missing.index,
    'Valores Faltantes': missing.values,
    'Percentual (%)': missing_percent.values
})

missing_df = missing_df[missing_df['Valores Faltantes'] > 0].sort_values('Valores Faltantes', ascending=False)

if not missing_df.empty:
    print("⚠️ COLUNAS COM VALORES AUSENTES:")
    print(missing_df.to_string(index=False))
else:
    print("✅ Nenhum valor ausente encontrado!")

# ============================================================
# 5. VALIDAÇÃO DE VALORES INVÁLIDOS
# ============================================================
print("\n" + "="*60)
print("5. VALIDAÇÃO DE VALORES INVÁLIDOS")
print("="*60)

problemas = []

# 5.1 Validar Idade
if 'PA_IDADE' in df.columns:
    print("\n🔍 Validando IDADE (PA_IDADE):")
    
    # Converter para numérico
    df['PA_IDADE'] = pd.to_numeric(df['PA_IDADE'], errors='coerce')
    
    idades_invalidas = df[(df['PA_IDADE'] < 0) | (df['PA_IDADE'] > 120)]
    
    if len(idades_invalidas) > 0:
        problemas.append(f"⚠️ {len(idades_invalidas)} registros com idade inválida")
        print(f"   ❌ {len(idades_invalidas)} idades fora do intervalo [0, 120]")
        print(f"\n   Estatísticas de idade:")
        print(f"      Mínima: {df['PA_IDADE'].min()}")
        print(f"      Máxima: {df['PA_IDADE'].max()}")
        print(f"      Média: {df['PA_IDADE'].mean():.2f}")
    else:
        print("   ✅ Todas as idades estão válidas [0-120]")

# 5.2 Validar Sexo
if 'PA_SEXO' in df.columns:
    print("\n🔍 Validando SEXO (PA_SEXO):")
    
    valores_sexo = df['PA_SEXO'].value_counts()
    print(f"   Distribuição:")
    for valor, freq in valores_sexo.items():
        percentual = (freq / len(df)) * 100
        print(f"      • {valor}: {freq:,} ({percentual:.2f}%)")
    
    sexos_validos = ['M', 'F', '0']
    sexos_invalidos = df[~df['PA_SEXO'].isin(sexos_validos)]
    
    if len(sexos_invalidos) > 0:
        problemas.append(f"⚠️ {len(sexos_invalidos)} registros com sexo inválido")
        print(f"   ❌ {len(sexos_invalidos)} valores inválidos de sexo")
        print(f"   Valores inválidos encontrados:")
        print(df[~df['PA_SEXO'].isin(sexos_validos)]['PA_SEXO'].value_counts())
    else:
        print("   ✅ Todos os valores de sexo são válidos")

# 5.3 Validar CIDs no banco de dados
print("\n🔍 Validando CIDs no banco de dados:")

# A coluna PA_CIDPRI contém os códigos CID
if 'PA_CIDPRI' in df.columns:
    try:
        # Conectar ao banco e buscar CIDs válidos
        print(f"   📡 Conectando ao banco datasus_db...")
        connection = get_database_connection()
        
        if connection:
            cursor = connection.cursor()
            
            # Buscar todos os CIDs válidos da tabela s_cid (coluna cd_cod)
            cursor.execute("SELECT DISTINCT cd_cod, cd_descr FROM s_cid")
            resultados = cursor.fetchall()
            
            # Criar dicionário: código -> descrição
            cids_validos = {row[0]: row[1] for row in resultados}
            
            print(f"   ✅ {len(cids_validos):,} CIDs válidos carregados do banco")
            
            # Validar coluna PA_CIDPRI
            print(f"\n   🔍 Validando coluna: PA_CIDPRI")
            
            # Remover valores nulos para análise
            cids_presentes = df['PA_CIDPRI'].dropna().unique()
            print(f"      Total de CIDs únicos na coluna: {len(cids_presentes)}")
            
            # Verificar CIDs inválidos
            cids_invalidos = [cid for cid in cids_presentes if cid not in cids_validos and cid != 'Não informado']
            
            if cids_invalidos:
                qtd_registros_invalidos = df[df['PA_CIDPRI'].isin(cids_invalidos)].shape[0]
                problemas.append(f"⚠️ PA_CIDPRI: {len(cids_invalidos)} CIDs não existem no banco ({qtd_registros_invalidos} registros)")
                print(f"      ❌ {len(cids_invalidos)} CIDs inválidos encontrados")
                print(f"      ❌ {qtd_registros_invalidos} registros afetados ({(qtd_registros_invalidos/len(df)*100):.2f}%)")
                
                if len(cids_invalidos) <= 10:
                    print(f"      CIDs inválidos: {cids_invalidos}")
                else:
                    print(f"      Primeiros 10 CIDs inválidos: {cids_invalidos[:10]}")
            else:
                print(f"      ✅ Todos os CIDs são válidos!")
            
            # Mostrar os 10 CIDs mais frequentes com descrição
            print(f"\n   📊 Top 10 CIDs mais frequentes:")
            top_cids = df['PA_CIDPRI'].value_counts().head(10)
            for i, (cid, freq) in enumerate(top_cids.items(), 1):
                percentual = (freq / len(df)) * 100
                descricao = cids_validos.get(cid, "Descrição não encontrada")
                print(f"      {i}. {cid} - {descricao}")
                print(f"         {freq:,} ocorrências ({percentual:.2f}%)")
            
            cursor.close()
            connection.close()
        else:
            print(f"   ❌ Não foi possível conectar ao banco")
            problemas.append(f"⚠️ Não foi possível validar CIDs - sem conexão com banco")
        
    except Exception as e:
        print(f"   ❌ Erro ao validar CIDs: {str(e)}")
        problemas.append(f"⚠️ Não foi possível validar CIDs no banco")
else:
    print("   ⚠️ Coluna PA_CIDPRI não encontrada no dataset")

# ============================================================
# 6. RESUMO DE PROBLEMAS IDENTIFICADOS
# ============================================================
print("\n" + "="*60)
print("6. RESUMO DE PROBLEMAS IDENTIFICADOS")
print("="*60)

if problemas:
    print(f"\n⚠️ Total de problemas encontrados: {len(problemas)}\n")
    for i, problema in enumerate(problemas, 1):
        print(f"   {i}. {problema}")
else:
    print("\n✅ Nenhum problema identificado! Dataset está válido.")

# ============================================================
# 7. DISTRIBUIÇÃO DE FREQUÊNCIAS (TOP CATEGORIAS)
# ============================================================
print("\n" + "="*60)
print("7. DISTRIBUIÇÃO DE FREQUÊNCIAS (TOP 10)")
print("="*60)

for col in categoricas[:5]:  # Mostrar apenas as 5 primeiras colunas categóricas
    print(f"\n📊 {col}:")
    freq = df[col].value_counts().head(10)
    for valor, count in freq.items():
        percentual = (count / len(df)) * 100
        print(f"   • {valor}: {count:,} ({percentual:.2f}%)")

# ============================================================
# 8. RELATÓRIO FINAL
# ============================================================
print("\n" + "="*60)
print("8. RELATÓRIO FINAL")
print("="*60)
print(f"✅ Total de registros: {len(df):,}")
print(f"✅ Total de variáveis: {len(df.columns)}")
print(f"✅ Variáveis numéricas: {len(numericas)}")
print(f"✅ Variáveis categóricas: {len(categoricas)}")
print(f"✅ Valores nulos: {df.isnull().sum().sum():,}")
print(f"✅ Problemas identificados: {len(problemas)}")

print("\n" + "="*60)
print("✅ VALIDAÇÃO CONCLUÍDA!")
print("="*60)