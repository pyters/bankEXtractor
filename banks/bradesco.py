import pandas as pd
import pdfplumber
import re

from core.formatador import clean_value, clean_date
from banks.base_bank import BaseBank

class BradescoBank(BaseBank):
    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Extrai dados do extrato PDF do Bradesco.
        O Bradesco não utiliza grids de pdf, apenas alinhamento de texto (layout=True).
        Um bloco de transação consiste em: [Pre-Text (opicional)] -> [Value Line] -> [Post-Text (opicional)]
        """
        extracted_data = []
        
        # Regex para identificar se um texto é puramente um valor monetário
        # Ex: "1.234,56", "-268,00", "0,00"
        money_pattern = re.compile(r'^[\-\d\.]*,\d{2}$')
        # Regex para extrair data dd/mm/yyyy
        date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')

        all_lines = []
        
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if not text:
                    continue
                
                for line in text.split('\n'):
                    if not line.strip():
                        continue
                        
                    # Divide a linha onde houver 2 ou mais espaços
                    cols = [col.strip() for col in re.split(r'\s{2,}', line) if col.strip()]
                    if not cols:
                        continue
                    
                    # Ignorar cabeçalhos de tabela recorrentes
                    first_col_lower = cols[0].lower()
                    if "agência" in first_col_lower or "extrato de:" in first_col_lower or "data" == first_col_lower or "total" in first_col_lower:
                        # Se acharmos Total, ignorar
                        continue
                    if "total" in line.lower() and "disponível" in line.lower():
                        continue
                    
                    # Verifica se é uma "Value Line" (última coluna é um valor monetário válido)
                    is_value_line = bool(money_pattern.match(cols[-1]))
                    
                    # Ignorar também totalizadores finais do PDF que não são transações
                    if is_value_line and len(cols) > 1 and "total" in cols[0].lower():
                        continue

                    all_lines.append({
                        "raw_cols": cols,
                        "is_value_line": is_value_line,
                        "raw_string": line.strip()
                    })

        # Processar blocos usando a heurística de agrupamento
        current_date_global = None
        
        # Agrupar pre-text, vl, post-text
        value_lines_indices = [i for i, row in enumerate(all_lines) if row["is_value_line"]]
        
        for idx in range(len(value_lines_indices)):
            vl_idx = value_lines_indices[idx]
            vl_row = all_lines[vl_idx]
            
            # Descobrir pre-text
            pre_text_parts = []
            start_search = value_lines_indices[idx-1] + 1 if idx > 0 else 0
            # Se há linhas de texto puras IMEDIATAMENTE antes da Value Line e DEPOIS da Value line anterior,
            # Regra heurística descrita: a ÚLTIMA dessas linhas é o pre-text da atual.
            # O restante das linhas são o post-text da anterior.
            text_lines_between = all_lines[start_search:vl_idx]
            
            if len(text_lines_between) > 0:
                # O pre-text dessa ValueLine é sempre a ÚLTIMA linha de texto do intervalo
                pre_text_parts.append(" ".join(text_lines_between[-1]["raw_cols"]))
                
                # Aproveitar o loop pra atribuir o post-text na value line ANTERIOR se existir!
                if idx > 0:
                    # As linhas text_lines_between[:-1] pertencem a idx-1 como post-text
                    extracted_data[-1]["post_text_parts"].extend([" ".join(row["raw_cols"]) for row in text_lines_between[:-1]])
            
            # Parse dos atributos da Value Line atual
            cols = vl_row["raw_cols"]
            
            # A data só aparece na ValueLine ou na descrição associada.
            # Vamos tentar procurar a data no cols[0]
            date_match = date_pattern.search(cols[0])
            if date_match:
                current_date_global = date_match.group(0)
            
            vl_desc_parts = []
            value_str = "0,00"
            
            if "SALDO ANTERIOR" in cols[0]:
                vl_desc_parts.append("SALDO ANTERIOR")
                value_str = "0,00"
            else:
                # Os valores são Crédito e Débito.
                # Geralmente cols[-1] é Saldo. 
                # O valor transferido fica na cols[-2] ou cols[-3] dependendo do documento
                # Vamos simplificar: se pegarmos o elemento antes do saldo que valida como money_pattern!
                # Nem sempre o penúltimo é o valor. Pode ter apenas Saldo? Não, uma transação tem valor.
                # Pegar o penúltimo elemento. Se for money_pattern, é o valor.
                
                # Tentar achar o valor percorrido de trás pra frente ignorando o último (Saldo).
                for c in reversed(cols[:-1]):
                    if money_pattern.match(c):
                        value_str = c
                        break
                
                # E o texto do Lançamento que eventualmente esteja na Value Line?
                # Se há colunas no meio que não são money_pattern nem doc (ex: DOC = numeros), é desc
                for c in cols:
                    if not money_pattern.match(c) and not date_pattern.match(c):
                        if c.isdigit() and len(c) > 4: # Ignorar documentos numéricos longos
                            continue
                        vl_desc_parts.append(c)

            # Criar registro base
            extracted_data.append({
                "DATA": current_date_global,
                "pre_text_parts": pre_text_parts,
                "vl_desc_parts": vl_desc_parts,
                "post_text_parts": [], # Será preenchido na próxima iteração
                "VALOR_RAW": value_str
            })

        # Adicionar o post-text dos itens que vêm DEPOIS da última Value Line
        if len(value_lines_indices) > 0:
            last_vl_idx = value_lines_indices[-1]
            extracted_data[-1]["post_text_parts"] = [" ".join(row["raw_cols"]) for row in all_lines[last_vl_idx+1:]]

        # Montar o DataFrame final formatado
        final_rows = []
        for item in extracted_data:
            # Concatenar as descrições na ordem: Pre-Text + ValueLine Text + Post-Text
            full_desc_parts = item["pre_text_parts"] + item["vl_desc_parts"] + item["post_text_parts"]
            full_desc = " - ".join([p for p in full_desc_parts if p])
            
            final_rows.append({
                "DATA": clean_date(item["DATA"]) if item["DATA"] else None,
                "DESCRIÇÃO": full_desc,
                "VALOR": clean_value(item["VALOR_RAW"])
            })

        df = pd.DataFrame(final_rows, columns=["DATA", "DESCRIÇÃO", "VALOR"])
        # Adicionar filtro para remover lixos do extrato que não possuem data (como cabeçalhos de tabela isolados)
        df = df.dropna(subset=['DATA'])
        return df
