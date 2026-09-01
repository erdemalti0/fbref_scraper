import asyncio
import nodriver as uc

from core.logger import get_logger

logger = get_logger(__name__)


async def start_browser(retries: int = 3, delay: float = 2.0, **kwargs):

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return await uc.start(**kwargs)
        except Exception as e:
            last_error = e
            logger.error(f"Browser failed to start (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    raise last_error
