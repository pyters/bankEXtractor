# Mapa de Bancos — Conversor PDF → Excel

> Documento vivo. Atualizar sempre que um banco mudar o formato do extrato ou novos bancos forem adicionados.
> Última atualização: 02/03/2026 — Versão 0.1

---

## Índice

- [x] BTG Pactual
- [x] Banco do Brasil (BB)
- [x] Bradesco
- [x] Sicredi
- [x] Banco Inter
- [x] Nu Bank (PJ)
- [x] Asaas
- [x] Cooperativa Acredi (Acredicoop)
- [x] Stone Instituição de Pagamento

---

## Detecção e Arquitetura por Instituição

Durante o processamento, o `bank_detector.py` faz um scanner textual (`page.extract_text()`) da primeira página do PDF e utiliza palavras-chave para identificar a instituição. O roteamento (Strategy) e Extração ocorrem da seguinte maneira:

### Banco do Brasil (BB)

- **Identificação**: Regex e Keyword scan para `banco do brasil`
- **Extração (`banks/bb.py`)**: Orientada a Expressões Regulares (Regex) com iterador linha a linha.

### BTG Pactual

- **Identificação**: Keyword scan para `btg pactual`
- **Extração (`banks/btg.py`)**: Utiliza `extract_tables()` nativo do `pdfplumber`, limpando rendimentos isentos/brutos de fundo de investimento como saldo zerado e respeitando blocos contábeis.

### Bradesco

- **Identificação**: Keyword scan para `bradesco`
- **Extração (`banks/bradesco.py`)**: Heurística de Value Lines e multilinhas de layout de texto via Text String split (Não contem grid nativo detectável).

### Banco Sicredi

- **Identificação**: Requer a palavra-chave `sicredi` explicitamente para evitar conflitos com outras cooperativas que usam layout similar.
- **Extração (`banks/sicredi.py`)**: Orientada a tabelas detectáveis nativamente usando `extract_tables()` do `pdfplumber`. Muito limpo e previsível.

### Banco Inter

- **Identificação**: Keyword scan para `banco inter`
- **Extração (`banks/inter.py`)**: Regex Mista. Estruturação contígua de linhas de saldo seguidas de linhas de transação. Resolve quebra de páginas espalmadas.

### Nu Bank (PJ)

- **Identificação**: Check prioritário. Keyword scan para `nubank`, `nu pagamentos` ou a combinação de `total de entradas` E `total de saídas` (exclusivo do layout Nubank PJ).  
- **Extração (`banks/nubank.py`)**: Altamente baseada em Regex Complexa Multilinha Lookahead. O PDF do Nubank não mapeia transações a cada linha. A Data e a Orientação Financeira (`Saida` e `Entrada`) são definidos pelo contexto/bloco superior.

### Asaas

- **Identificação**: Keyword scan para `asaas`.
- **Extração (`banks/asaas.py`)**: Parse Multilinha invertido baseado no sufixo de dinheiro de Final de Linha.

### Cooperativa Acredi (Acredicoop)

- **Identificação**: Check antes da Sicredi. Keyword scan para `acredicoop` ou `acredi`.
- **Extração (`banks/acredicoop.py`)**: Regex flat com base no layout transacional padronizado na ordem Data > Descrição > Documento > Valor > Saldo.

### Stone Instituição de Pagamento

- **Identificação**: Keyword scan para `stone instituição de pagamento` ou `stone`.
- **Extração (`banks/stone.py`)**: Regex Multilinha. Extrai o bloco de transação com base na linha de data e valor, buscando descrições na linha anterior ou posterior dependendo da orientação financeira.

---
