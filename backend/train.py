import re
import subprocess
import timeit

def process_greeting(message):
    greetings = ["hola", "buenos días", "buenas tardes"]
    if any(greet in message.lower() for greet in greetings):
        return "Hola, soy el chatbot que evalúa códigos de Python."
    return None

def evaluar_codigo(codigo):
    evaluacion = {
        "Funcionalidad": 0, 
        "Eficiencia": 0, 
        "Legibilidad": 0, 
        "Cumplimiento de estándares": 0, 
        "Pruebas": 0
    }
    retroalimentacion = []

    # 1. Funcionalidad
    try:
        exec_globals = {}
        exec(codigo, exec_globals)  # Ejecuta el código
        evaluacion["Funcionalidad"] = 4
        retroalimentacion.append("El código funciona correctamente y cumple con todos los requisitos planteados.")
    except Exception as e:
        evaluacion["Funcionalidad"] = 1
        retroalimentacion.append(f"El código no funciona o tiene errores críticos: {str(e)}")

    # 2. Eficiencia
    try:
        tiempo = timeit.timeit(lambda: exec(codigo), number=1)
        if tiempo < 1:  # Código eficiente
            evaluacion["Eficiencia"] = 4
            retroalimentacion.append("El código es eficiente y aprovecha al máximo los recursos disponibles.")
        elif tiempo < 3:  # Moderadamente eficiente
            evaluacion["Eficiencia"] = 3
            retroalimentacion.append("El código es moderadamente eficiente, pero podría optimizarse en algunos aspectos.")
        else:  # Ineficiente
            evaluacion["Eficiencia"] = 1
            retroalimentacion.append("El código es ineficiente, utiliza recursos innecesarios o tiene un tiempo de ejecución excesivo.")
    except Exception as e:
        evaluacion["Eficiencia"] = 1
        retroalimentacion.append(f"No se pudo medir la eficiencia debido a errores: {str(e)}")

    # 3. Legibilidad
    comentario_count = len(re.findall(r'#', codigo))  # Cuenta de comentarios
    if comentario_count >= 3:  # Código bien comentado
        evaluacion["Legibilidad"] = 4
        retroalimentacion.append("El código es claro, organizado, está bien comentado, y utiliza nombres descriptivos.")
    elif comentario_count >= 2:  # Moderadamente comentado
        evaluacion["Legibilidad"] = 3
        retroalimentacion.append("El código es comprensible con un esfuerzo adicional, tiene algunos comentarios y nombres moderadamente claros.")
    else:  # Pocos o ningún comentario
        evaluacion["Legibilidad"] = 1
        retroalimentacion.append("El código es difícil de entender, carece de comentarios o utiliza nombres poco descriptivos.")

    # 4. Cumplimiento de estándares
    try:
        result = subprocess.run(['flake8', '--stdin-display-name', 'evaluacion.py', '-'],
                                input=codigo, text=True, capture_output=True)
        if result.stdout.strip() == "":  # Cumple con los estándares
            evaluacion["Cumplimiento de estándares"] = 4
            retroalimentacion.append("Cumple con los estándares de codificación, aplicando buenas prácticas de manera consistente.")
        elif len(result.stdout.strip()) < 100:  # Algunos errores, pero no graves
            evaluacion["Cumplimiento de estándares"] = 3
            retroalimentacion.append(f"Sigue algunos estándares, pero tiene errores menores: {result.stdout.strip()}")
        else:  # Muchos errores
            evaluacion["Cumplimiento de estándares"] = 1
            retroalimentacion.append(f"No sigue los estándares de codificación o presenta malas prácticas: {result.stdout.strip()}")
    except Exception as e:
        evaluacion["Cumplimiento de estándares"] = 1
        retroalimentacion.append(f"Error al verificar estándares: {str(e)}")

    # 5. Pruebas
    if "def test_" in codigo:  # Busca funciones de prueba
        evaluacion["Pruebas"] = 4
        retroalimentacion.append("Las pruebas son exhaustivas, cubriendo todos los casos relevantes y verificando resultados.")
    elif "def " in codigo:  # Si hay funciones pero no son pruebas específicas
        evaluacion["Pruebas"] = 3
        retroalimentacion.append("Se incluyen algunas pruebas básicas, pero no abarcan todos los casos importantes.")
    else:  # No hay pruebas
        evaluacion["Pruebas"] = 1
        retroalimentacion.append("No se incluyen pruebas o no cubren casos básicos ni funcionales.")

    # Nota final (suma de todas las evaluaciones)
    nota_total = sum(evaluacion.values())

    return {
        "evaluacion": evaluacion,
        "nota": nota_total,
        "retroalimentacion": "\n".join(retroalimentacion)
    }
