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
                
            # Nubank deve vir ANTES de Sicredi/Acredicoop — o PDF do Nubank pode conter
            # a palavra 'sicredi' ou 'acredi' no corpo das transações (ex: transferência para Sicredi).
            # 'total de entradas' + 'total de saídas' são exclusivos do layout Nubank PJ.
            if "nubank" in text or "nu pagamentos" in text or ("total de entradas" in text and "total de saídas" in text):
                return "nubank"

            # Acredicoop deve vir ANTES do Sicredi — ambos têm 'cooperativa' e 'conta' no texto
            if "acredicoop" in text or "acredi" in text:
                return "acredicoop"

            # Sicredi: exige a palavra 'sicredi' explicitamente para não confundir com outros bancos
            if "sicredi" in text:
                return "sicredi"
                
            if "instituição: banco inter" in text or "banco inter" in text:
                return "inter"
                
            if "asaas" in text or "data movimentações valor" in text:
                return "asaas"
                
    except Exception as e:
        print(f"Erro ao ler PDF para identificação: {e}")
        
    return "unknown"
