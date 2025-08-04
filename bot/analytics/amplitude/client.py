from __future__ import annotations

import asyncio
import orjson
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from loguru import logger

from bot.analytics.types import AbstractAnalyticsLogger, BaseEvent

AMPLITUDE_ENDPOINT = "https://api2.amplitude.com/2/httpapi"


class AmplitudeTelegramLogger(AbstractAnalyticsLogger):
    def __init__(self, api_token: str, base_url: str = AMPLITUDE_ENDPOINT, max_concurrent: int = 100) -> None:
        self._api_token: str = api_token
        self._base_url: str = base_url
        self._headers = {"Content-Type": "application/json", "Accept": "*/*"}
        self._timeout = ClientTimeout(total=15)
        self.SUCCESS_STATUS_CODE = 200

        self._connector = TCPConnector(limit=max_concurrent, ttl_dns_cache=300)
        self._session = None
        self._tasks = set()
    
    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session with optimized settings."""
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector,
                timeout=self._timeout,
            )
        return self._session

    async def _send_request(
        self,
        event: BaseEvent,
    ) -> None:
        """Implementation of interaction with Amplitude API."""
        session = await self._get_session()
        data = {"api_key": self._api_token, "events": [event.to_dict()]}

        try:
            async with session.post(
                self._base_url,
                headers=self._headers,
                data=orjson.dumps(data),
            ) as response:
                json_response = await response.json(content_type="application/json")

            self._validate_response(json_response)
        except Exception as e:
            logger.error(f"Error sending event to Amplitude: {str(e)}")

    def _validate_response(self, response: dict[str, str | int]) -> None:
        """Validate response."""
        if response.get("code") != self.SUCCESS_STATUS_CODE:
            error = response.get("error")
            code = response.get("code")

            logger.error(f"get error from amplitude api | error: {error} | code: {code}")
            msg = f"Error in amplitude api call | error: {error} | code: {code}"
            raise ValueError(msg)

        logger.info(f"successfully send to Amplitude | server_upload_time: {response['server_upload_time']}")

    async def log_event(
        self,
        event: BaseEvent,
    ) -> None:
        """Use this method to sends event to Amplitude."""
        task = asyncio.create_task(self._send_request(event))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
    
    async def close(self) -> None:
        """Wait for all pending tasks and close the session."""
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
            
        if self._session and not self._session.closed:
            await self._session.close()