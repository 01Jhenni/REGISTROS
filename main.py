import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import io
import base64

# Funções auxiliares
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

def init_db():
    conn = sqlite3.connect('registros.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT,
            tipo_arquivo TEXT,
            imagem_base64 TEXT,
            descricao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_registro(empresa, tipo_arquivo, imagem_base64, descricao):
    conn = sqlite3.connect('registros.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO registros (empresa, tipo_arquivo, imagem_base64, descricao)
        VALUES (?, ?, ?, ?)
    ''', (empresa, tipo_arquivo, imagem_base64, descricao))
    conn.commit()
    conn.close()

def fetch_registros(filtro_empresa=None, filtro_tipo=None):
    conn = sqlite3.connect('registros.db')
    query = 'SELECT * FROM registros WHERE 1=1'
    params = []
    if filtro_empresa:
        query += ' AND empresa IN ({})'.format(','.join('?'*len(filtro_empresa)))
        params += filtro_empresa
    if filtro_tipo:
        query += ' AND tipo_arquivo IN ({})'.format(','.join('?'*len(filtro_tipo)))
        params += filtro_tipo
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Inicializar banco de dados
init_db()

# Lista de tipos de arquivos
tipos_arquivos = [
    "NFE entrada", "NFE saída", "CTE entrada", "CTE saída", 
    "CTE cancelado", "SPED", "NFCE", "NFS tomado", "NFS prestado", "PLANILHA"
]

# Carregar lista de empresas do CSV anexado
empresas_df = pd.read_csv("C:\\Users\\Jhenni\\Downloads\\empresas (2).csv", encoding='latin1', sep=';')
empresas_df.columns = empresas_df.columns.str.strip().str.lower()

if 'nome' not in empresas_df.columns or 'cnpj' not in empresas_df.columns:
    st.error("CSV deve conter colunas 'nome' e 'cnpj'.")
    st.stop()

empresas = dict(zip(empresas_df['nome'], empresas_df['cnpj']))

st.set_page_config(page_title="Registro de Importações", layout="wide")
st.title("📑 Sistema de Registro e Consulta de Importações")

# Criar abas
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
    empresas_unicas = df_todos['empresa'].unique()
    tipos_unicos = df_todos['tipo_arquivo'].unique()

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
