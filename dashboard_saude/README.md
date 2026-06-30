# Dashboard para Gestão em Saúde

Sistema em Python para gestão administrativo-financeira de uma clínica/área
de saúde, com cadastro de pacientes, profissionais, consultas e pagamentos,
cálculo de KPIs e geração de dashboard (texto + gráficos).

Desenvolvido como projeto prático aplicando: estruturas de dados, funções,
condicionais, laços, modularização, persistência em arquivo e tratamento de
erros, conforme o roteiro das Aulas 15, 16 e 17.

## Como executar

Requer Python 3.10+ e a biblioteca `matplotlib` (para os gráficos):

```bash
pip install matplotlib
```

1. (Opcional, mas recomendado para testar) Popule o sistema com dados de exemplo:
   ```bash
   python3 seed_data.py
   ```
2. Execute o sistema:
   ```bash
   python3 main.py
   ```
3. Navegue pelo menu para cadastrar, listar, buscar e visualizar o dashboard.

## Estrutura do projeto

```
dashboard_saude/
├── main.py          # Menu principal e fluxo de execução
├── models.py        # Classes/estruturas de dados (Paciente, Profissional, Consulta, Pagamento)
├── storage.py       # Leitura/gravação em CSV e JSON (toda a camada de I/O)
├── services.py      # Cadastro, listagem e busca (CRUD) de cada entidade
├── rules.py         # Cálculos de negócio: médias, saldo, taxas e KPIs
├── dashboard.py      # Exibição de tabelas/KPIs no terminal e geração de gráficos/relatório
├── seed_data.py     # Script para popular o sistema com dados de exemplo (testes)
├── config.json       # Configurações gerais (gerado se necessário)
├── data/             # Arquivos CSV com os dados cadastrados
│   ├── pacientes.csv
│   ├── profissionais.csv
│   ├── consultas.csv
│   └── pagamentos.csv
└── exports/          # Relatórios e gráficos gerados pelo dashboard
    ├── relatorio_gargalos.txt
    ├── kpis.json
    ├── grafico_volume_consultas.png
    ├── grafico_receita_por_tipo.png
    └── grafico_comparativo_financeiro.png
```

## Funcionalidades

- **Cadastro**: pacientes, profissionais, consultas (SUS/Particular/Convênio) e pagamentos, incluindo cadastro em lote de consultas.
- **Listagem**: com filtros por tipo e status de consulta, ou status de pagamento.
- **Busca**: por nome, ID, data, tipo, convênio ou status.
- **Regras de negócio / KPIs**:
  - Volume de consultas por tipo
  - Receita total e ticket médio por tipo
  - Taxa de cancelamento e taxa de glosa
  - Saldo financeiro (faturado x recebido x pendente x glosado)
  - Identificação automática de gargalos administrativos (heurísticas simples)
  - **Comparativo com período anterior** (mesma duração, com variação percentual de cada KPI)
- **Dashboard**: KPIs no terminal + gráficos (barras e pizza) salvos em PNG.
- **Exportação**: relatório em `.txt`, KPIs em `.json`, gráficos em `.png`.
- **Validação e tratamento de erros**: datas, tipos/status válidos, valores
  numéricos e referências entre entidades (ex.: consulta só pode ser
  cadastrada para paciente/profissional já existentes).

## Requisitos técnicos do curso — onde aparecem no código

- **Listas, tuplas e dicionários**: listas em quase todo módulo; tuplas em
  `rules._periodo_anterior` (retorna `(inicio, fim)`), em `main.cadastrar_consultas_em_lote`
  (lista de tuplas `(id, tipo, valor)`) e no resultado de `comparar_com_periodo_anterior`;
  dicionários como estrutura central de KPIs e configuração (`config.json`).
- **Conjuntos (`set`)**: `TIPOS_CONSULTA`, `STATUS_CONSULTA`, `STATUS_PAGAMENTO` em `models.py`.
- **Compreensões de lista**: em `services.py` (ex.: `listar_pacientes`), em
  `rules.comparar_com_periodo_anterior` (monta o dicionário de comparação) e em
  `main.cadastrar_consultas_em_lote` (soma de valores e lista de IDs do lote).
- **`if/elif/else`**: em todos os menus de `main.py` e nas validações de `models.py`/`rules.py`.
- **`for`/`while`**: `while True` nos menus e nas funções `ler_*`; `for` nas listagens e cálculos.
- **`break`/`continue`**: em `main.cadastrar_consultas_em_lote` — `break` encerra o lote
  quando o usuário digita "fim"; `continue` pula um item com erro sem interromper o lote.
- **Funções com `def`, parâmetros e retorno**: em todos os módulos.
- **Funções puras**: todas as funções de `rules.py` (mesmos parâmetros → mesmo resultado, sem I/O).
- **Funções de alta ordem**: uso de `max(..., key=...)` para achar o tipo dominante de consulta.
- **Modularização**: `import` entre módulos, separação clara de responsabilidades (ver tabela acima).
- **Persistência**: CSV (`data/*.csv`) e JSON (`config.json`, `exports/kpis.json`).
- **Tratamento de erros**: `try/except` em `main.py` (entradas do usuário) e em `storage.py` (I/O).

## Decisões de design

- **Dataclasses** em `models.py` para deixar a estrutura de cada entidade
  explícita e validar os dados já na criação (`__post_init__`).
- **Toda a I/O concentrada em `storage.py`** — os demais módulos nunca abrem
  arquivos diretamente, o que facilita testes e manutenção.
- **CSV para dados transacionais** (fácil de abrir em Excel/Sheets) e
  **JSON para configurações e exportação de KPIs** (estrutura aninhada).
- **`rules.py` com funções puras**: recebem dados e devolvem um resultado,
  sem efeitos colaterais — facilita testes e reuso (ex.: cálculo por período).
- Heurísticas de gargalo são simples e ajustáveis (limiares de % fixos em
  `rules.py`), pensadas para serem facilmente calibradas com dados reais.

## Possíveis evoluções

- Interface web (ex.: Streamlit/Flask) no lugar do menu de terminal.
- Persistência em banco de dados (SQLite) em vez de CSV.
- Autenticação e perfis de acesso (recepção, financeiro, gestão).
