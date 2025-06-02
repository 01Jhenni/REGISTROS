import streamlit as st
from PIL import Image
import io
import base64
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Configurações do Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Registro de Erros - HENRIQUE", layout="wide")
st.title("Registro de Erros - HENRIQUE")

def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_str: str) -> Image.Image:
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data))

def save_registro(empresa, tipo_arquivo, descricao, imagem_base64):
    data = {
        "empresa": empresa,
        "tipo_arquivo": tipo_arquivo,
        "descricao": descricao,
        "imagem_base64": imagem_base64,
        "data_hora": datetime.now().isoformat()
    }
    response = supabase.table("registros").insert(data).execute()
    return response

def fetch_registros():
    response = supabase.table("registros").select("*").execute()
    data = response.data
    return pd.DataFrame(data)

# Formulário para registro
with st.form("registro_form"):
    empresa = st.selectbox("Selecione a empresa", ["Henrique", "Henrique Import", "Auto Peças", "Henrique Auto Peças"])
    tipo_arquivo = st.selectbox("Selecione o tipo de arquivo", ["XML", "TXT", "OUTRO"])
    descricao = st.text_area("Descrição do erro", placeholder="Descreva o erro encontrado...")
    imagem = st.file_uploader("Upload de imagem (opcional)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("Salvar Registro")

    if submitted:
        imagem_base64 = None
        if imagem:
            image = Image.open(imagem)
            imagem_base64 = image_to_base64(image)
        
        save_registro(empresa, tipo_arquivo, descricao, imagem_base64)
        st.success("Registro salvo com sucesso!")

st.write("---")
st.header("📋 Registros Salvos")

# Filtros
registros_df = fetch_registros()

if not registros_df.empty:
    empresa_filtro = st.multiselect("Filtrar por empresa", registros_df["empresa"].unique(), default=registros_df["empresa"].unique())
    tipo_filtro = st.multiselect("Filtrar por tipo de arquivo", registros_df["tipo_arquivo"].unique(), default=registros_df["tipo_arquivo"].unique())

    registros_filtrados = registros_df[
        (registros_df["empresa"].isin(empresa_filtro)) &
        (registros_df["tipo_arquivo"].isin(tipo_filtro))
    ]

    for idx, registro in registros_filtrados.iterrows():
        with st.expander(f"🔍 {registro['empresa']} - {registro['tipo_arquivo']}"):
            if 'descricao' in registro and pd.notna(registro['descricao']) and registro['descricao'].strip() != '':
                st.write(f"**Descrição:** {registro['descricao']}")
            else:
                st.write("**Descrição:** Nenhuma descrição informada.")

            if "imagem_base64" in registro and pd.notna(registro["imagem_base64"]):
                st.image(base64_to_image(registro["imagem_base64"]), caption="Imagem do Erro", use_container_width=True)
            else:
                st.write("**Imagem:** Nenhuma imagem anexada.")

else:
    st.info("Nenhum registro encontrado.")
