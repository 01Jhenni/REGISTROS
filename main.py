import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
from supabase import create_client, Client

SUPABASE_URL = "https://dirvujbiaqfvlxizjnax.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpcnZ1amJpYXFmdmx4aXpqbmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2MDIxNTgsImV4cCI6MjA1OTE3ODE1OH0.Tn6-iLi6LgQtKT_mK5cJeQYG8FDHN2pCkaNU1Bhzmas"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

USERS = {
    "IMPORT": "import123",
    "FISCAL": "fisc123"
}

PERMISSIONS = {
    "IMPORT": {"can_register": True, "can_view": True},
    "FISCAL": {"can_register": False, "can_view": True}
}

def login():
    st.title("🔐 Login")
    username = st.text_input("Usuário:")
    password = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['permissions'] = PERMISSIONS.get(username, {"can_register": False, "can_view": False})
        else:
            st.error("Usuário ou senha incorretos")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['permissions'] = {"can_register": False, "can_view": False}

if not st.session_state['logged_in']:
    login()
    st.stop()

def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

def insert_registro(empresa, tipo_arquivo, imagem_base64, descricao):
    status = "pendente" if imagem_base64 or descricao else "ok"
    data = {
        "empresa": empresa,
        "tipo_arquivo": tipo_arquivo,
        "imagem_base64": imagem_base64,
        "descricao": descricao,
        "status": status
    }
    response = supabase.table('registro').insert(data).execute()
    return response


def fetch_registro(filtro_empresa=None, filtro_status=None):
    query = supabase.table('registro').select("*")
    if filtro_empresa:
        query = query.in_("empresa", filtro_empresa)
    if filtro_status:
        query = query.in_("status", filtro_status)
    response = query.execute()
    if hasattr(response, "error") and response.error:
        st.error(f"Erro ao buscar dados: {response.error.message}")
        return pd.DataFrame()
    return pd.DataFrame(response.data)


def update_status_registro(registro_id, novo_status):
    response = supabase.table('registro').update({"status": novo_status}).eq('id', registro_id).execute()
    return response

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

tabs = []
if st.session_state['permissions']['can_register']:
    tabs.append("Registrar Importação")
if st.session_state['permissions']['can_view']:
    tabs.append("Visualizar Registro")

abas = st.tabs(tabs)

for idx, nome_aba in enumerate(tabs):
    with abas[idx]:
        if nome_aba == "Registrar Importação":
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

        elif nome_aba == "Visualizar Registro":
    st.header("Visualização e Filtros de Registros")

    df_todos = fetch_registro()
    empresas_unicas = df_todos['empresa'].unique() if not df_todos.empty else []
    status_unicos = df_todos['status'].unique() if not df_todos.empty else []

    st.subheader("Filtros")
    filtro_empresa = st.multiselect("Filtrar por Empresa:", empresas_unicas)
    filtro_status = st.multiselect("Filtrar por Status:", status_unicos)

    registro_filtrados = fetch_registro(filtro_empresa, filtro_status)

    st.subheader("Visualizar Detalhes dos Registros")

    if registro_filtrados.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
    else:
        for idx, registro in registro_filtrados.iterrows():
            with st.expander(f"🔍 {registro['empresa']} - {registro['tipo_arquivo']} - Status: {registro['status']}"):
                st.write(f"**Status:** {registro['status']}")

                if 'descricao' in registro and pd.notna(registro['descricao']) and registro['descricao'].strip() != '':
                    st.write(f"**Descrição:** {registro['descricao']}")
                else:
                    st.write("**Descrição:** Nenhuma descrição informada.")

                if pd.notna(registro["imagem_base64"]):
                    st.image(base64_to_image(registro["imagem_base64"]), caption="Imagem do Erro", use_container_width=True)

    st.subheader("Exportar Registros Filtrados")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar para Excel"):
            registro_filtrados.to_excel("registro_filtrados.xlsx", index=False)
            st.success("Arquivo 'registro_filtrados.xlsx' gerado com sucesso!")

    with col2:
        if st.button("Exportar para CSV"):
            registro_filtrados.to_csv("registro_filtrados.csv", index=False)
            st.success("Arquivo 'registro_filtrados.csv' gerado com sucesso!")
