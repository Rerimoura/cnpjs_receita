import streamlit as st
import pandas as pd

# Status mapping
SITUACAO_MAP = {
    '01': 'Nula', '1': 'Nula',
    '02': 'Ativa', '2': 'Ativa',
    '03': 'Suspensa', '3': 'Suspensa',
    '04': 'Inapta', '4': 'Inapta',
    '08': 'Baixada', '8': 'Baixada'
}

import duckdb

# ... (Status mapping remains) ...

@st.cache_data
def load_municipios():
    import os
    import subprocess
    
    # Get absolute path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'municipios.xlsx')
    temp_path = os.path.join(base_dir, 'municipios_temp_app.xlsx')
    fallback_path = os.path.join(base_dir, 'municipios_fallback.xlsx')
    
    status_msg = None # Tuple (type, msg)

    try:
        # Try reading directly
        df_mun = pd.read_excel(file_path, usecols=['MUNICIPIO', 'NOME_MUNICIPIO'])
    except PermissionError:
        # If locked, try copy to temp
        try:
            cmd = f'copy "{file_path}" "{temp_path}"'
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            df_mun = pd.read_excel(temp_path, usecols=['MUNICIPIO', 'NOME_MUNICIPIO'])
        except Exception:
            # Try fallback
            if os.path.exists(fallback_path):
                try:
                    df_mun = pd.read_excel(fallback_path, usecols=['MUNICIPIO', 'NOME_MUNICIPIO'])
                    status_msg = ("warning", "Aviso: Usando arquivo de backup para municípios (Original bloqueado).")
                except Exception as e:
                     return {}, ("error", f"Erro ao acessar backup: {e}")
            else:
                return {}, ("error", "Erro: Arquivo municipios.xlsx bloqueado e backup não encontrado.")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    except Exception as e:
        return {}, ("error", f"Erro ao carregar municipios.xlsx: {e}")

    # Ensure code is string
    df_mun['MUNICIPIO'] = df_mun['MUNICIPIO'].astype(str)
    return dict(zip(df_mun['MUNICIPIO'], df_mun['NOME_MUNICIPIO'])), status_msg

st.set_page_config(page_title="Consulta CNPJ - MG", layout="wide")

st.title("Consulta CNPJ - Minas Gerais")
st.markdown("Busque por estabelecimentos ativos em MG utilizando o CNPJ.")

# Load only auxiliary data
mun_dict, mun_status = load_municipios()

if mun_status:
    type_, msg = mun_status
    if type_ == "error":
        st.error(msg)
    elif type_ == "warning":
        st.toast(msg)

if "cnpj_search" not in st.session_state:
    st.session_state.cnpj_search = ""

def clear_search():
    st.session_state.cnpj_search = ""

cnpj_input = st.text_input("Digite o CNPJ (apenas números):", max_chars=14, key="cnpj_search")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    search_clicked = st.button("Consultar")
with col_btn2:
    st.button("Limpar Nova Busca", on_click=clear_search)

if search_clicked and cnpj_input:
    # Query using DuckDB
    try:
        # Convert input to int for comparison
        search_cnpj = int(cnpj_input)
        
        # Query both parquet parts using wildcard
        query = f"SELECT * FROM 'estabelecimentos_mg_part*.parquet' WHERE CNPJ = {search_cnpj}"
        
        with st.spinner('Consultando base de dados...'):
            # execute query and fetch as dataframe
            con = duckdb.connect(database=':memory:')
            result = con.execute(query).df()
            con.close()
            
    except ValueError:
        st.warning("Por favor, digite apenas números válidos.")
        result = pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        result = pd.DataFrame()
    
    if not result.empty:
        item = result.iloc[0]
        
        st.success("CNPJ Encontrado!")
        st.markdown("---")
        
        # Display Address
        st.subheader("📍 Endereço")
        col1, col2 = st.columns(2)
        with col1:
            # Map municipipality code to name
            mun_code = str(item['municipio'])
            mun_name = mun_dict.get(mun_code, mun_code)
            
            st.metric("Município", mun_name)
            
            # Tipo + Logradouro
            tipo_log = item['tipo_de_logradouro'] if item['tipo_de_logradouro'] else ""
            log_nome = item['logradouro'] if item['logradouro'] else ""
            log_completo = f"{tipo_log} {log_nome}".strip()
            
            st.metric("Logradouro", log_completo)
        with col2:
            st.metric("Bairro", item['bairro'])
            st.metric("Número", item['numero'])
            
        st.markdown("---")
        
        # Display Status
        st.subheader("📋 Situação Cadastral")
        
        # Map status code to text
        sit_code = str(item['situacao_cadastral'])
        sit_text = SITUACAO_MAP.get(sit_code, f"Desconhecido ({sit_code})")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Situação", sit_text)
        with col4:
            st.metric("Data da Situação", item['data_situacao_cadastral'])
        
    else:
        st.warning("CNPJ não encontrado na base de dados de MG.")
        st.info("Verifique se o número está correto e se o estabelecimento pertence ao estado de Minas Gerais.")
