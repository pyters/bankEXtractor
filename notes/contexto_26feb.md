# Contexto do Projeto: Conversor Joicont (PDF → Excel)

## 🎯 O Problema e o Objetivo
O objetivo deste software é automatizar a conversão de extratos bancários em PDF para planilhas Excel padronizadas. 
- **Usuário Final:** Contadores (Joicont).
- **Requisito Não-Funcional Principal:** Interface com "zero atrito". O usuário não tem conhecimento técnico. O software deve ser uma tela simples de "Arrastar PDF" e "Baixar Excel".

## 🏗️ Decisões de Arquitetura (Padrão Strategy)
Devido à natureza instável dos PDFs de banco (cada um tem um formato, e eles mudam com o tempo), optou-se por uma **Arquitetura Modular (Strategy Pattern)**.
Em vez de um código gigante cheio de `if/else`, o sistema funciona como uma placa-mãe com "slots" intercambiáveis:
1. **Controlador (`main.py`):** Interface visual (Streamlit) e orquestração.
2. **MUX/Identificador (`identificador.py`):** Lê o cabeçalho do PDF e descobre de qual banco se trata.
3. **Módulos de Banco (`bancos/*.py`):** Scripts independentes para cada banco (ex: `btg.py`, `bb.py`). Eles herdam as regras de `banco_base.py`. Se um banco mudar o formato, apenas o arquivo dele é alterado, com risco zero de quebrar o resto do sistema.
4. **Condicionador de Sinal (`utils/formatador.py` - Futuro):** Limpa os dados de saída (padroniza datas e transforma "150,00 D" ou "150,00 (-)" em `-150.00`).

## 🛠️ Stack Tecnológica
- **Backend/Lógica:** Python 3
- **Interface Gráfica:** Streamlit (Simplicidade máxima, design clean nativo).
- **Extração de PDF:** `pdfplumber` (Excelente precisão geométrica para ler tabelas e ignorar cabeçalhos).
- **Manipulação de Dados:** `pandas`
- **Geração de Excel:** `openpyxl`

## 🚦 Estado Atual do Projeto (O que já foi feito)
- [x] Definição da Stack e Arquitetura.
- [x] Mapeamento dos primeiros bancos no arquivo `BANCOS.md` (BTG, Banco do Brasil e Bradesco).
- [x] Criação da estrutura de pastas.
- [x] Desenvolvimento do `banco_base.py` (o contrato).
- [x] Desenvolvimento do `identificador.py` (capaz de identificar BTG, BB e Bradesco com base nos PDFs reais analisados).
- [x] Construção do `main.py` com a interface inicial em Streamlit e dados "mockados" (falsos) para validar o fluxo visual.

## 🚀 Próximos Passos (Onde a IA deve focar agora)
1. **Construir o primeiro extrator real:** Usar as regras definidas no `BANCOS.md` para escrever o script de extração (ex: `bancos/btg.py`) usando `pdfplumber` e `pandas`.
2. **Substituir o Mock:** No `main.py`, trocar a geração da tabela falsa (`dados_falsos`) pela chamada real da função `extrair_dados()` do módulo do banco detectado.
3. **Criar o Formatador:** Desenvolver as funções para limpar a coluna de VALOR e DATA.