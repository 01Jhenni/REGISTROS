
import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
from supabase import create_client, Client

# --- Configurações Supabase ---
SUPABASE_URL = "https://seu-projeto.supabase.co"  # Substitua pela sua URL Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpcnZ1amJpYXFmdmx4aXpqbmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2MDIxNTgsImV4cCI6MjA1OTE3ODE1OH0.Tn6-iLi6LgQtKT_mK5cJeQYG8FDHN2pCkaNU1Bhzmas"                      # Substitua pela sua chave de API
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Usuários e senhas ---
USERS = {
    "IMPORT": "import123",
    "FISCAL": "fisc123"
}

def login():
    st.title("🔐 Login")
    username = st.text_input("Usuário:")
    password = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Usuário ou senha incorretos")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

if not st.session_state['logged_in']:
    login()
    st.stop()

# --- Funções auxiliares ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

# --- Funções Supabase ---
def insert_registro(empresa, tipo_arquivo, imagem_base64, descricao):
    data = {
        "empresa": empresa,
        "tipo_arquivo": tipo_arquivo,
        "imagem_base64": imagem_base64,
        "descricao": descricao
    }
    response = supabase.table('registros').insert(data).execute()
    return response

def fetch_registros(filtro_empresa=None, filtro_tipo=None):
    query = supabase.table('registros').select("*")
    if filtro_empresa:
        query = query.in_("empresa", filtro_empresa)
    if filtro_tipo:
        query = query.in_("tipo_arquivo", filtro_tipo)
    response = query.execute()
    if response.error:
        st.error(f"Erro ao buscar dados: {response.error.message}")
        return pd.DataFrame()
    return pd.DataFrame(response.data)

# --- Configurações iniciais ---
tipos_arquivos = [
    "NFE entrada", "NFE saída", "CTE entrada", "CTE saída", 
    "CTE cancelado", "SPED", "NFCE", "NFS tomado", "NFS prestado", "PLANILHA"
]

empresas_df = pd.read_csv("empresas (2).csv", encoding='latin1', sep=';')
empresas_df.columns = empresas_df.columns.str.strip().str.lower()

if 'nome' not in empresas_df.columns or 'cnpj' not in empresas_df.columns:
    st.error("CSV deve conter colunas 'nome' e 'cnpj'.")
    st.stop()

empresas = dict(zip(empresas_df['nome'], empresas_df['cnpj']))

st.set_page_config(page_title="Registro de Importações", layout="wide")
st.title(f"📑 Sistema de Registro e Consulta de Importações — Usuário: {st.session_state['username']}")

aba1, aba2 = st.tabs(["Registrar Importação", "Visualizar Registros"])

with aba1:
    st.header("Registrar uma nova importação")

    empresa = st.selectbox("Nome da Empresa:", list(empresas.keys()))
    cnpj = empresas[empresa]
    tipo_arquivo = st.selectbox("Tipo de Arquivo Importado:", tipos_arquivos)
    imagem_erro = st.file_uploader("Anexe uma imagem do erro (opcional):", type=["png", "jpg", "jpeg"])
    descricao = st.text_area("Descrição do erro (opcional):")

    if st.button("Registrar Importação"):
        imagem_base64 = None
        if imagem_erro:
            imagem_base64 = image_to_base64(imagem_erro)

        registro_empresa = f"{empresa} - {cnpj}"
        insert_registro(registro_empresa, tipo_arquivo, imagem_base64, descricao)
        st.success("Importação registrada com sucesso!")

with aba2:
    st.header("Visualização e Filtros de Registros")

    df_todos = fetch_registros()
    empresas_unicas = df_todos['empresa'].unique() if not df_todos.empty else []
    tipos_unicos = df_todos['tipo_arquivo'].unique() if not df_todos.empty else []

    st.subheader("Filtros")
    filtro_empresa = st.multiselect("Filtrar por Empresa:", empresas_unicas)
    filtro_tipo = st.multiselect("Filtrar por Tipo de Arquivo:", tipos_unicos)

    registros_filtrados = fetch_registros(filtro_empresa, filtro_tipo)

    st.subheader("Visualizar Detalhes dos Registros")

    if registros_filtrados.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
    else:
        for idx, registro in registros_filtrados.iterrows():
            with st.expander(f"🔍 {registro['empresa']} - {registro['tipo_arquivo']}"):
                if registro['descricao']:
                    st.write(f"**Descrição:** {registro['descricao']}")
                else:
                    st.write("**Descrição:** Nenhuma descrição informada.")
                if pd.notna(registro["imagem_base64"]):
                    st.image(base64_to_image(registro["imagem_base64"]), caption="Imagem do Erro", use_container_width=True)

    st.subheader("Exportar Registros Filtrados")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar para Excel"):
            registros_filtrados.to_excel("registros_filtrados.xlsx", index=False)
            st.success("Arquivo 'registros_filtrados.xlsx' gerado com sucesso!")

    with col2:
        if st.button("Exportar para CSV"):
            registros_filtrados.to_csv("registros_filtrados.csv", index=False)
            st.success("Arquivo 'registros_filtrados.csv' gerado com sucesso!")
 # Substitua pela sua URL Supabase
