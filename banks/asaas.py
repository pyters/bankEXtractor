import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class AsaasBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Asaas.
        O Asaas imprime um texto contínuo onde a linha da transação sempre termina com R$ [VALOR].
        As descrições podem quebrar em várias linhas *antes* da linha que contém o valor.
        A data pode vir na primeira linha da descrição ou na última junto com o valor.
        """
        extracted_data = []

        date_pattern = re.compile(r'^(\d{2}/\d{2}/\d{4})')
        money_suffix_pattern = re.compile(r'R\$\s*([\-\+]?\s*[\d\.]*,\d{2})$')

        with pdfplumber.open(filepath) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            lines = text.split('\n')
            
            i = 0
            # Ignorar o cabeçalho fixo até "Data Movimentações Valor"
            while i < len(lines):
                if "Data Movimentações Valor" in lines[i]:
                    i += 1
                    break
                i += 1
                
            desc_acumulada = ""
            row_date = None
            
            while i < len(lines):
                segment = lines[i].strip()
                if not segment:
                    i += 1
                    continue
                if segment.startswith("Saldo final do período") or segment.startswith("Resumo"):
                    break # Fim absoluto das transações
                    
                # Extraindo data se estiver no início deste segmento
                d_match = date_pattern.search(segment)
                if d_match:
                    row_date = d_match.group(1)
                    segment = segment.replace(row_date, "").strip()
                    
                m_suffix = money_suffix_pattern.search(segment)
                if m_suffix:
                    value_str = m_suffix.group(1).replace(' ', '')
                    segment = segment[:m_suffix.start()].strip()
                    
                    if segment:
                        desc_acumulada += " " + segment
                        
                    desc_clean = desc_acumulada.strip().replace('"', '')
                    extracted_data.append({
                        "DATA": clean_date(row_date),
                        "DESCRIÇÃO": desc_clean,
                        "VALOR": clean_value(value_str)
                    })
                    
                    # Resetar acumuladores para a próxima transação
                    desc_acumulada = ""
                    # row_date não reseta pois algumas transações no Asaas no mesmo dia podem vir sem a string de data explícita (Herdam a anterior)
                    
                else:
                    # É apenas um pedaço de descrição de uma transação futura que vai fechar quando achar o valor
                    if segment != "Data Movimentações Valor" and not "Saldo inicial do período" in segment:
                        desc_acumulada += " " + segment
                        
                i += 1

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        df = df.dropna(subset=['DATA'])
        return df
