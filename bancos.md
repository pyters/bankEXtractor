# Mapa de Bancos — Conversor PDF → Excel

> Documento vivo. Atualizar sempre que um banco mudar o formato do extrato ou novos bancos forem adicionados.
> Última atualização: 26/02/2026

---

## Índice
- [x] BTG Pactual
- [ ] Banco do Brasil (BB)

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
- **Identificação**: Keyword scan para `sicredi` e `cooperativa de crédito`
- **Extração (`banks/sicredi.py`)**: Orientada a tabelas detectáveis nativamente usando `extract_tables()` do `pdfplumber`. Muito limpo e previsível.

### Banco Inter
- **Identificação**: Keyword scan para `banco inter`
- **Extração (`banks/inter.py`)**: Regex Mista. Estruturação contígua de linhas de saldo seguidas de linhas de transação. Resolve quebra de páginas espalmadas.

### Nu Bank (PJ)
- **Identificação**: Keyword scan para `nubank`, `nu pagamentos` ou `nu bank`.
- **Extração (`banks/nubank.py`)**: Altamente baseada em Regex Complexa Multilinha Lookahead. O PDF do Nubank não mapeia transações a cada linha. A Data e a Orientação Financeira (`Saida` e `Entrada`) são definidos pelo contexto/bloco superior.

### Asaas
- **Identificação**: Keyword scan para `asaas`.
- **Extração (`banks/asaas.py`)**: Parse Multilinha invertido baseado no sufixo de dinheiro de Final de Linha.

### Cooperativa Acredi (Acredicoop)
- **Identificação**: Keyword scan para `acredicoop` ou aglutinação de `acredi` e `cooperativa`.
- **Extração (`banks/acredicoop.py`)**: Regex flat com base no layout transacional padronizado na ordem Data > Descrição > Documento > Valor > Saldo.

---