import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class NubankBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Nubank PJ.
        O Relátório do Nubank não possui grides delimitadores, nem para extract_text(layout=True).
        Isso nos força a ler as quebras de linha raw e reagrupar transações quebradas (Multilinha).
        A data é declarada antes no formato '06 JAN 2025' e afeta todas as linhas abaixo.
        A direção do saldo (Positivo/Negativo) é inferida pelo Agrupador 'Total de entradas' ou 'Total de saídas'.
        """
        extracted_data = []

        # 06 JAN 2025
        date_pattern = re.compile(r'^(\d{2})\s+([A-Z]{3})\s+(\d{4})\s+')
        # Sufixos de valor da linha: "15.380,00" ou "- 15.380,00" ou "+ 15.380,00"
        money_suffix_pattern = re.compile(r'([\-\+]?\s*[\d\.]*,\d{2})$')

        meses = {
            "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
            "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
            "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
        }

        with pdfplumber.open(filepath) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            lines = text.split('\n')
            
            current_date_str = None
            current_group_type = None # "entrada" ou "saida"
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                    
                # Ignorar rodapés e cabeçalhos de folha intrusivos
                if "Tem alguma dúvida?" in line or "Ouvidoria:" in line or "Extrato gerado dia" in line:
                    i += 1
                    continue
                if line.startswith("SALVIANO ENGENHARIA"): # Ou cabeçalho de empresa
                    i += 1
                    continue
                if date_pattern.match(line) and "VALORES EM R$" in line:
                    i += 1
                    continue
                if line == "Movimentações":
                    i += 1
                    continue
                    
                d_match = date_pattern.match(line)
                if d_match:
                    dia = d_match.group(1).zfill(2)
                    mes_nome = d_match.group(2)
                    ano = d_match.group(3)
                    mes_num = meses.get(mes_nome, "01")
                    current_date_str = f"{dia}/{mes_num}/{ano}"
                    
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
                    
                if "Saldo do dia" in line or "Saldo inicial" in line or "Saldo final" in line:
                    i += 1
                    continue
                    
                m_suffix = money_suffix_pattern.search(line)
                if current_date_str and m_suffix:
                    value_str = m_suffix.group(1).replace(' ', '')
                    desc = line[:m_suffix.start()].strip()
                    
                    # Lookahead para descrições multilinha
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                            
                        # Quebras de bloco (Pára de concatenar)
                        if next_line.startswith('Saldo'): break
                        if "Total de saídas" in next_line or "Total de entradas" in next_line: break
                        if date_pattern.match(next_line): break
                        if "Tem alguma dúvida?" in next_line or "Ouvidoria:" in next_line or "Extrato gerado dia" in next_line: break
                        
                        # Se a próxima linha POSSUI um valor final de transação, ela é OUTRA transação
                        if money_suffix_pattern.search(next_line):
                            break
                            
                        # Limpa lixos textuais da desc
                        desc += " - " + next_line
                        j += 1
                        
                    # Fixar Sinal Baseado no Bloco de Agrupamento ("Total de saídas")
                    # Se for saída e não tiver o menos na string (as vezes vem cru "15.000,00"), forçamos negativo
                    if current_group_type == "saida" and not "-" in value_str:
                        value_str = "-" + value_str
                        
                    # Adicionar RDB como Débito (Aplicação RDB é dinheiro saindo da Conta Corrente pro Investimento)
                    if "Aplicação RDB" in desc and not "-" in value_str:
                        value_str = "-" + value_str
                        
                    extracted_data.append({
                        "DATA": current_date_str,
                        "DESCRIÇÃO": desc.replace('"', ''),
                        "VALOR": clean_value(value_str)
                    })
                    
                    i = j # Avança o ponteiro pelo tamanho do lookahead
                    continue
                    
                i += 1

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        df = df.dropna(subset=['DATA'])
        return df
