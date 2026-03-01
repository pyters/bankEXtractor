import pdfplumber
import re

def investigate_asaas_pdf(filepath):
    print(f"Investigating: {filepath}")
    # Ex: 02/12/2024
    date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})')
    # Valor no fim Ex: R$ 683,00 ou R$ -1,99
    money_suffix_pattern = re.compile(r'R\$\s*([\-\+]*\s*[\d\.]*,\d{2})$')
    
    with pdfplumber.open(filepath) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        lines = text.split('\n')
        
        parsed_items = []
        i = 0
        
        # Ignorar o cabeçalho fixo até "Data Movimentações Valor"
        while i < len(lines):
            if "Data Movimentações Valor" in lines[i]:
                i += 1
                break
            i += 1
            
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Identificação de Transação (Toda transação Asaas SEMPRE tem o valor no fim da última ou única linha)
            # Porém o Asaas inverte a ordem: as vezes a Data ta na linha debaixo, e o titulo em cima.
            # Olhando o log:
            # [8]: Taxa de mensageria - fatura nr. 479715020 Karin Juliana Bitencourt
            # [9]: 02/12/2024 R$ -0,99
            # Logo, a identificação do bloco se dá ao bater no valor. Tudo acima (desde o ultimo valor) é descrição!
            
            # Vamos acumular texto até bater no money suffix
            desc_acumulada = ""
            row_date = None
            
            while i < len(lines):
                segment = lines[i].strip()
                if not segment:
                    i += 1
                    continue
                if segment.startswith("Saldo final do período") or segment.startswith("Resumo"):
                    break # Fim real do extrato
                    
                # Extraindo data se estiver na linha (Pode estar na 1ª ou na última linha do bloco)
                d_match = date_pattern.search(segment)
                if d_match:
                    row_date = d_match.group(1)
                    segment = segment.replace(row_date, "").strip()
                    
                m_suffix = money_suffix_pattern.search(segment)
                if m_suffix:
                    value_str = m_suffix.group(1).replace(' ', '')
                    segment = segment[:m_suffix.start()].strip()
                    desc_acumulada += " " + segment
                    
                    parsed_items.append((row_date, desc_acumulada.strip(), value_str))
                    i += 1
                    break # Fim deste bloco de transação
                else:
                    # É só um pedaço de descrição
                    if segment != "Data Movimentações Valor":
                        desc_acumulada += " " + segment
                i += 1
                
        print("--- PARSED ITEMS ---")
        for it in parsed_items[:20]:
             print(f"[{it[0]}] {it[1]} -> {it[2]}")

if __name__ == "__main__":
    investigate_asaas_pdf("/home/pyter/Projects/bankEXtractor/tests/pdfs/Asaas.pdf")
