import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class InterBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Banco Inter.
        O extrato do Inter PJ possui uma estrutura de texto crua.
        """
        extracted_data = []
        
        # Mapeamento de meses por extenso
        meses = {
            "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03", "abril": "04",
            "maio": "05", "junho": "06", "julho": "07", "agosto": "08", 
            "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
        }

        # Exemplo: 6 de Dezembro de 2024
        date_pattern = re.compile(r'^(\d{1,2})\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4})')
        # Exemplo: Pagamento -R$ 440,00 -R$ 5.378,16
        tx_pattern = re.compile(r'^(.*?)\s+([\-]?R\$?\s*[\d\.,]+)\s+([\-]?R\$?\s*[\d\.,]+)$')
        
        current_date_str = None

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                for line in text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    d_match = date_pattern.match(line)
                    if d_match:
                        dia = d_match.group(1).zfill(2)
                        mes_nome = d_match.group(2).lower()
                        ano = d_match.group(3)
                        mes_num = meses.get(mes_nome, "01")
                        current_date_str = f"{dia}/{mes_num}/{ano}"
                        continue
                    
                    t_match = tx_pattern.match(line)
                    if t_match:
                        desc_str = t_match.group(1).strip()
                        val_str = t_match.group(2).strip()
                        
                        # Limpa strings sujas na descrição do Inter
                        desc_str = desc_str.replace('"', '')
                        
                        extracted_data.append({
                            "DATA": current_date_str,
                            "DESCRIÇÃO": desc_str,
                            "VALOR": clean_value(val_str)
                        })

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        df = df.dropna(subset=['DATA'])
        return df
