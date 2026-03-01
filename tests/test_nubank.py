import pdfplumber
import re

def investigate_nubank_pdf(filepath):
    print(f"Investigating: {filepath}")
    
    # 06 JAN 2025
    date_pattern = re.compile(r'^(\d{2})\s+([A-Z]{3})\s+(\d{4})\s+')
    # Regex para pegar o sufixo "15.380,00" ou "- 15.380,00"
    money_suffix_pattern = re.compile(r'([\-\+]?\s*[\d\.]*,\d{2})$')
    
    with pdfplumber.open(filepath) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        lines = text.split('\n')
        
        current_date = None
        current_group_type = None # "entrada" ou "saida"
        
        parsed_items = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            d_match = date_pattern.match(line)
            if d_match:
                current_date = f"{d_match.group(1)} {d_match.group(2)} {d_match.group(3)}"
                # Opcionalmente a linha da data do Nubank possui "Total de entradas + 16.265,94" na frente, vamos pular pro grupo.
                if "Total de entradas" in line:
                    current_group_type = "entrada"
                elif "Total de saídas" in line:
                    current_group_type = "saida"
                i += 1
                continue
                
            if "Total de saídas" in line:
                current_group_type = "saida"
                i += 1
                continue
            if "Total de entradas" in line:
                current_group_type = "entrada"
                i += 1
                continue
                
            if "Saldo do dia" in line or "Saldo inicial" in line or "Saldo final" in line or "Movimentações" in line:
                i += 1
                continue
                
            # É uma linha de transação (se for valor)
            # Como a transação quebra linha, pegamos da atual até achar a proxima ou um valor final!
            m_suffix = money_suffix_pattern.search(line)
            
            if current_date:
                # O Nubank coloca o titulo e o valor na PRIMEIRA linha, ou as vezes na quebra.
                # Ex 1: Transferência Recebida 16.265,94
                # Ex 2: Transferência enviada pelo Pix JOICONT CONTADORES E CONSULTORES 380,00
                #       ASSOCIADOS LTDA ME - 27.606.592/0001-46 -
                if m_suffix:
                    value_str = m_suffix.group(1)
                    desc = line[:m_suffix.start()].strip()
                    
                    # Vamos olhar as proximas linhas pra ver se elas Não tem valor (continuacao da desc)
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line or next_line.startswith('Saldo') or date_pattern.match(next_line):
                            break
                        if "Total de saídas" in next_line or "Total de entradas" in next_line:
                            break
                            
                        # Se a proxima linha POSSUI valor, então ela é outra transação!
                        if money_suffix_pattern.search(next_line):
                            break
                            
                        # É uma lina sem valor, logo é multiline description da atual
                        desc += " - " + next_line
                        j += 1
                        
                    # Applica sinal
                    if current_group_type == "saida" and not value_str.startswith('-'):
                        value_str = "-" + value_str
                        
                    parsed_items.append((current_date, desc, value_str))
                    i = j # Pula as linhas que engolimos
                    continue
                    
            i += 1

    print("--- PARSED ITEMS ---")
    for it in parsed_items[:20]:
         print(f"[{it[0]}] {it[1]} -> {it[2]}")

if __name__ == "__main__":
    investigate_nubank_pdf("/home/pyter/Projects/bankEXtractor/tests/pdfs/NU BANK.pdf")
