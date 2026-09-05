import streamlit as st
import requests


# -------------------------------
# Configuración página
# -------------------------------

st.set_page_config(
    page_title="AlToque AI",
    page_icon="🩺",
    layout="centered"
)


# -------------------------------
# Estilos CSS
# -------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f1117;
    }


    .title {
        font-size: 38px;
        font-weight: 700;
        color: white;
        margin-bottom: 0px;
    }


    .subtitle {
        color: #a0aec0;
        font-size: 16px;
        margin-bottom: 30px;
    }


    .user-message {

        background-color: #2b2d42;
        color:white;
        padding:15px;
        border-radius:12px;
        margin:10px 0;
        text-align:right;

    }


    .bot-message {

        background-color:#163d2a;
        color:#d1fae5;
        padding:15px;
        border-radius:12px;
        margin:10px 0;

    }


    </style>
    """,
    unsafe_allow_html=True
)



# -------------------------------
# Estado conversación
# -------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []



# -------------------------------
# Título
# -------------------------------

st.markdown(
    '<div class="title">🩺 AlToque AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Asistente preventivo inteligente para prediabetes'
    '</div>',
    unsafe_allow_html=True
)



# -------------------------------
# Sidebar paciente
# -------------------------------

with st.sidebar:


    st.header("Paciente")


    user_id = st.number_input(
        "Seleccionar usuario",
        min_value=1,
        max_value=3,
        value=1
    )


    st.divider()


    st.write(
        """
        Pacientes demo:

        🟢 1 - Ana Torres  
        🟡 2 - Carlos Perez  
        🔴 3 - Jose Ramirez
        """
    )



# -------------------------------
# Mostrar historial
# -------------------------------

for message in st.session_state.messages:


    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="user-message">
            {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            f"""
            <div class="bot-message">
            🩺 AlToque AI

            <br><br>

            {message["content"]}

            </div>
            """,
            unsafe_allow_html=True
        )



# -------------------------------
# Entrada usuario
# -------------------------------

prompt = st.chat_input(
    "Escribe tu consulta..."
)



if prompt:


    # Guardar mensaje usuario

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )



    # Enviar al backend


    response = requests.post(

        "http://localhost:8000/api/v1/chat",

        json={

            "user_id":user_id,

            "message":prompt

        }

    )


    if response.status_code == 200:

        answer = response.json()["response"]

    else:

        answer = (
            "Error conectando con AlToque AI"
        )



    # Guardar respuesta

    st.session_state.messages.append(

        {
            "role":"assistant",
            "content":answer
        }

    )


    st.rerun()