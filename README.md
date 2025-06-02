
# 📦 REGISTROS

**Aplicação web em Streamlit para registro e visualização de registros de importação, com backend na Supabase.**

---

## 📌 Visão Geral

**REGISTROS** é uma solução web moderna desenvolvida para **facilitar o registro e a visualização de registros de importação**.

Construída com **Streamlit** para oferecer uma interface rápida e interativa, e utilizando **Supabase** como banco de dados na nuvem, permite aos usuários:

✅ Cadastrar facilmente novos registros de importação
✅ Armazenar os dados de forma segura na **Supabase**
✅ Visualizar e explorar registros já cadastrados de maneira prática

---

## 🚀 Funcionalidades

* ⚡️ Interface web rápida e intuitiva utilizando **Streamlit**
* 🛢️ Integração com **Supabase** para armazenamento e recuperação de dados em tempo real
* 📝 Cadastro de **novos registros de importação** por meio de formulários
* 📊 **Visualização e consulta** de registros existentes
* 🔐 Backend seguro e escalável utilizando **PostgreSQL** via Supabase

---

## ⚙️ Tecnologias Utilizadas

* **Frontend**: Streamlit (Python)
* **Backend / Banco de Dados**: Supabase (PostgreSQL)
* **Comunicação com o banco**: Bibliotecas cliente do Supabase ou APIs REST

---

## 📂 Estrutura do Projeto

```
REGISTROS/
├── app.py               # Aplicação principal em Streamlit
├── supabase_client.py   # Configuração e consultas ao Supabase
├── requirements.txt     # Dependências do Python
├── README.md            # Documentação do projeto
└── .env                 # Credenciais do Supabase (não versionadas)
```

---

## 🛠️ Configuração e Instalação

1. **Clone o repositório**:

```bash
git clone https://github.com/01Jhenni/REGISTROS.git
cd REGISTROS
```

2. **Configure o Supabase**:

* Crie um projeto no [Supabase](https://supabase.io/)
* Configure o **schema do banco de dados** para armazenar os registros de importação
* Copie a **URL da API** e a **Chave Pública (Anon Key)**

3. **Crie um arquivo `.env`** com as credenciais do Supabase:

```
SUPABASE_URL=Sua_URL_do_Supabase
SUPABASE_KEY=Sua_Anon_Key
```

4. **Instale as dependências**:

```bash
pip install -r requirements.txt
```

5. **Execute a aplicação Streamlit**:

```bash
streamlit run app.py
```

---

## 🎯 Como Usar

* Acesse a interface web do Streamlit gerada pela aplicação.
* Utilize o formulário para **cadastrar novos registros de importação**.
* Visualize os registros cadastrados na mesma interface, com filtros e visualizações facilitadas.

---

## ✅ Pré-requisitos

* **Python 3.x**
* Conta e projeto no **Supabase**
* **Streamlit** e bibliotecas listadas no `requirements.txt`

---

## 💡 Possíveis Melhorias Futuras

* Implementar autenticação de usuários com o Supabase Auth
* Adicionar gráficos e relatórios estatísticos
* Exportação de registros para formatos como **Excel** ou **PDF**
* CRUD completo: edição e exclusão de registros

---

## 🙋‍♀️ Autora

**Jhennifer Ferreira Nascimento**

* GitHub: [@01Jhenni](https://github.com/01Jhenni)
* TikTok: [@01jhenni](https://www.tiktok.com/@01jhenni)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** — fique à vontade para usar, modificar e distribuir.

---

## ⭐️ Contribua!

Se gostou deste projeto, deixe uma **estrela ⭐ no GitHub**!
Pull requests e sugestões são sempre bem-vindos.

