import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union

# --- Configuração ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("A variável de ambiente 'TELEGRAM_BOT_TOKEN' não está configurada.")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# URL da API de Chat do serviço backend (usando o nome do serviço 'backend' e a barra final corrigida)
BACKEND_CHAT_API_URL = "http://backend:8000/api/v1/agent/chat/" 

# --- ID Fixo para Contornar Bug do Backend ---
# Este ID é fixo porque o backend só aceita alguns valores inteiros grandes (como 12347),
# em vez de aceitar um ID de conversa único para cada usuário.
ID_FIXO_CONVERSA = 12347 

app = FastAPI()

# --- Modelos Pydantic para a Mensagem Recebida (Telegram) ---

class Chat(BaseModel):
    id: int
    type: str

class Message(BaseModel):
    message_id: int
    chat: Chat
    text: str | None = None

class Update(BaseModel):
    update_id: int
    message: Message | None = None

# --- Função de Envio de Mensagem (Telegram) ---

async def send_telegram_message(chat_id: int, text: str):
    """Envia uma mensagem de volta para o Telegram."""
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Erro ao enviar mensagem: {e.response.text}")
            # Em vez de levantar HTTPException, apenas registra o erro e prossegue
            print("AVISO: Falha ao enviar resposta ao Telegram.")

# --- Endpoint Principal: Webhook ---

@app.post("/webhook")
async def telegram_webhook(update: Update):
    """Endpoint que recebe as atualizações (mensagens) do Telegram e as envia para a IA."""
    
    if not update.message or not update.message.text:
        return {"message": "Update recebido, ignorado."}
    
    # IDs no Telegram são inteiros.
    chat_id = update.message.chat.id
    user_id_int = chat_id 
    mensagem_recebida = update.message.text

    print(f"Mensagem recebida de chat ID {chat_id}: '{mensagem_recebida}'")

    # 1. MONTAR O PAYLOAD PARA O BACKEND (Com a solução de ID fixo)
    
    payload = {
        "chat": {
            "agent_id": 1,
            # ID: Usa o valor fixo que o backend aceita para o ID da conversa.
            "id": ID_FIXO_CONVERSA,        
            "platform_id": 1,
            # user_id: Usa o ID real do Telegram, que é único para o usuário (conforme seu teste).
            "user_id": user_id_int 
        },
        "message": {
            "client_name": f"User_{user_id_int}", 
            "text": mensagem_recebida
        }
    } 

    ia_resposta = "Não foi possível obter uma resposta da IA."

    # 2. CHAMAR A API DO BACKEND
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Enviando o payload em JSON
            response = await client.post(BACKEND_CHAT_API_URL, json=payload)
            response.raise_for_status() # Levanta exceção para status 4xx/5xx
            
            ia_response_data = response.json()
            # Assumindo que a resposta da IA está no campo 'response'
            ia_resposta = ia_response_data.get("response", "A IA não respondeu claramente, mas o status foi 200 OK.")
            
        except httpx.HTTPStatusError as e:
            # Captura o erro 400, 500, etc.
            print(f"ERRO API BACKEND {e.response.status_code}: {e.response.text}")
            ia_resposta = f"Erro no serviço de IA: Status {e.response.status_code}. Mensagem do Backend: {e.response.text[:50]}..."
        except httpx.RequestError as e:
            # Erro de conexão/DNS/Timeout
            print(f"ERRO CONEXÃO BACKEND: {e}")
            ia_resposta = "Erro de conexão com o serviço de IA. O backend está ativo e na porta 8000?"
        
    # 3. RESPONDER AO TELEGRAM com a resposta da IA
    await send_telegram_message(
        chat_id=chat_id, 
        text=ia_resposta
    )
    
    return {"status": "success", "response_sent": ia_resposta}

@app.get("/")
def read_root():
    return {"service": "Telegram Chat Bot", "status": "running", "backend_api": BACKEND_CHAT_API_URL}