SUPABASE_KEY = "sua_api_key"                      # Substitua pela sua chave de API
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Usuários e senhas ---
USERS = {
    "IMPORT": "import123",
    "FISCAL": "fisc123"
}

def login():
    st.title("🔐 Login")
    username = st.text_input("Usuário:")
    password = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Usuário ou senha incorretos")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

if not st.session_state['logged_in']:
    login()
    st.stop()

# --- Funções auxiliares ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

# --- Funções Supabase ---
def insert_registro(empresa, tipo_arquivo, imagem_base64, descricao):
    data = {
        "empresa": empresa,
        "tipo_arquivo": tipo_arquivo,
        "imagem_base64": imagem_base64,
        "descricao": descricao
    }
    response = supabase.table('registros').insert(data).execute()
    return response

def fetch_registros(filtro_empresa=None, filtro_tipo=None):
    query = supabase.table('registros').select("*")
    if filtro_empresa:
        query = query.in_("empresa", filtro_empresa)
    if filtro_tipo:
        query = query.in_("tipo_arquivo", filtro_tipo)
    response = query.execute()
    if response.error:
        st.error(f"Erro ao buscar dados: {response.error.message}")
        return pd.DataFrame()
    return pd.DataFrame(response.data)

# --- Configurações iniciais ---
tipos_arquivos = [
    "NFE entrada", "NFE saída", "CTE entrada", "CTE saída", 
    "CTE cancelado", "SPED", "NFCE", "NFS tomado", "NFS prestado", "PLANILHA"
]

empresas_df = pd.read_csv("empresas (2).csv", encoding='latin1', sep=';')
empresas_df.columns = empresas_df.columns.str.strip().str.lower()

if 'nome' not in empresas_df.columns or 'cnpj' not in empresas_df.columns:
    st.error("CSV deve conter colunas 'nome' e 'cnpj'.")
    st.stop()

empresas = dict(zip(empresas_df['nome'], empresas_df['cnpj']))

st.set_page_config(page_title="Registro de Importações", layout="wide")
st.title(f"📑 Sistema de Registro e Consulta de Importações — Usuário: {st.session_state['username']}")

aba1, aba2 = st.tabs(["Registrar Importação", "Visualizar Registros"])

with aba1:
    st.header("Registrar uma nova importação")

    empresa = st.selectbox("Nome da Empresa:", list(empresas.keys()))
    cnpj = empresas[empresa]
    tipo_arquivo = st.selectbox("Tipo de Arquivo Importado:", tipos_arquivos)
    imagem_erro = st.file_uploader("Anexe uma imagem do erro (opcional):", type=["png", "jpg", "jpeg"])
    descricao = st.text_area("Descrição do erro (opcional):")

    if st.button("Registrar Importação"):
        imagem_base64 = None
        if imagem_erro:
            imagem_base64 = image_to_base64(imagem_erro)

        registro_empresa = f"{empresa} - {cnpj}"
        insert_registro(registro_empresa, tipo_arquivo, imagem_base64, descricao)
        st.success("Importação registrada com sucesso!")

with aba2:
    st.header("Visualização e Filtros de Registros")

    df_todos = fetch_registros()
    empresas_unicas = df_todos['empresa'].unique() if not df_todos.empty else []
    tipos_unicos = df_todos['tipo_arquivo'].unique() if not df_todos.empty else []

    st.subheader("Filtros")
    filtro_empresa = st.multiselect("Filtrar por Empresa:", empresas_unicas)
    filtro_tipo = st.multiselect("Filtrar por Tipo de Arquivo:", tipos_unicos)

    registros_filtrados = fetch_registros(filtro_empresa, filtro_tipo)

    st.subheader("Visualizar Detalhes dos Registros")

    if registros_filtrados.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
    else:
        for idx, registro in registros_filtrados.iterrows():
            with st.expander(f"🔍 {registro['empresa']} - {registro['tipo_arquivo']}"):
                if registro['descricao']:
                    st.write(f"**Descrição:** {registro['descricao']}")
                else:
                    st.write("**Descrição:** Nenhuma descrição informada.")
                if pd.notna(registro["imagem_base64"]):
                    st.image(base64_to_image(registro["imagem_base64"]), caption="Imagem do Erro", use_container_width=True)

    st.subheader("Exportar Registros Filtrados")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar para Excel"):
            registros_filtrados.to_excel("registros_filtrados.xlsx", index=False)
            st.success("Arquivo 'registros_filtrados.xlsx' gerado com sucesso!")

    with col2:
        if st.button("Exportar para CSV"):
            registros_filtrados.to_csv("registros_filtrados.csv", index=False)
            st.success("Arquivo 'registros_filtrados.csv' gerado com sucesso!")
