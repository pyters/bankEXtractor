# Bank EXtractor 🏦📄➡️📊

O **Bank EXtractor** é uma ferramenta poderosa e extensível desenvolvida em Python para converter extratos bancários em formato PDF em planilhas Excel estruturadas (`.xlsx`).

Utilizando o `pdfplumber` e estratégias avançadas de processamento de texto (Regex e Extração de Tabelas), ele resolve o problema de extratos com layouts complexos, multilinhas e falta de padrões estruturais entre bancos.

## 🚀 Bancos Suportados
Atualmente, o projeto suporta a extração dos seguintes bancos:
- ✅ **BTG Pactual** (Tabelas nativas)
- ✅ **Banco do Brasil** (Regex de texto cru)
- ✅ **Bradesco** (Fatiamento de layout de texto)
- ✅ **Sicredi** (Grades identificadas)
- ✅ **Banco Inter** (Regex Mista / Tabelas)
- ✅ **Nubank PJ** (Regex Lookahead Contextual)
- ✅ **Asaas** (Regex Inversa por sufixo de valor)
- ✅ **Acredicoop** (Regex Flat de 5 colunas)

## 🛠️ Tecnologias Utilizadas
- **Python 3.12+**
- **Streamlit**: Interface web intuitiva para upload e download.
- **pdfplumber**: Motor de extração de dados de PDFs.
- **Pandas**: Manipulação e estruturação de dados.
- **Openpyxl**: Engine para geração de arquivos Excel.

## 📦 Como Instalar e Rodar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/bankEXtractor.git
   cd bankEXtractor
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Linux/Mac
   .venv\Scripts\activate     # No Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o aplicativo:**
   ```bash
   streamlit run main.py
   ```

## 🧪 Como Testar
Para validar novas implementações ou garantir que tudo está funcionando nos bancos existentes:
1. Veja o arquivo [what_test.md](what_test.md) para o guia de teste manual.
2. Utilize os scripts de teste unitário `/test_[banco]_module.py` para diagnósticos rápidos via terminal.

## 📐 Arquitetura
O projeto utiliza os padrões **Strategy** e **Factory Method** para garantir que cada banco tenha sua própria lógica isolada em `banks/`, enquanto o `core/bank_detector.py` decide automaticamente qual extrator utilizar baseado no conteúdo do arquivo.

---
Desenvolvido como um assistente para automação financeira.
