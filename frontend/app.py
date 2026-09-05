import streamlit as st
import requests


st.title("🤖 AlToque AI")

st.write(
    "Asistente preventivo para prediabetes"
)


user_id = st.number_input(
    "Usuario",
    value=1
)


message = st.text_input(
    "Escribe tu consulta"
)


if st.button("Enviar"):


    response = requests.post(

        "http://localhost:8000/api/v1/chat",

        json={

            "user_id": user_id,

            "message": message

        }

    )


    if response.status_code == 200:

        data = response.json()

        st.success(
            data["response"]
        )

    else:

        st.error(
            "Error en el servidor"
        )