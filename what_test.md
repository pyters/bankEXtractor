# Plano de Teste Manual — bankEXtractor

Para garantir que o conversor está operando corretamente após as implementações, siga este checklist de validação manual no painel Streamlit.

## 1. Testes de Detecção Automática
- [ ] **BTG Pactual**: Fazer upload do `BTG.pdf`. Verificar se o sistema detecta como "BTG".
- [ ] **Banco do Brasil**: Fazer upload do `bb.pdf`. Verificar se detecta como "BB".
- [ ] **Bradesco**: Fazer upload do `BRADESCO.PDF`. Verificar se detecta como "Bradesco".
- [ ] **Sicredi**: Fazer upload do `SICREDI.pdf`. Verificar se detecta como "Sicredi".
- [ ] **Banco Inter**: Fazer upload do `INTER.pdf`. Verificar se detecta como "Inter".
- [ ] **Nubank**: Fazer upload do `NU BANK.pdf`. Verificar se detecta como "Nubank".
- [ ] **Asaas**: Fazer upload do `Asaas.pdf`. Verificar se detecta como "Asaas".
- [ ] **Acredicoop**: Fazer upload do `ACREDICOOP.pdf`. Verificar se detecta como "Acredicoop".

## 2. Validação de Dados (Excel)
Para cada banco, após o processamento, baixe o arquivo Excel e verifique:
- [ ] **Datas**: Estão no formato DD/MM/YYYY?
- [ ] **Descrições**: Estão completas (incluindo as quebras de linha que foram unificadas)?
- [ ] **Sinais (Débito/Crédito)**:
    - [ ] Saídas/Pagamentos estão com valor **negativo** (ex: -150.00)?
    - [ ] Entradas/Recebimentos estão com valor **positivo** (ex: 150.00)?
- [ ] **Saldos Iniciais/Finais**: Estão presentes no Excel com o valor correto ou zerados conforme a regra do banco?

## 3. Testes de Estresse e Interface
- [ ] **Múltiplos Arquivos**: Tentar subir 2 ou 3 PDFs de bancos diferentes simultaneamente.
- [ ] **Arquivo Inválido**: Tentar subir um PDF que não seja um extrato. O sistema deve exibir um aviso de "Banco não identificado".
- [ ] **Limpeza de Cache**: Verificar se ao trocar o arquivo o grid do Streamlit atualiza os dados corretamente.

---
*Dica: Compare os valores da primeira e da última linha do Excel com o PDF original para garantir que nada foi cortado.*
