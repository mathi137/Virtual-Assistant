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
        agent_data: Dictionary containing agent information
    
    Returns:
        bool: True if webhook was successfully triggered, False otherwise
    """
    try:
        payload = {
            "event": event_type,
            "agent": agent_data
        }
        
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
                
                logger.info(f"Successfully triggered webhook for agent {event_type}: agent_id={agent_data.get('id')}")
                return True
    except aiohttp.ClientError as e:
        logger.error(f"Webhook request error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error triggering webhook: {e}")
        return False

