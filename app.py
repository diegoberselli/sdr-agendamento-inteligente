import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agent.sdr_agent import SDRAgent

app = FastAPI(title="SDR Agent - Elite Dev IA")

try:
    sdr = SDRAgent()
except Exception as e:
    sdr = None


class ChatMessage(BaseModel):
    message: str
    history: list = []


@app.get("/", response_class=HTMLResponse)
async def get_chat():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 SDR Agent - Elite Dev IA</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .chat-container {
                height: 300px;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            .message {
                margin: 10px 0;
                padding: 12px 16px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;
            }
            .user {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            .assistant {
                background: white;
                border: 1px solid #e9ecef;
                margin-right: auto;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 15px;
            }
            #messageInput {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            #messageInput:focus { border-color: #667eea; }
            button {
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s;
            }
            button:hover { transform: translateY(-2px); }
            button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
            .typing {
                display: none;
                padding: 15px 20px;
                color: #666;
                font-style: italic;
            }
            .examples {
                padding: 20px;
                background: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
            .examples h3 { margin-bottom: 15px; color: #333; }
            .example-btn {
                display: inline-block;
                margin: 5px;
                padding: 8px 15px;
                background: white;
                border: 1px solid #667eea;
                color: #667eea;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .example-btn:hover {
                background: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 SDR Agent</h1>
                <p>Elite Dev IA - Assistente Virtual Inteligente</p>
            </div>

            <div id="chat" class="chat-container"></div>
            <div id="typing" class="typing">Digitando...</div>

            <div class="examples">
                <h3>💡 Exemplos de perguntas:</h3>
                <span class="example-btn" onclick="setMessage('Olá, gostaria de saber sobre soluções de IA')">Soluções de IA</span>
                <span class="example-btn" onclick="setMessage('Preciso automatizar processos na minha empresa')">Automação</span>
                <span class="example-btn" onclick="setMessage('Tenho interesse em chatbots para atendimento')">Chatbots</span>
                <span class="example-btn" onclick="setMessage('Quero agendar uma conversa')">Agendar reunião</span>
            </div>

            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Digite sua mensagem..." onkeypress="handleKeyPress(event)">
                <button id="sendBtn" onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <script>
            let history = [];

            function addMessage(content, isUser) {
                const chat = document.getElementById('chat');
                const message = document.createElement('div');
                message.className = 'message ' + (isUser ? 'user' : 'assistant');
                message.innerHTML = content.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                chat.appendChild(message);
                chat.scrollTop = chat.scrollHeight;
            }

            function setMessage(text) {
                document.getElementById('messageInput').value = text;
                document.getElementById('messageInput').focus();
            }

            function showTyping(show) {
                document.getElementById('typing').style.display = show ? 'block' : 'none';
                document.getElementById('sendBtn').disabled = show;
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, true);
                input.value = '';
                showTyping(true);

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message, history })
                    });

                    const data = await response.json();
                    showTyping(false);
                    addMessage(data.response, false);
                    history = data.history;
                } catch (error) {
                    showTyping(false);
                    addMessage('❌ Erro de conexão. Tente novamente.', false);
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            }

            // Mensagem inicial
            window.onload = function() {
                addMessage('Olá! 👋 Sou o assistente da Elite Dev IA. Como posso ajudá-lo hoje?', false);
            }
        </script>
    </body>
    </html>
    """


@app.post("/chat")
async def chat_endpoint(chat_data: ChatMessage):
    try:
        if sdr is None:
            return {"response": "❌ SDR Agent não inicializado. Verifique as configurações.", "history": chat_data.history}
        
        # Converter histórico do formato FastAPI para formato SDR Agent
        historico_convertido = []
        for i in range(0, len(chat_data.history), 2):
            if i + 1 < len(chat_data.history):
                user_msg = chat_data.history[i].get('content', '') if isinstance(chat_data.history[i], dict) else str(chat_data.history[i])
                assistant_msg = chat_data.history[i + 1].get('content', '') if isinstance(chat_data.history[i + 1], dict) else str(chat_data.history[i + 1])
                historico_convertido.append([user_msg, assistant_msg])
        
        response = sdr.processar_conversa(chat_data.message, historico_convertido)
        
        # Garantir que response é string
        if not isinstance(response, str):
            response = str(response) if response is not None else "Erro: resposta vazia"
        
        if not response.strip():
            response = "Desculpe, não consegui processar sua mensagem. Tente novamente."

        new_history = chat_data.history + [
            {"role": "user", "content": chat_data.message},
            {"role": "assistant", "content": response},
        ]

        return {"response": response, "history": new_history}
    except Exception as e:
        return {"response": f"❌ Erro interno: {str(e)}", "history": chat_data.history}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
