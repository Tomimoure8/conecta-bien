import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

# Cargar clave de API desde .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Configuración general
st.set_page_config(page_title="Conecta Bien", page_icon="🧠")
st.title("🧠 Conecta Bien")
st.markdown("Mejorá tu comunicación con IA")
st.markdown("""
**👥 Creada con ❤️ por _Tomás Moure_ y _Matías Amen_.**
""")

# Explicación de cómo funciona la app
with st.expander("ℹ️ ¿Cómo funciona Conecta Bien?"):
    st.markdown("""
Conecta Bien te ayuda a mejorar tu comunicación con inteligencia artificial. La app está dividida en 3 secciones clave:

### 🔍 1. Analiza tu comunicación
Escribí un mensaje como lo harías en una conversación real. La IA te devuelve:
- El **tono emocional**
- El nivel de **claridad**
- Las **emociones detectadas**
- Consejos útiles para mejorar tu expresión

---

### 🎯 2. Generá un ejercicio personalizado
Después del análisis, podés generar un ejercicio práctico adaptado a tu mensaje. Puede ser sobre:
- Asertividad
- Escucha activa
- Empatía
- Resolución de conflictos

---

### 💬 3. Practicá con el Chatbot
Simulá una conversación real:
1. Enviás un mensaje al bot según el contexto.
2. El bot responde con empatía y hace una pregunta.
3. Le contestás.
4. Recibís un **feedback general sobre cómo te comunicaste**.

---

### 🎮 Puntos acumulados
Cada acción suma puntos que podés ver en la barra lateral:
- Análisis: +10
- Ejercicio: +5
- Conversación completada: +5
""")


# Inicializar puntos
if "puntos" not in st.session_state:
    st.session_state.puntos = 0

# --- Análisis de comunicación ---
st.header("🔍 Analiza tu comunicación")
texto = st.text_area("Escribí tu mensaje:")

if st.button("Analizar") and texto:
    with st.spinner("Analizando con Gemini..."):
        prompt = f"""
        Analiza este texto y devolveme un JSON con:
        - tono
        - claridad (de 0 a 1)
        - emociones
        - sugerencias
        Texto: "{texto}"
        Solo el JSON.
        """
        try:
            respuesta = model.generate_content(prompt)
            texto_respuesta = respuesta.text.strip()

            # Buscar JSON con regex
            json_match = re.search(r"\{.*\}", texto_respuesta, re.DOTALL)
            if not json_match:
                raise ValueError("Gemini no devolvió JSON válido. Revisá el prompt o el texto.")

            resultado = json.loads(json_match.group())

            st.success("Análisis completo")
            st.markdown(f"**Tono:** {resultado['tono']}")
            st.markdown(f"**Claridad:** {resultado['claridad']}")
            st.markdown(f"**Emociones:** {', '.join(resultado['emociones'])}")
            st.markdown("**Sugerencias:**")
            for sugerencia in resultado['sugerencias']:
                st.write(f"- {sugerencia}")
            st.session_state.puntos += 10

        except Exception as e:
            st.error(f"Error al analizar: {e}")

# --- Generar ejercicio personalizado ---
if texto and st.button("🎯 Generar ejercicio"):
    with st.spinner("Generando ejercicio..."):
        prompt = f"""
        Basado en este mensaje, generá un ejercicio de comunicación en JSON.
        Estructura esperada:
        {{
            "tipo": "asertividad | escucha activa | empatía | resolución de conflictos",
            "descripcion": "Instrucciones claras para practicar"
        }}
        Mensaje: "{texto}"
        Devolveme solo el JSON sin explicaciones.
        """
        try:
            respuesta = model.generate_content(prompt)
            texto_respuesta = respuesta.text.strip()

            # Limpiar formato si viene con markdown o \n
            if texto_respuesta.startswith("```json"):
                texto_respuesta = texto_respuesta.replace("```json", "").replace("```", "").strip()

            # Intentar parsear JSON
            ejercicio = json.loads(texto_respuesta)

            st.markdown(f"**🧠 Tipo de ejercicio:** {ejercicio['tipo'].capitalize()}")
            st.markdown("**📋 Instrucciones:**")
            st.markdown(ejercicio["descripcion"].replace("\\n", "\n"))  # Mostrar con saltos de línea
            st.session_state.puntos += 5

        except Exception as e:
            st.error("Gemini no devolvió JSON válido. Revisá el prompt o el texto.")
            st.exception(e)
            st.code(texto_respuesta, language="json")



