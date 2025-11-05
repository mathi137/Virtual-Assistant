from typing import Dict, Union
import httpx
from .config import WEBHOOK_BASE_URL, BACKEND_AGENTS_API_URL


# Agent Registry: Store agent tokens and metadata
agent_registry: Dict[int, Dict[str, Union[str, int, bool]]] = {}


def get_agent(agent_id: int) -> Dict[str, Union[str, int, bool]] | None:
    """Get agent information from registry."""
    return agent_registry.get(agent_id)


async def send_telegram_message(token: str, chat_id: int, text: str):
    """Envia uma mensagem de volta para o Telegram usando o token específico do bot."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Erro ao enviar mensagem: {e.response.text}")
        except Exception:
            print("AVISO: Falha ao enviar resposta ao Telegram.")


async def register_telegram_webhook(token: str, agent_id: int):
    """Registra o webhook do Telegram para um bot específico."""
    webhook_url = f"{WEBHOOK_BASE_URL}/webhook/{agent_id}"
    
    if not webhook_url.startswith("https://"):
        print(f"AVISO: WEBHOOK_BASE_URL deve ser HTTPS. URL atual: {webhook_url}")
        print(f"Webhook NÃO foi registrado para agent {agent_id}. Configure WEBHOOK_BASE_URL com HTTPS.")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/setWebhook",
                json={"url": webhook_url}
            )
            result = response.json()
            if result.get("ok"):
                print(f"Webhook registrado para agent {agent_id}: {webhook_url}")
                return True
            else:
                print(f"Erro ao registrar webhook: {result.get('description')}")
                return False
        except Exception as e:
            print(f"Erro ao registrar webhook: {e}")
            return False


async def unregister_telegram_webhook(token: str):
    """Remove o webhook do Telegram para um bot específico."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/deleteWebhook",
                json={"drop_pending_updates": True}
            )
            result = response.json()
            if result.get("ok"):
                print(f"Webhook removido para token")
                return True
            return False
        except Exception as e:
            print(f"Erro ao remover webhook: {e}")
            return False


async def load_agent_from_backend(agent_data: dict):
    """Helper function to load an agent into the registry."""
    agent_id = agent_data.get("id")
    user_id = agent_data.get("user_id")
    disabled = agent_data.get("disabled", False)
    tokens = agent_data.get("tokens", [])
    
    for token_data in tokens:
        if isinstance(token_data, dict) and token_data.get("platform_name", "").lower() == "telegram":
            token = token_data.get("token")
            platform_id = token_data.get("platform_id")
            
            agent_registry[agent_id] = {
                "token": token,
                "user_id": user_id,
                "platform_id": platform_id,
                "disabled": disabled
            }
            print(f"Telegram token armazenado para agent {agent_id}, Platform ID: {platform_id}")
            await register_telegram_webhook(token, agent_id)


async def load_all_active_agents():
    """Load all active agents from the backend on startup."""
    print("Carregando agents ativos do backend...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(BACKEND_AGENTS_API_URL)
            response.raise_for_status()
            agents = response.json()
            print(f"Encontrados {len(agents)} agent(s) ativo(s)")
            
            for agent_data in agents:
                try:
                    await load_agent_from_backend(agent_data)
                except Exception as e:
                    print(f"Erro ao carregar agent {agent_data.get('id')}: {e}")
            
            print(f"Total de {len(agent_registry)} agent(s) registrado(s) no chatbot")
        except httpx.HTTPStatusError as e:
            print(f"ERRO ao carregar agents: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Erro ao carregar agents: {e}")


async def handle_agent_created(agent_data: dict):
    """Handle agent creation event."""
    agent_id = agent_data.get("id")
    print(f"Agent created: {agent_id}")
    await load_agent_from_backend(agent_data)


async def handle_agent_deleted(agent_id: int):
    """Handle agent deletion event."""
    print(f"Agent deleted: {agent_id}")
    
    agent_info = get_agent(agent_id)
    if agent_info:
        token = agent_info.get("token")
        if token:
            await unregister_telegram_webhook(token)
        del agent_registry[agent_id]
        print(f"Agent {agent_id} removido do registro")

