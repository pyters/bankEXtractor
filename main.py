import streamlit as st
import pandas as pd
import tempfile
import os
import io

from core.bank_detector import detect_bank
from banks.btg import BtgBank

st.set_page_config(page_title="Joicont PDF -> Excel", page_icon="📄", layout="centered")

# Custom CSS — Premium Dark Theme (compatível com config.toml)
st.markdown("""
<style>
    /* Botões de ação principais */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #4F8BF9, #3a6fd4);
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 8px rgba(79,139,249,0.4);
        transition: 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    /* Botão de download */
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #28a745, #1e7e34);
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 8px rgba(40,167,69,0.4);
        transition: 0.2s ease;
    }
    .stDownloadButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    /* Abas */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# Navegação na Sidebar
with st.sidebar:
    st.title("📂 Navegação")
    pagina = st.radio(
        "Ir para:",
        ["🚀 Processar", "🏦 Bancos Suportados", "📖 Como Usar", "ℹ️ Sobre"],
        label_visibility="collapsed"
    )

# --- Página: Processar ---
if pagina == "🚀 Processar":
    st.title("Conversor Joicont 📄->📊")
    st.markdown("Transforme extratos bancários em PDF em planilhas padronizadas do Excel com **zero atrito**.")

    uploaded_file = st.file_uploader("Arraste e solte o extrato em PDF aqui", type=["pdf"])

    if uploaded_file is not None:
        st.info(f"Arquivo recebido: **{uploaded_file.name}**")
        
        with st.spinner("Analisando o arquivo e extraindo dados..."):
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
                    
                    # 2. Strategy: Escolhe o extrator (Factory)
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
                            
                            st.subheader("Prévia dos Dados")
                            st.dataframe(df_resultado.head(10))
                            
                            # 4. Download Excel
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
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

# --- Página: Bancos Suportados ---
elif pagina == "🏦 Bancos Suportados":
    st.title("🏦 Bancos Suportados")
    st.markdown("""
    Atualmente suportamos a extração automática dos seguintes bancos:

    | Banco | Método de Extração |
    |---|---|
    | BTG Pactual | Tabelas Nativas |
    | Banco do Brasil (BB) | Regex Linha a Linha |
    | Bradesco | Fatiamento de Texto |
    | Sicredi | Tabelas Nativas |
    | Banco Inter | Regex Mista |
    | Nubank PJ | Regex Lookahead |
    | Asaas | Regex Invertida |
    | Acredicoop | Regex por Colunas |

    *Trabalhamos constantemente para adicionar novas instituições.*
    """)

# --- Página: Como Usar ---
elif pagina == "📖 Como Usar":
    st.title("📖 Como Usar")
    st.markdown("""
    ### Passo a Passo

    1. Clique em **🚀 Processar** na barra lateral.
    2. Arraste e solte o seu arquivo PDF do extrato bancário na área indicada.
    3. Aguarde o sistema identificar o banco e processar os dados automaticamente.
    4. Confira a prévia dos lançamentos exibida na tela.
    5. Clique em **⬇️ Baixar Planilha Excel** para salvar o resultado.

    ---
    ### Dicas
    - Se o sistema não identificar o seu banco, verifique se o PDF **não possui senha**.
    - Use o botão **🔄 Novo Extrato (Resetar)** para limpar e processar um novo arquivo rapidamente.
    - Apenas arquivos no formato `.pdf` são aceitos.
    """)

# --- Página: Sobre ---
elif pagina == "ℹ️ Sobre":
    st.title("ℹ️ Sobre o bankEXtractor")
    
    st.markdown("""
    ### Propósito
    Este software foi desenvolvido para automatizar a conversão de extratos bancários em PDF (de diversas instituições) para planilhas Excel padronizadas, eliminando o trabalho manual de digitação e facilitando a análise contábil.

    ---
    ### Informações do Desenvolvedor
    - **Autor:** Pyter Ely da Silva
    - **E-mail:** [pyter.ely@gmail.com](mailto:pyter.ely@gmail.com)
    
    ---
    ### Detalhes do Software
    - **Versão:** 0.1
    - **Data de Release:** 02 de Março de 2026
    - **Status:** Beta (Piloto)
    """)
