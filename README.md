# Análises Ambulatoriais — Ijuí e Região

## Pré-requisitos

- **Python 3.8+** instalado (Windows)
- **MySQL** com base de dados DATASUS configurada
- Instalar dependências:
  ```bash
  pip install -r requirements.txt
  ```

---

## Configuração Inicial

### 1. Configurar Banco de Dados

Edite o arquivo `database_connection.py` com suas credenciais MySQL ou crie um arquivo `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=datasus_db
DB_USER=root
DB_PASSWORD=sua_senha_aqui
```

---

## Fluxo de Trabalho

### Passo 1: Extrair Dados do Banco SQL

#### Para Ijuí (código 431020):
```bash
python extrair_dados_slq_to_csv.py
```
- **Gera**: `dados_pars.csv`

#### Para outras cidades (Santa Rosa: 4317202, Cruz Alta: 4306106):
```bash
python extrair_outras_cidades.py
```
- Edite o código SQL no arquivo para escolher o município
- **Gera**: `dados_pars_sr.csv` ou `dados_pars_ca.csv`

### Passo 2: Limpar os Dados

#### Para Ijuí:
```bash
python limpeza_dados.py
```
- **Entrada**: `dados_pars.csv`
- **Saída**: `dados_limpos.csv`

#### Para outras cidades:
```bash
python limpeza_dados_outras_cidades.py
```
- **Entrada**: `dados_pars_sr.csv` ou `dados_pars_ca.csv`
- **Saída**: `dados_limpos_sr.csv` ou `dados_limpos_ca.csv`

**Operações de limpeza realizadas:**
- Filtro de dados de 2025
- Remoção de duplicatas
- Remoção de colunas com >50% valores nulos
- Preenchimento de valores ausentes
- Validação de idades (0-120 anos)

### Passo 3: Análise Exploratória (Opcional)

```bash
python analise_exploratoria_de_dados.py
```

**Validações realizadas:**
- Dimensões e tipos de variáveis
- Estatísticas descritivas
- Valores ausentes e inválidos
- Validação de CIDs contra o banco de dados
- Distribuição de frequências

### Passo 4: Executar Scripts de Análise

Execute os scripts na ordem sugerida:

#### 1. Volume e Perfil dos Procedimentos
```bash
python scripts\1_volume_perfil_procedimentos.py
```
- Top 15 procedimentos mais realizados
- Evolução temporal (mensal/trimestral)
- Identificação de picos e quedas

#### 2. Produção por Estabelecimento
```bash
python scripts\2_producao_estabelecimento_saude.py
```
- Ranking de estabelecimentos
- Taxa de produção (aprovados vs produzidos)
- Identificação de estabelecimentos com baixa/alta produção

#### 3. Perfil Demográfico e Epidemiológico
```bash
python scripts\3_perfil_demografico_epidemiologico.py
```
- Distribuição por sexo e faixa etária
- Estatísticas de idade
- Grupos predominantes

#### 4. Fluxos Regionais e Acesso
```bash
python scripts\4_fluxos_regionais_acessos.py
```
- Origem dos pacientes (Ijuí vs outros municípios)
- Estabelecimentos mais procurados
- Top municípios externos

#### 5. Recursos Financeiros
```bash
python scripts\5_recursos_financeiros.py
```
- Valores totais (aprovado vs produzido)
- Evolução mensal dos valores
- Gasto médio por procedimento
- Top procedimentos mais caros
- Distribuição por faixa de valor

#### 6. Áreas Críticas da Saúde
```bash
python scripts\6_areas_criticas.py
```
- Análise de quimioterapia
- Análise de radioterapia
- Análise de saúde mental
- Análise de atenção básica
- Comparação entre áreas

#### 7. Comparações e Tendências Regionais
```bash
python scripts\7_comparacoes_tendencias.py
```
- Comparação entre Ijuí, Santa Rosa e Cruz Alta
- Evolução temporal comparativa
- Taxa de crescimento
- Valores financeiros comparativos
- Perfil etário comparativo
- Áreas especializadas
- Tendências de envelhecimento

