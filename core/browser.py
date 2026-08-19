import asyncio
import nodriver as uc


async def start_browser(retries: int = 3, delay: float = 2.0, **kwargs):

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return await uc.start(**kwargs)
        except Exception as e:
            last_error = e
            print(f"Tarayıcı başlatılamadı (deneme {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    raise last_error
