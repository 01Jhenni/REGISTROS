import streamlit as st
import pandas as pd
import base64
from supabase import create_client, Client
from PIL import Image
import io

from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")


# Função para converter imagem para base64
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# Função para converter base64 para imagem
def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data))

# Função para inserir registro com status
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

# Função para buscar registros com filtros
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

# Função para atualizar status
def update_status(registro_id, novo_status):
    response = supabase.table('registro').update({"status": novo_status}).eq('id', registro_id).execute()
    return response

# Título principal
st.title("Sistema de Registros")

# Seleção de abas
abas = ["Cadastrar Registro", "Visualizar Registro"]
nome_aba = st.sidebar.radio("Escolha a opção:", abas)

# Aba de Cadastro
if nome_aba == "Cadastrar Registro":
    st.header("Cadastro de Novo Registro")

    empresa = st.text_input("Empresa")
    tipo_arquivo = st.selectbox("Tipo de Arquivo", ["XML", "PDF", "Imagem"])
    descricao = st.text_area("Descrição do Erro")

    imagem_file = st.file_uploader("Upload de Imagem (opcional)", type=["png", "jpg", "jpeg"])

    if imagem_file:
        imagem_base64 = image_to_base64(imagem_file)
    else:
        imagem_base64 = None

    if st.button("Cadastrar"):
        response = insert_registro(empresa, tipo_arquivo, imagem_base64, descricao)
        if hasattr(response, "error") and response.error:
            st.error(f"Erro ao inserir registro: {response.error.message}")
        else:
            st.success("Registro cadastrado com sucesso!")

# Aba de Visualização
elif nome_aba == "Visualizar Registro":
    st.header("Visualização e Filtros de Registros")

    df_todos = fetch_registro()
    empresas_unicas = df_todos['empresa'].unique() if not df_todos.empty else []
    status_unicos = df_todos['status'].unique() if not df_todos.empty else []

    st.subheader("Filtros")
    filtro_empresa = st.multiselect("Filtrar por Empresa:", empresas_unicas)
    filtro_status = st.multiselect("Filtrar por Status:", status_unicos)

    registros_filtrados = fetch_registro(filtro_empresa, filtro_status)

    st.subheader("Visualizar Detalhes dos Registros")

    if registros_filtrados.empty:
        st.info("Nenhum registro encontrado com os filtros selecionados.")
    else:
        for idx, registro in registros_filtrados.iterrows():
            with st.expander(f"🔍 {registro['empresa']} - {registro['tipo_arquivo']} - Status: {registro['status']}"):
                st.write(f"**Status:** {registro['status']}")

                if 'descricao' in registro and pd.notna(registro['descricao']) and registro['descricao'].strip() != '':
                    st.write(f"**Descrição:** {registro['descricao']}")
                else:
                    st.write("**Descrição:** Nenhuma descrição informada.")

                if pd.notna(registro["imagem_base64"]):
                    st.image(base64_to_image(registro["imagem_base64"]), caption="Imagem do Erro", use_container_width=True)

                if registro['status'] == 'pendente':
                    if st.button(f"Marcar como OK - ID {registro['id']}", key=f"ok_{registro['id']}"):
                        response = update_status(registro['id'], "ok")
                        if hasattr(response, "error") and response.error:
                            st.error(f"Erro ao atualizar status: {response.error.message}")
                        else:
                            st.success(f"Status do registro {registro['id']} atualizado para 'ok'.")
                            st.experimental_rerun()

    st.subheader("Exportar Registros Filtrados")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar para Excel"):
            registros_filtrados.to_excel("registro_filtrados.xlsx", index=False)
            st.success("Arquivo 'registro_filtrados.xlsx' gerado com sucesso!")

    with col2:
        if st.button("Exportar para CSV"):
            registros_filtrados.to_csv("registro_filtrados.csv", index=False)
            st.success("Arquivo 'registro_filtrados.csv' gerado com sucesso!")
