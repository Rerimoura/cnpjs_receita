# Consulta CNPJ - Minas Gerais

Este aplicativo Streamlit permite consultar a base de dados de estabelecimentos ativos em Minas Gerais através do CNPJ.
A base de dados foi otimizada e dividida para respeitar os limites do GitHub.

## Funcionalidades
- **Busca por CNPJ**: Pesquise estabelecimentos pelo número de 14 dígitos.
- **Visualização de Endereço**: Exibe município (com mapeamento de código para nome), bairro, logradouro e número.
- **Situação Cadastral**: Exibe o status da empresa.
- **Backup Automático**: Sistema de fallback para leitura do arquivo de municípios caso esteja bloqueado.

## Instalação

1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como Executar

Execute o aplicativo Streamlit:
```bash
streamlit run app_cnpj.py
```

## Estrutura de Dados
Os arquivos de dados principais `estabelecimentos_mg_part1.parquet` e `estabelecimentos_mg_part2.parquet` são carregados automaticamente pelo aplicativo. Caso precise regenerar os dados, utilize o script `consulta_cnpj.py` (necessita do arquivo fonte original da Receita).
