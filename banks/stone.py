import pandas as pd
import pdfplumber
import re
from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class StoneBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF da Stone.
        """
        extracted_data = []

        date_line_pattern = re.compile(r'^(\d{2}/\d{2}/\d{2,4})\s+(Entrada|Saída)\s+(.*?)(-?\s*R\$\s*[\d\.,]+)\s+(?:-?\s*R\$\s*[\d\.,]+)$')
        
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            lines = [L.strip() for L in text.split('\n') if L.strip()]
            
            in_transactions = False
            desc_buffer = []
            
            current_transaction = None
            
            for line in lines:
                if "DATA TIPO DESCRIÇÃO VALOR" in line:
                    in_transactions = True
                    desc_buffer = []
                    continue
                    
                if not in_transactions:
                    continue
                    
                # Fim do extrato
                if "Resumo da conta" in line or "Total de Saídas" in line:
                    if current_transaction:
                        current_transaction["DESCRIÇÃO"] = " ".join(current_transaction["desc_parts"]).strip()
                        extracted_data.append(current_transaction)
                        current_transaction = None
                    in_transactions = False
                    continue
                    
                # Ignorar cabeçalhos/rodapés de página no meio das transações
                if "Página" in line or "Emitido em" in line or "Período:" in line or "Ouvidoria" in line or "Nome Documento" in line or "Instituição Agência Conta" in line or "Stone Instituição de Pagamento" in line or line.startswith("Extrato de conta corrente") or line.startswith("Dados da conta") or line.startswith("DATA TIPO DESCRIÇÃO VALOR SALDO CONTRAPARTE"):
                    continue
                    
                match = date_line_pattern.match(line)
                if match:
                    if current_transaction:
                        current_transaction["DESCRIÇÃO"] = " ".join(current_transaction["desc_parts"]).strip()
                        extracted_data.append(current_transaction)
                        
                    date_str = match.group(1)
                    tipo = match.group(2)
                    desc_middle = match.group(3).strip()
                    val_str = match.group(4).strip()
                    
                    parsed_val = clean_value(val_str)
                    if tipo == "Saída" and parsed_val > 0:
                        parsed_val = -parsed_val
                        
                    # Build current transaction
                    current_desc_parts = desc_buffer.copy()
                    if desc_middle:
                        current_desc_parts.append(desc_middle)
                        
                    current_transaction = {
                        "DATA": clean_date(date_str),
                        "desc_parts": current_desc_parts,
                        "VALOR": parsed_val
                    }
                    
                    # Clear buffer
                    desc_buffer = []
                else:
                    # It's a description line
                    if "|" in line:
                        if current_transaction:
                            current_transaction["desc_parts"].append(line)
                        else:
                            desc_buffer.append(line)
                    else:
                        if current_transaction:
                            current_transaction["DESCRIÇÃO"] = " ".join(current_transaction["desc_parts"]).strip()
                            extracted_data.append(current_transaction)
                            current_transaction = None
                        desc_buffer.append(line)
                        
            # Final line if any
            if current_transaction:
                current_transaction["DESCRIÇÃO"] = " ".join(current_transaction["desc_parts"]).strip()
                extracted_data.append(current_transaction)

        df = pd.DataFrame(extracted_data, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        df = df.dropna(subset=['DATA'])
        return df
