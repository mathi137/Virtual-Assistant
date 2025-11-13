import aiohttp
from typing import Optional
from src.config import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


async def trigger_agent_webhook(event_type: str, agent_data: dict) -> bool:
    """
    Trigger webhook to chatbot service when agent is created or deleted.
    
    Args:
        event_type: 'created' or 'deleted'
        agent_data: Dictionary containing agent information (from AgentRead.model_dump())
    
    Returns:
        bool: True if webhook was successfully triggered, False otherwise
    """
    try:
        # Format agent data to match AgentEvent schema expected by chatBot
        # AgentEvent expects: id, user_id, system_prompt, disabled, tokens, created_at
        agent_payload = {
            "id": agent_data.get("id"),
            "user_id": agent_data.get("user_id"),
            "system_prompt": agent_data.get("system_prompt", ""),
            "disabled": agent_data.get("disabled", False),
            "tokens": agent_data.get("tokens", []),
            "created_at": agent_data.get("created_at")
        }
        
        # Ensure tokens are in the correct format (list of dicts)
        if agent_payload["tokens"]:
            formatted_tokens = []
            for token in agent_payload["tokens"]:
                if isinstance(token, dict):
                    formatted_tokens.append({
                        "platform_id": token.get("platform_id"),
                        "platform_name": token.get("platform_name", "").lower(),
                        "token": token.get("token")
                    })
                else:
                    # If token is already a Token object, convert it
                    formatted_tokens.append({
                        "platform_id": getattr(token, "platform_id", None),
                        "platform_name": getattr(token, "platform_name", "").lower() if hasattr(token, "platform_name") else "",
                        "token": getattr(token, "token", None)
                    })
            agent_payload["tokens"] = formatted_tokens
        
        payload = {
            "event": event_type,
            "agent": agent_payload
        }
        
        logger.info(f"Sending webhook for agent {event_type}: agent_id={agent_payload.get('id')}, payload={payload}")
        
        timeout = aiohttp.ClientTimeout(total=10.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                settings.CHATBOT_WEBHOOK_URL,
                json=payload
            ) as response:
                if response.status >= 400:
                    text = await response.text()
                    logger.error(f"Webhook failed with status {response.status}: {text}")
                    return False
                
                response_data = await response.json()
                logger.info(f"Successfully triggered webhook for agent {event_type}: agent_id={agent_payload.get('id')}, response={response_data}")
                return True
    except aiohttp.ClientError as e:
        logger.error(f"Webhook request error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error triggering webhook: {e}", exc_info=True)
        return False

