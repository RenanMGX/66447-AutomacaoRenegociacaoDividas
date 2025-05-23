# Automação de Renegociação de Dívidas - Contas a Receber

Este projeto automatiza o processo de renegociação de dívidas utilizando Python, Selenium e manipulação de arquivos Excel.

## Estrutura do Projeto

- **Entities/imobme.py**: Classe principal de automação, responsável por acessar o sistema, navegar entre páginas e registrar renegociações.
- **Entities/preparar_dados.py**: Funções para validação, preparação dos dados e registro dos retornos no arquivo Excel.
- **teste.py**: Script principal para execução em lote, leitura dos dados, chamada da automação e gravação dos resultados.
- **teste.ipynb**: Notas e testes interativos para desenvolvimento e depuração.

## Funcionamento

1. **Leitura dos Dados**
   - O script lê um arquivo Excel com os contratos a serem renegociados.
   - Os dados são validados e preparados para processamento.

2. **Automação Web**
   - Utiliza Selenium para acessar o sistema Imobme.
   - Para cada contrato, navega até a página de renegociação, preenche os campos necessários e seleciona as parcelas conforme as datas informadas.
   - Marca checkboxes, preenche valores e confirma a renegociação.

3. **Registro de Resultados**
   - O resultado de cada tentativa (sucesso ou erro) é registrado em uma nova coluna do arquivo Excel, facilitando o acompanhamento.

4. **Execução**
   - O script principal (`teste.py`) pode ser executado diretamente.
   - O processo é automatizado e não requer intervenção manual durante a execução.

## Requisitos

- Python 3.8+
- Bibliotecas: `selenium`, `pandas`, `xlwings`, `openpyxl`
- Navegador Chrome instalado

## Como usar

1. Ajuste o caminho do arquivo Excel no `teste.py`.
2. Execute o script:
   ```bash
   python teste.py
   ```
3. O resultado será salvo no próprio arquivo Excel, na coluna "Observação".

## Observações

- O código está preparado para lidar com exceções e registrar mensagens de erro detalhadas.
- O uso de variáveis de ambiente pode ser feito para armazenar credenciais ou caminhos sensíveis.
- Para depuração, utilize o notebook `teste.ipynb`.

## Contato

Dúvidas ou sugestões? Entre em contato com a equipe de desenvolvimento.

```# Automação de Renegociação de Dívidas - Contas a Receber```

Este projeto automatiza o processo de renegociação de dívidas utilizando Python, Selenium e manipulação de arquivos Excel.

## Estrutura do Projeto

- **Entities/imobme.py**: Classe principal de automação, responsável por acessar o sistema, navegar entre páginas e registrar renegociações.
- **Entities/preparar_dados.py**: Funções para validação, preparação dos dados e registro dos retornos no arquivo Excel.
- **teste.py**: Script principal para execução em lote, leitura dos dados, chamada da automação e gravação dos resultados.
- **teste.ipynb**: Notas e testes interativos para desenvolvimento e depuração.

## Funcionamento

1. **Leitura dos Dados**
   - O script lê um arquivo Excel com os contratos a serem renegociados.
   - Os dados são validados e preparados para processamento.

2. **Automação Web**
   - Utiliza Selenium para acessar o sistema Imobme.
   - Para cada contrato, navega até a página de renegociação, preenche os campos necessários e seleciona as parcelas conforme as datas informadas.
   - Marca checkboxes, preenche valores e confirma a renegociação.

3. **Registro de Resultados**
   - O resultado de cada tentativa (sucesso ou erro) é registrado em uma nova coluna do arquivo Excel, facilitando o acompanhamento.

4. **Execução**
   - O script principal (`teste.py`) pode ser executado diretamente.
   - O processo é automatizado e não requer intervenção manual durante a execução.

## Requisitos

- Python 3.8+
- Bibliotecas: `selenium`, `pandas`, `xlwings`, `openpyxl`
- Navegador Chrome instalado

## Como usar

1. Ajuste o caminho do arquivo Excel no `teste.py`.
2. Execute o script:
   ```bash
   python teste.py
   ```
3. O resultado será salvo no próprio arquivo Excel, na coluna "Observação".

## Observações

- O código está preparado para lidar com exceções e registrar mensagens de erro detalhadas.
- O uso de variáveis de ambiente pode ser feito para armazenar credenciais ou caminhos sensíveis.
- Para depuração, utilize o notebook `teste.ipynb`.

## Contato

Dúvidas ou sugestões? Entre em contato com a equipe de desenvolvimento.
