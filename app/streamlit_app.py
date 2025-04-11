import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Cargar clave de API desde .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")  # o "gemini-1.5-flash" si lo preferís

st.set_page_config(page_title="Conecta Bien", page_icon="🧠")
st.title("🧠 Conecta Bien")
st.markdown("Mejorá tu comunicación con IA")

# Inicializar puntos
if "puntos" not in st.session_state:
    st.session_state.puntos = 0

# --- Análisis de comunicación ---
st.header("🔍 Analiza tu comunicación")
texto = st.text_area("Escribí tu mensaje:")

if st.button("Analizar" and texto):
    with st.spinner("Analizando con Gemini..."):
        prompt = f"""
        Analiza este texto y devolveme un JSON con:
        - tono
        - claridad (de 0 a 1)
        - emociones
        - sugerencias para mejorar
        Texto: "{texto}"
        Solo el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            resultado = eval(respuesta.text)

            st.success("Análisis completo")
            st.markdown(f"**Tono:** {resultado['tono']}")
            st.markdown(f"**Claridad:** {resultado['claridad']}")
            st.markdown(f"**Emociones:** {', '.join(resultado['emociones'])}")
            st.markdown(f"**Sugerencias:** {resultado['sugerencias']}")
            st.session_state.puntos += 10
        except Exception as e:
            st.error(f"Error al analizar: {e}")

# --- Generar ejercicio personalizado ---
if texto and st.button("🎯 Generar ejercicio"):
    with st.spinner("Generando ejercicio..."):
        prompt = f"""
        Basado en este mensaje, generá un ejercicio de comunicación.
        Dame un JSON con:
        - tipo (asertividad, escucha activa, empatía, etc.)
        - descripcion (instrucciones claras)
        Mensaje: "{texto}"
        Solo el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            ejercicio = eval(respuesta.text)
            st.markdown(f"**Tipo:** {ejercicio['tipo']}")
            st.markdown(ejercicio['descripcion'])
            st.session_state.puntos += 5
        except Exception as e:
            st.error(f"Error al generar ejercicio: {e}")

# --- Chat con feedback ---
st.header("💬 Practicá con el Chatbot")
contexto = st.selectbox("Contexto", ["pareja", "trabajo", "familia"])
mensaje = st.text_input("Tu mensaje para el chatbot:")

if st.button("Enviar al chatbot"):
    with st.spinner("Pensando respuesta..."):
        prompt = f"""
        Simulá una conversación en el contexto "{contexto}".
        Respondé al siguiente mensaje con una respuesta breve y devolveme un JSON:
        - respuesta (mensaje del bot)
        - feedback (evaluación del tono, claridad y sugerencias)
        Usuario dijo: "{mensaje}"
        Solo el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            resultado = eval(respuesta.text)

            st.markdown(f"**Respuesta del bot:** {resultado['respuesta']}")
            st.markdown(f"**Feedback:** {resultado['feedback']}")
            st.session_state.puntos += 5
        except Exception as e:
            st.error(f"Error: {e}")

# --- Puntos acumulados ---
st.sidebar.title("🎮 Gamificación")
st.sidebar.markdown(f"**Puntos acumulados:** {st.session_state.puntos}")
