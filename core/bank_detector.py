import pdfplumber

def detect_bank(filepath: str) -> str:
    """
    Lê a primeira página de um PDF e tenta identificar de qual banco ele é.
    Retorna uma string com o identificador do banco, que será usada
    como chave pelo Factory para instanciar a classe extratora correspondente.
    """
    try:
        with pdfplumber.open(filepath) as pdf:
            # Pegamos apenas a primeira página para ler o cabeçalho
            first_page = pdf.pages[0]
            text = first_page.extract_text().lower()

            # Baseado no PDF real: "conta corrente - pj" e menções implícitas ao BTG (geralmente nome do arquivo ou outros detalhes)
            # Na verdare, o extrato do BTG testado incrivelmente não tem a palavra "BTG" solta no texto textual do header!
            # Mas tem "conta corrente - pj", "saldo bloqueado", "01. conta corrente", "02. lançamentos".
            if "conta corrente - pj" in text and "02. lançamentos" in text:
                return "btg"
            
            if "extrato de conta corrente" in text and "cliente" in text:
                return "bb"
                
            if "bradesco" in text and "net empresa" in text:
                return "bradesco"
            # O PDF Bradesco às vezes não tem "bradesco" escrito claro na tela principal?
            # Na investigação a page tem: "Agência | Conta Total Disponível (R$) Total (R$)"
            if "total disponível" in text and "agência | conta" in text:
                return "bradesco"
                
            if "sicredi" in text or ("cooperativa:" in text and "conta:" in text and "saldo anterior" in text):
                return "sicredi"
                
            if "instituição: banco inter" in text or "banco inter" in text:
                return "inter"
            
            if "nubank" in text.lower() or "nu pagamentos" in text.lower() or "nu bank" in text.lower() or "total de entradas" in text:
                return "nubank"
                
            if "asaas" in text.lower() or "data movimentações valor" in text.lower():
                return "asaas"
                
            if "acredicoop" in text.lower() or "acredi" in text.lower() and "cooperativa" in text.lower():
                return "acredicoop"
                
    except Exception as e:
        print(f"Erro ao ler PDF para identificação: {e}")
        
    return "unknown"
