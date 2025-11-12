import pandas as pd
import warnings

# Suprimir warnings específicos (opcional)
warnings.filterwarnings('ignore', category=FutureWarning)

print("="*60)
print("LIMPEZA DE DADOS")
print("="*60)

# Carregar dados com low_memory=False para evitar DtypeWarning
df = pd.read_csv('dados_pars.csv', low_memory=False)

print(f"\n📊 Dimensões iniciais: {df.shape[0]} linhas x {df.shape[1]} colunas")

# 1. Filtrar apenas dados de 2025
if 'PA_CMP' in df.columns:
    print("\n🗓️ Filtrando dados de 2025...")
    antes = len(df)
    
    # Converter PA_CMP para string e extrair o ano (primeiros 4 dígitos)
    df['PA_CMP'] = df['PA_CMP'].astype(str)
    df['ano_temp'] = df['PA_CMP'].str[:4]
    
    # Filtrar apenas 2025
    df = df[df['ano_temp'] == '2025']
    
    # Remover coluna temporária
    df = df.drop(columns=['ano_temp'])
    
    print(f"   ✅ Mantidos apenas dados de 2025")
    print(f"   ✅ Removidas {antes - len(df)} linhas de outros anos")
else:
    print("\n   ⚠️ Coluna 'PA_CMP' não encontrada - filtro de ano não aplicado")

# 2. Remover duplicatas
print("\n🧹 Removendo duplicatas...")
df_original = len(df)
df = df.drop_duplicates()
print(f"   ✅ Removidas {df_original - len(df)} linhas duplicadas")

# 3. Remover colunas com muitos valores nulos (>50%)
print("\n🧹 Analisando colunas com valores nulos...")
threshold = 0.5  # 50% de valores nulos

colunas_para_remover = []
colunas_para_preencher = []

for col in df.columns:
    if df[col].isnull().sum() > 0:
        percentual_nulo = df[col].isnull().sum() / len(df)
        qtd = df[col].isnull().sum()
        
        if percentual_nulo > threshold:
            colunas_para_remover.append(col)
            print(f"   ❌ {col}: {qtd} nulos ({percentual_nulo*100:.2f}%) - SERÁ REMOVIDA")
        else:
            colunas_para_preencher.append(col)
            print(f"   ⚠️ {col}: {qtd} nulos ({percentual_nulo*100:.2f}%) - SERÁ PREENCHIDA")

# Remover colunas com muitos nulos
if colunas_para_remover:
    df = df.drop(columns=colunas_para_remover)
    print(f"\n   ✅ Removidas {len(colunas_para_remover)} colunas com mais de {threshold*100}% de nulos")

# Preencher colunas com poucos nulos
if colunas_para_preencher:
    print(f"\n🧹 Preenchendo colunas com menos de {threshold*100}% de nulos...")
    for col in colunas_para_preencher:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('Não informado')
        else:
            df[col] = df[col].fillna(-1)
        print(f"   ✅ {col}: preenchido")

# 4. Verificar campo 'sexo'
if 'PA_SEXO' in df.columns:
    print("\n📊 Distribuição do campo 'PA_SEXO':")
    valores_sexo = df['PA_SEXO'].value_counts().to_dict()
    print(f"   {valores_sexo}")
    print("   ✅ Valores mantidos como estão no dataset original")

# 5. Remover idades inválidas (se existir)
if 'PA_IDADE' in df.columns:
    print("\n🔧 Removendo idades inválidas...")
    antes = len(df)
    
    # Converter PA_IDADE para numérico se não for
    df['PA_IDADE'] = pd.to_numeric(df['PA_IDADE'], errors='coerce')
    
    # Remover idades inválidas
    df = df[(df['PA_IDADE'] >= 0) & (df['PA_IDADE'] <= 120)]
    print(f"   ✅ Removidas {antes - len(df)} linhas com idade inválida")

# 6. Resumo da limpeza
print("\n" + "="*60)
print("RESUMO DA LIMPEZA")
print("="*60)
print(f"📊 Dados originais: {df_original} linhas")
print(f"📊 Dados limpos: {len(df)} linhas x {df.shape[1]} colunas")
print(f"📉 Linhas removidas: {df_original - len(df)} ({((df_original - len(df))/df_original*100):.2f}%)")
print(f"📉 Colunas removidas: {len(colunas_para_remover)}")
print(f"✅ Valores nulos restantes: {df.isnull().sum().sum()}")

# 7. Salvar dados limpos
df.to_csv('dados_limpos.csv', index=False)
print(f"\n💾 Dados limpos salvos em 'dados_limpos.csv'")

print("\n" + "="*60)
print("✅ LIMPEZA CONCLUÍDA!")
print("="*60)