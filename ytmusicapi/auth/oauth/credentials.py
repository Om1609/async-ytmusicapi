from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Mapping, Optional

from aiohttp import ClientSession

from ytmusicapi.constants import (
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_CODE_URL,
    OAUTH_SCOPE,
    OAUTH_TOKEN_URL,
    OAUTH_USER_AGENT,
)

from .exceptions import BadOAuthClient, UnauthorizedOAuthClient
from .models import AuthCodeDict, BaseTokenDict, RefreshableTokenDict


@dataclass
class Credentials(ABC):
    """Base class representation of YouTubeMusicAPI OAuth Credentials"""

    client_id: str
    client_secret: str

    @abstractmethod
    def get_code(self) -> Mapping:
        """Method for obtaining a new user auth code. First step of token creation."""

    @abstractmethod
    def token_from_code(self, device_code: str) -> RefreshableTokenDict:
        """Method for verifying user auth code and conversion into a FullTokenDict."""

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        """Method for requesting a new access token for a given refresh_token.
        Token must have been created by the same OAuth client."""


class OAuthCredentials(Credentials):
    """
    Class for handling OAuth credential retrieval and refreshing.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        session: Optional[ClientSession] = None,
        proxies: Optional[Dict] = None,
    ):
        """
        :param client_id: Optional. Set the GoogleAPI client_id used for auth flows.
            Requires client_secret also be provided if set.
        :param client_secret: Optional. Corresponding secret for provided client_id.
        :param session: Optional. Connection pooling with an active session.
        :param proxies: Optional. Modify the session with proxy parameters.
        """
        # id, secret should be None, None or str, str
        if not isinstance(client_id, type(client_secret)):
            raise KeyError(
                "OAuthCredential init failure. Provide both client_id and client_secret or neither."
            )

        # bind instance to OAuth client for auth flows
        self.client_id = client_id if client_id else OAUTH_CLIENT_ID
        self.client_secret = client_secret if client_secret else OAUTH_CLIENT_SECRET

        self._session = session if session else ClientSession()  # for auth requests
        if proxies:
            self._session.proxies.update(proxies)

    async def get_code(self) -> AuthCodeDict:
        """Method for obtaining a new user auth code. First step of token creation."""
        code_response = await self._send_request(OAUTH_CODE_URL, data={"scope": OAUTH_SCOPE})
        return await code_response.json()

    async def _send_request(self, url, data):
        """Method for sending post requests with required client_id and User-Agent modifications"""

        data.update({"client_id": self.client_id})
        response = await self._session.post(url, data=data, headers={"User-Agent": OAUTH_USER_AGENT})
        if response.status == 401:
            data = await response.json()
            issue = data.get("error")
            if issue == "unauthorized_client":
                raise UnauthorizedOAuthClient("Token refresh error. Most likely client/token mismatch.")

            elif issue == "invalid_client":
                raise BadOAuthClient(
                    "OAuth client failure. Most likely client_id and client_secret mismatch or "
                    "YouTubeData API is not enabled."
                )
            else:
                raise Exception(
                    f"OAuth request error. status_code: {response.status}, url: {url}, content: {data}"
                )
        return response

    async def token_from_code(self, device_code: str) -> RefreshableTokenDict:
        """Method for verifying user auth code and conversion into a FullTokenDict."""
        response = await self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "http://oauth.net/grant_type/device/1.0",
                "code": device_code,
            },
        )
        return await response.json()

    async def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        """
        Method for requesting a new access token for a given refresh_token.
        Token must have been created by the same OAuth client.

        :param refresh_token: Corresponding refresh_token for a matching access_token.
            Obtained via
        """
        response = await self._send_request(
            OAUTH_TOKEN_URL,
            data={
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        return await response.json()