# --- Chatbot con diálogo activo ---
import re

st.header("💬 Practicá con el Chatbot (modo conversación)")
contexto = st.selectbox("Contexto", ["pareja", "trabajo", "familia"], key="contexto_chat")

# Inicializar variables en session_state
if "paso_chat" not in st.session_state:
    st.session_state.paso_chat = 1
if "mensaje_1" not in st.session_state:
    st.session_state.mensaje_1 = ""
if "mensaje_2" not in st.session_state:
    st.session_state.mensaje_2 = ""
if "respuesta_bot_1" not in st.session_state:
    st.session_state.respuesta_bot_1 = ""

# Función para limpiar JSON
def limpiar_json(texto):
    return re.sub(r"```json|```", "", texto).strip()

# PASO 1 – Primer mensaje del usuario
if st.session_state.paso_chat == 1:
    st.subheader("Paso 1: Iniciá la conversación")
    st.session_state.mensaje_1 = st.text_input("¿Qué querés decirle al bot?")

    if st.button("Enviar primer mensaje"):
        prompt = f"""
Actuá como un chatbot que conversa en un contexto de "{st.session_state.contexto_chat}". 
Respondé de manera empática al mensaje del usuario con una pregunta abierta para continuar el diálogo.
Devolvé solo un JSON válido con esta estructura:

{{
    "respuesta": "respuesta del bot al mensaje del usuario"
}}

Mensaje del usuario: "{st.session_state.mensaje_1}"
"""
        try:
            respuesta = model.generate_content(prompt)
            json_text = limpiar_json(respuesta.parts[0].text)
            data = json.loads(json_text)
            st.session_state.respuesta_bot_1 = data["respuesta"]
            st.session_state.paso_chat = 2
            st.session_state.puntos += 5
        except Exception as e:
            st.error("❌ Error en la respuesta del bot.")
            print("Error:", e)

# PASO 2 – Respuesta del usuario al bot
if st.session_state.paso_chat == 2:
    st.subheader("Paso 2: Respondé al bot")
    st.markdown(f"**🤖 Bot:** {st.session_state.respuesta_bot_1}")
    st.session_state.mensaje_2 = st.text_input("Tu respuesta al bot:")

    if st.button("Finalizar conversación"):
        prompt = f"""
Actuá como un coach de comunicación. Analizá esta breve conversación en el contexto de "{st.session_state.contexto_chat}".
Dale al usuario un feedback constructivo sobre cómo se expresó (tono, empatía, claridad) y una sugerencia para mejorar.
Devolvé solo un JSON con esta estructura:

{{
    "feedback": "análisis de la conversación y sugerencia de mejora"
}}

Conversación:
Usuario: "{st.session_state.mensaje_1}"
Bot: "{st.session_state.respuesta_bot_1}"
Usuario: "{st.session_state.mensaje_2}"
"""
        try:
            respuesta = model.generate_content(prompt)
            json_text = limpiar_json(respuesta.parts[0].text)
            data = json.loads(json_text)

            st.markdown("✅ **Conversación completada.**")
            st.markdown(f"**🧠 Feedback:** {data['feedback']}")
            st.session_state.puntos += 5
            st.session_state.paso_chat = 1  # reiniciar para otra conversación
        except Exception as e:
            st.error("❌ Error al generar el feedback.")
            print("Error:", e)


# --- Puntos acumulados ---
st.sidebar.title("🎮 Gamificación")
st.sidebar.markdown(f"**Puntos acumulados:** {st.session_state.puntos}")
