from train import process_greeting, evaluar_codigo  

from flask import Flask, request, jsonify, Response
from flask_cors import CORS  # Importar CORS
import os
from huggingface_hub import InferenceClient
import time
import re

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración del cliente de HuggingFace
os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "D:/huggingface_cache"
client = InferenceClient(api_key="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")

# Prompt base para evaluación de código
PROMPT_BASE = """
Evalúa el siguiente código según los criterios de la rúbrica:
1. **Funcionalidad**: Evalúa si el código cumple con los requisitos y funciona correctamente.
2. **Eficiencia**: Analiza el rendimiento y uso de recursos, incluyendo tiempo de ejecución.
3. **Legibilidad**: Evalúa claridad, organización, comentarios y nombres descriptivos.
4. **Cumplimiento de estándares**: Verifica si sigue las mejores prácticas y estándares de codificación.
5. **Pruebas**: Analiza si se incluyen pruebas y cuán exhaustivas son.

Por cada criterio, asigna una puntuación del 1 al 4, donde 1 es deficiente y 4 es excelente. 
Devuelve también la nota total que es la suma de los puntajes de estos criterios (0 >= 20).
Proporciona una retroalimentación detallada.
"""
def convert_links_to_html(text):
    # Expresión regular para encontrar URLs
    url_pattern = re.compile(r'(https?://[^\s\)\*]+)') 
    # Reemplazar las URLs por un enlace HTML
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)


def stream_response(message):
    try:
        response = client.chat.completions.create(
            model="microsoft/Phi-3.5-mini-instruct",
            messages=[{"role": "user", "content": message}],
            max_tokens=1000
        )
        bot_response = response['choices'][0]['message']['content']
        # Convertir las URLs a enlaces HTML
        bot_response = convert_links_to_html(bot_response)
        # Dividir respuesta en fragmentos para simular streaming
        fragment_size = 50  # Tamaño de cada fragmento
        for i in range(0, len(bot_response), fragment_size):
            yield bot_response[i:i+fragment_size]
            time.sleep(0.1)  # Espera para simular retraso
    except Exception as e:
        yield f"Error: {str(e)}"

def evaluar_codigo_archivo(archivo): 
    try:
        # Leer el contenido del archivo
        with open(archivo, 'r') as f:
            codigo = f.read()

        # Construir el prompt completo
        prompt_completo = PROMPT_BASE + "\n```python\n" + codigo + "\n```"

        # Enviar el prompt al modelo
        response = client.chat.completions.create(
            model="microsoft/Phi-3.5-mini-instruct",
            messages=[
                {"role": "system", "content": "Eres un experto evaluador de código."},
                {"role": "user", "content": prompt_completo}
            ],
            max_tokens=1000
        )

        # Obtener la respuesta
        bot_response = response["choices"][0]["message"]["content"]

        # Formatear la salida
        salida_formateada = f"""
        Evaluación del Código: {archivo}

        {bot_response}
        """

        # Retornar el texto formateado
        return salida_formateada
    except Exception as e:
        return f"Error al evaluar el archivo: {str(e)}"
    

@app.route("/ask", methods=["POST"])
def ask():
    message = request.json.get("message")
    print(f"Mensaje recibido: {message}")
    
    # Si se carga un archivo para evaluación
    if message.startswith("evaluar archivo:"):
        archivo = message.split("evaluar archivo:")[1].strip()
        if os.path.exists(archivo):
            resultado_archivo = evaluar_codigo_archivo(archivo)
            return Response(resultado_archivo, content_type='text/plain')
        else:
            return jsonify({"error": "Archivo no encontrado"}), 404

    # Si el mensaje parece ser código, evaluarlo
    if "def " in message:  # Verifica si el mensaje parece ser código
        prompt_completo = PROMPT_BASE + "\n```python\n" + message + "\n```"
        response = client.chat.completions.create(
            model="microsoft/Phi-3.5-mini-instruct",
            messages=[
                {"role": "system", "content": "Eres un experto evaluador de código."},
                {"role": "user", "content": prompt_completo}
            ],
            max_tokens=1000
        )
        resultado_codigo = response["choices"][0]["message"]["content"]

        # Formatear respuesta
        salida_formateada = f"""
        Evaluación del Código:
        {resultado_codigo}
        """
        return Response(salida_formateada, content_type='text/plain')
        

    # Si no es código ni archivo, usar el modelo para otros mensajes
    return Response(stream_response(message), content_type='text/plain')
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

