import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union

# --- 1. Configuração e Modelos do Telegram ---

# Lê o token de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    # Se o token não for encontrado, o container falhará ao iniciar
    raise ValueError("TELEGRAM_BOT_TOKEN não configurado no ambiente.")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Modelo para a estrutura da mensagem que o Telegram envia
class Chat(BaseModel):
    id: int # O ID do chat é essencial para a resposta
    type: str

class Message(BaseModel):
    message_id: int
    chat: Chat
    text: Union[str, None] = None # O texto pode ser None (ex: se for uma foto)

class Update(BaseModel):
    update_id: int
    message: Union[Message, None] = None

app = FastAPI()

# --- 2. Lógica para Responder ao Telegram ---

async def send_telegram_message(chat_id: int, text: str):
    """Função que envia a mensagem de volta para o chat."""
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    
    # Faz uma requisição assíncrona para a API do Telegram
    async with httpx.AsyncClient() as client:
        # Tenta enviar a mensagem via método sendMessage
        response = await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
        if response.status_code != 200:
            print(f"ERRO DE ENVIO: {response.text}")
            # Não é estritamente necessário, mas bom para debug/log
            raise HTTPException(status_code=500, detail="Falha ao enviar resposta para o Telegram.")
        
        return response.json()


# --- 3. Endpoint do Webhook (Onde o Telegram "liga") ---

# O Telegram enviará um POST para este endpoint
@app.post("/webhook")
async def telegram_webhook(update: Update):
    """Recebe e processa as mensagens do Telegram."""
    
    # Verifica se o update é uma mensagem de texto válida
    if update.message and update.message.text:
        chat_id = update.message.chat.id
        
        # 4. Ação Principal: Responder "Olá"
        await send_telegram_message(
            chat_id=chat_id, 
            text="Olá! Recebi sua mensagem."
        )
        
    # O Telegram exige um retorno rápido (Status 200) para saber que a mensagem foi recebida.
    return {"status": "ok", "message": "Update processado."}


# --- 4. Endpoint de Teste (Health Check) ---

@app.get("/")
async def read_root():
    """Endpoint simples para verificar se o serviço está rodando."""
    return {"service": "Telegram Bot", "status": "running"}