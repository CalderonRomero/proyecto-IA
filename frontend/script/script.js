// Capturar elementos por ID
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatbox = document.getElementById('chatbox');
const fileInput = document.getElementById('fileInput');

let fileContent = ''; // Variable para almacenar el contenido del archivo

// Capturar el archivo cargado y leer su contenido
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    
    if (file) {
        const reader = new FileReader();
        
        // Leer el archivo como texto
        reader.onload = function(e) {
            fileContent = e.target.result; // Almacenar el contenido del archivo
            const userMessage = `Archivo cargado: ${file.name}`;
            addMessageToChat('user', userMessage); // Mostrar mensaje en el chat
        };
        
        // Leer el archivo
        reader.readAsText(file);
    }
});

// Manejar el evento keydown en el campo de entrada
messageInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        if (event.shiftKey) {
            // Insertar un salto de línea si se presiona Shift + Enter
            const cursorPos = messageInput.selectionStart;
            const textBeforeCursor = messageInput.value.substring(0, cursorPos);
            const textAfterCursor = messageInput.value.substring(cursorPos);

            // Agregar un salto de línea en la posición del cursor
            messageInput.value = textBeforeCursor + '\n' + textAfterCursor;

            // Ajustar la posición del cursor después del salto de línea
            messageInput.selectionStart = messageInput.selectionEnd = cursorPos + 1;

            event.preventDefault(); // Prevenir que Enter envíe el formulario
        } else {
            // Evitar el comportamiento por defecto y simular el envío del formulario
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit')); // Disparar el evento submit del formulario
        }
    }
});


// Manejar el envío del formulario
chatForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevenir el comportamiento por defecto (recarga de la página)

    // Obtener el mensaje escrito por el usuario
    const userMessage = messageInput.value.trim();
    if (userMessage || fileContent) {
        // Agregar el mensaje del usuario al chat
        addMessageToChat('user', userMessage);

        // Crear el mensaje combinado que se enviará al backend
        const combinedMessage = `${userMessage}\n\n${fileContent}`;
        getBotResponse(combinedMessage); // Obtener respuesta del bot

        messageInput.value = ''; // Limpiar campo
        fileInput.value = ''; // Limpiar el campo de archivo
        fileContent = ''; // Reiniciar el contenido del archivo
    }
});

// Agregar mensajes al chatbox con soporte para animación tipo "tipeando"
function addMessageToChat(sender, text) {
    const messageElement = document.createElement('div');

    if (text.startsWith("```") && text.endsWith("```")) {
        const codeBlock = document.createElement('pre');
        const codeContent = text.replace(/```/g, ""); // Eliminar delimitadores de código
        codeBlock.textContent = codeContent;
        codeBlock.classList.add('code-block');
        messageElement.appendChild(codeBlock);
    } else {
        // Expresión regular para identificar enlaces
        const linkPattern = /(https?:\/\/[^\s]+)/g;
        let htmlText = text.replace(linkPattern, (url) => {
            // Eliminar caracteres no deseados al final del enlace
            let cleanUrl = url.replace(/[)\*\s]+$/, ""); // Remover `)`, `*` o espacios al final
            return `<a href="${cleanUrl}" target="_blank" class="link" style="color: #007bff; text-decoration: underline;">${cleanUrl}</a>`;
        });

        // Reemplazar asteriscos para otros usos si es necesario
        htmlText = htmlText.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>"); // Negrita para texto entre `**`

        messageElement.innerHTML = htmlText; // Usar innerHTML para mostrar el texto formateado
    }

    messageElement.classList.add('message', sender);
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight; // Desplazar hacia abajo
}


// Obtener la respuesta del bot desde el backend Flask con animación tipo "tipeando"
async function getBotResponse(message) {
    const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let botMessage = '';
    const botMessageElement = document.createElement('div');
    botMessageElement.classList.add('message', 'bot');

    // Usar <pre> para conservar el formato de indentación y saltos de línea
    const preElement = document.createElement('pre');
    botMessageElement.appendChild(preElement);
    chatbox.appendChild(botMessageElement);

    // Leer en streaming y actualizar el contenido de <pre>
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        botMessage += decoder.decode(value, { stream: true });
        preElement.innerHTML = botMessage; // Actualizar <pre> con el texto recibido
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}