---

## Estrutura do Projeto

```
📁 Trabalho 3/
├── 📄 database_connection.py          # Configuração de conexão MySQL
├── 📄 extrair_dados_slq_to_csv.py    # Extração de dados de Ijuí
├── 📄 extrair_outras_cidades.py      # Extração de Santa Rosa e Cruz Alta
├── 📄 limpeza_dados.py               # Limpeza dados de Ijuí
├── 📄 limpeza_dados_outras_cidades.py # Limpeza outras cidades
├── 📄 analise_exploratoria_de_dados.py # Análise exploratória inicial
├── 📄 requirements.txt               # Dependências Python
├── 📄 README.md                      # Documentação
│
├── 📄 dados_pars.csv                 # Dados brutos Ijuí
├── 📄 dados_pars_sr.csv             # Dados brutos Santa Rosa
├── 📄 dados_pars_ca.csv             # Dados brutos Cruz Alta
├── 📄 dados_limpos.csv              # Dados limpos Ijuí
├── 📄 dados_limpos_sr.csv           # Dados limpos Santa Rosa
├── 📄 dados_limpos_ca.csv           # Dados limpos Cruz Alta
│
├── 📁 scripts/
│   ├── 1_volume_perfil_procedimentos.py
│   ├── 2_producao_estabelecimento_saude.py
│   ├── 3_perfil_demografico_epidemiologico.py
│   ├── 4_fluxos_regionais_acessos.py
│   ├── 5_recursos_financeiros.py
│   ├── 6_areas_criticas.py
│   └── 7_comparacoes_tendencias.py
│
├── 📁 utils/
│   ├── __init__.py
│   ├── common.py           # Funções comuns (gráficos, formatação)
│   ├── data_loader.py      # Carregamento de dados CSV e MySQL
│   ├── data_processor.py   # Processamento de dados
│   └── visualizacoes.py    # Criação de visualizações
│
└── 📁 graficos/
    ├── 1_volume_perfil_procedimentos/
    ├── 2_producao_estabelecimentos/
    ├── 3_perfil_demografico_epidemiologico/
    ├── 4_fluxos_regionais_acessos/
    ├── 5_recursos_financeiros/
    ├── 6_areas_criticas/
    └── 7_comparacoes_tendencias/
```

---


## Colunas Principais do Dataset

- **PA_CMP**: Competência (formato AAAAMM, ex: 202501)
- **PA_PROC_ID**: Código do procedimento (10 dígitos)
- **PA_IDADE**: Idade do paciente (0-120 anos)
- **PA_SEXO**: Sexo (M/F/0)
- **PA_VALAPR**: Valor aprovado pelo SUS (R$)
- **PA_VALPRO**: Valor produzido (R$)
- **PA_QTDAPR**: Quantidade aprovada
- **PA_QTDPRO**: Quantidade produzida
- **PA_CODUNI**: Código CNES do estabelecimento (7 dígitos)
- **PA_MUNPCN**: Código do município do paciente (6 dígitos)
- **PA_CIDPRI**: CID principal do procedimento

---

## Tabelas Auxiliares do Banco

- **tb_sigtaw**: Descrição dos procedimentos (ip_cod, ip_dscr)
- **tb_municip**: Nomes dos municípios (co_municip, ds_nome)
- **cadgerrs**: Estabelecimentos CNES (cnes, fantasia, raz_soci)
- **s_cid**: Classificação Internacional de Doenças (cd_cod, cd_descr)
- **dimtempo**: Dimensão temporal (Id, mes, mesext, ano, anomes, trimestre, etc.)

---

## Observações Práticas

- **Warnings suprimidos**: Scripts usam `warnings.filterwarnings('ignore', category=UserWarning)`
- **Gráficos**: Salvos automaticamente em alta resolução (300 DPI) em subpastas de `graficos/`
- **Conexão com banco**: Configure `database_connection.py` com suas credenciais MySQL

---

## Dependências

```txt
pandas
mysql-connector-python
python-dotenv
matplotlib
seaborn
```

---
