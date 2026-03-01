import streamlit as st
import pandas as pd
import tempfile
import os
import io

from core.bank_detector import detect_bank
from banks.btg import BtgBank

st.set_page_config(page_title="Joicont PDF -> Excel", page_icon="📄", layout="centered")

st.title("Conversor Joicont 📄->📊")
st.markdown("Transforme extratos bancários em PDF em planilhas padronizadas do Excel com **zero atrito**.")

uploaded_file = st.file_uploader("Arraste e solte o extrato em PDF aqui", type=["pdf"])

if uploaded_file is not None:
    st.info(f"Arquivo recebido: **{uploaded_file.name}**")
    
    with st.spinner("Analisando o arquivo e extraindo dados..."):
        # Salva o arquivo temporariamente no disco para leitura limpa com pdfplumber
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        try:
            # 1. Identifica o Banco
            bank_id = detect_bank(tmp_path)
            
            if bank_id == "unknown":
                st.error("Ops! Não consegui identificar qual banco é este PDF. É possível que não seja suportado ainda.")
            else:
                st.success(f"Banco identificado: **{bank_id.upper()}**")
                
                # 2. Strategy: Escolhe o extrator (Factory provisória)
                extractor = None
                if bank_id == "btg":
                    extractor = BtgBank()
                elif bank_id == "bb":
                    from banks.bb import BbBank
                    extractor = BbBank()
                elif bank_id == "bradesco":
                    from banks.bradesco import BradescoBank
                    extractor = BradescoBank()
                elif bank_id == "sicredi":
                    from banks.sicredi import SicrediBank
                    extractor = SicrediBank()
                elif bank_id == "inter":
                    from banks.inter import InterBank
                    extractor = InterBank()
                elif bank_id == "nubank":
                    from banks.nubank import NubankBank
                    extractor = NubankBank()
                elif bank_id == "asaas":
                    from banks.asaas import AsaasBank
                    extractor = AsaasBank()
                elif bank_id == "acredicoop":
                    from banks.acredicoop import AcredicoopBank
                    extractor = AcredicoopBank()

                if extractor:
                    # 3. Extrai os dados em DataFrame
                    df_resultado = extractor.extract(tmp_path)
                    
                    if df_resultado.empty:
                        st.warning("A extração rodou, mas nenhuma transação foi encontrada. O PDF pode estar vazio ou o formato mudou.")
                    else:
                        st.success(f"Extração concluída! {len(df_resultado)} lançamentos encontrados.")
                        
                        # Mostra um preview rápido
                        st.subheader("Prévia dos Dados")
                        st.dataframe(df_resultado.head(10))
                        
                        # 4. Oferece o Download em Excel na memória
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_resultado.to_excel(writer, index=False, sheet_name='Extrato')
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            label="⬇️ Baixar Planilha Excel",
                            data=excel_data,
                            file_name=f"Extrato_{bank_id.upper()}_Formatado.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error(f"Extrator para o banco {bank_id} ainda não foi implementado!")
                    
        except Exception as e:
            st.error(f"Ocorreu um erro durante a extração: {str(e)}")
            
        finally:
            # Limpa o arquivo temp
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
