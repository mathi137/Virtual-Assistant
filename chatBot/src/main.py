import httpx
from fastapi import FastAPI, HTTPException

from .schemas import Update, AgentWebhookPayload
from .config import BACKEND_CHAT_API_URL
from .utils import (
    agent_registry,
    get_agent,
    send_telegram_message,
    load_all_active_agents,
    handle_agent_created,
    handle_agent_deleted,
)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await load_all_active_agents()


@app.post("/webhook/{agent_id}")
async def telegram_webhook(agent_id: int, update: Update):
    """Endpoint que recebe as atualizações (mensagens) do Telegram e as envia para a IA."""
    
    agent_info = get_agent(agent_id)
    if not agent_info:
        print(f"Agent {agent_id} não encontrado no registro")
        return {"message": "Agent not found", "status": "error"}
    
    if agent_info.get("disabled", False):
        print(f"Agent {agent_id} está desabilitado")
        return {"message": "Agent is disabled", "status": "error"}
    
    if not update.message or not update.message.text:
        return {"message": "Update recebido, ignorado."}
    
    chat_id = update.message.chat.id
    user_id_int = update.message.from_user.get("id") if update.message.from_user else chat_id
    mensagem_recebida = update.message.text
    
    print(f"Mensagem recebida de chat ID {chat_id} para agent {agent_id}: '{mensagem_recebida}'")

    payload = {
        "chat": {
            "id": chat_id,
            "agent_id": agent_id,
            "platform_id": agent_info["platform_id"],
            "user_id": agent_info["user_id"]
        },
        "message": {
            "client_name": f"User_{user_id_int}",
            "text": mensagem_recebida
        }
    } 

    ia_resposta = "Não foi possível obter uma resposta da IA."

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(BACKEND_CHAT_API_URL, json=payload)
            response.raise_for_status()
            ia_response_data = response.json()
            ia_resposta = ia_response_data.get("response", "A IA não respondeu claramente, mas o status foi 200 OK.")
        except httpx.HTTPStatusError as e:
            print(f"ERRO API BACKEND {e.response.status_code}: {e.response.text}")
            ia_resposta = f"Erro no serviço de IA: Status {e.response.status_code}."
        except httpx.RequestError:
            print("ERRO CONEXÃO BACKEND")
            ia_resposta = "Erro de conexão com o serviço de IA."
        
    await send_telegram_message(agent_info["token"], chat_id, ia_resposta)
    return {"status": "success", "response_sent": ia_resposta}


@app.post("/agent/event")
async def agent_event_webhook(payload: AgentWebhookPayload):
    """Endpoint to receive agent creation/deletion events from the backend."""
    try:
        event_type = payload.event
        agent = payload.agent
        
        print(f"Agent event received: {event_type} - Agent ID: {agent.id}")
        
        if event_type == "created":
            agent_dict = {
                "id": agent.id,
                "user_id": agent.user_id,
                "disabled": agent.disabled,
                "tokens": [token.model_dump() if hasattr(token, 'model_dump') else token for token in agent.tokens] if agent.tokens else []
            }
            await handle_agent_created(agent_dict)
        elif event_type == "deleted":
            await handle_agent_deleted(agent.id)
        
        return {"status": "success", "event": event_type, "agent_id": agent.id}
    except Exception as e:
        print(f"Error processing agent event: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing agent event: {str(e)}")


@app.get("/agents")
async def list_agents():
    """Endpoint para listar todos os agents registrados (para debug)."""
    return {
        agent_id: {
            "platform_id": info["platform_id"],
            "user_id": info["user_id"],
            "disabled": info["disabled"],
            "token_prefix": info["token"][:10] + "..." if len(info["token"]) > 10 else info["token"]
        }
        for agent_id, info in agent_registry.items()
    }


@app.get("/")
def read_root():
    return {
        "service": "Telegram Chat Bot", 
        "status": "running", 
        "backend_api": BACKEND_CHAT_API_URL,
        "registered_agents": len(agent_registry)
    }
