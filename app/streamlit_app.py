import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Cargar clave de API desde .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Configuración general
st.set_page_config(page_title="Conecta Bien", page_icon="🧠")
st.title("🧠 Conecta Bien")
st.markdown("Mejorá tu comunicación con IA")

# Inicializar puntos
if "puntos" not in st.session_state:
    st.session_state.puntos = 0

# --- Análisis de comunicación ---
st.header("🔍 Analiza tu comunicación")
texto = st.text_area("Escribí tu mensaje:")

if st.button("Analizar") and texto:
    with st.spinner("Analizando con Gemini..."):
        prompt = f"""
        Analiza el siguiente texto y devolveme un JSON con estas claves exactas:
        - "tono" (ej: positivo, negativo, agresivo, etc.)
        - "claridad" (número entre 0 y 1)
        - "emociones" (lista de emociones)
        - "sugerencias" (consejos para mejorar la comunicación)

        Texto: "{texto}"

        Respondé únicamente con el JSON, sin explicaciones.
        """
        try:
            respuesta = model.generate_content(prompt)
            st.code(respuesta.text, language="json")  # Mostrar respuesta para debug

            resultado = json.loads(respuesta.text)

            st.success("Análisis completo")
            st.markdown(f"**Tono:** {resultado['tono']}")
            st.markdown(f"**Claridad:** {resultado['claridad']}")
            st.markdown(f"**Emociones:** {', '.join(resultado['emociones'])}")
            st.markdown(f"**Sugerencias:** {resultado['sugerencias']}")
            st.session_state.puntos += 10
        except Exception as e:
            st.error("Gemini no devolvió JSON válido. Revisá el prompt o el texto.")
            st.exception(e)

# --- Generar ejercicio personalizado ---
if texto and st.button("🎯 Generar ejercicio"):
    with st.spinner("Generando ejercicio..."):
        prompt = f"""
        Basado en este mensaje, generá un ejercicio de comunicación y devolvelo en JSON con estas claves exactas:
        - "tipo" (asertividad, escucha activa, empatía, etc.)
        - "descripcion" (instrucciones claras)

        Mensaje: "{texto}"

        Respondé únicamente con el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            st.code(respuesta.text, language="json")  # Mostrar respuesta para debug

            ejercicio = json.loads(respuesta.text)
            st.markdown(f"**Tipo:** {ejercicio['tipo']}")
            st.markdown(ejercicio['descripcion'])
            st.session_state.puntos += 5
        except Exception as e:
            st.error("Gemini no devolvió JSON válido. Revisá el prompt o el texto.")
            st.exception(e)

# --- Chat con feedback ---
st.header("💬 Practicá con el Chatbot")
contexto = st.selectbox("Contexto", ["pareja", "trabajo", "familia"])
mensaje = st.text_input("Tu mensaje para el chatbot:")

if st.button("Enviar al chatbot") and mensaje:
    with st.spinner("Pensando respuesta..."):
        prompt = f"""
        Simulá una conversación en el contexto "{contexto}".
        Respondé al siguiente mensaje con un JSON que contenga exactamente:
        - "respuesta": tu mensaje como chatbot
        - "feedback": evaluación de la comunicación del usuario (tono, claridad, sugerencias)

        Usuario dijo: "{mensaje}"

        Solo el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            st.code(respuesta.text, language="json")  # Mostrar respuesta para debug

            resultado = json.loads(respuesta.text)
            st.markdown(f"**Respuesta del bot:** {resultado['respuesta']}")
            st.markdown(f"**Feedback:** {resultado['feedback']}")
            st.session_state.puntos += 5
        except Exception as e:
            st.error("Gemini no devolvió JSON válido. Revisá el prompt o el texto.")
            st.exception(e)

# --- Puntos acumulados ---
st.sidebar.title("🎮 Gamificación")
st.sidebar.markdown(f"**Puntos acumulados:** {st.session_state.puntos}")
