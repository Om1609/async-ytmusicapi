"""protocol that defines the functions available to mixins"""

from typing import Dict, Optional, Protocol

from aiohttp import ClientResponse

from ytmusicapi.auth.types import AuthType
from ytmusicapi.parsers.i18n import Parser


class MixinProtocol(Protocol):
    """protocol that defines the functions available to mixins"""

    auth_type: AuthType

    parser: Parser

    proxies: Optional[Dict[str, str]]

    def _check_auth(self) -> None:
        """checks if self has authentication"""

    async def _send_request(self, endpoint: str, body: Dict, additionalParams: str = "") -> Dict:
        """for sending post requests to YouTube Music"""

    async def _send_get_request(self, url: str, params: Optional[Dict] = None) -> ClientResponse:
        """for sending get requests to YouTube Music"""

    @property
    def headers(self) -> Dict[str, str]:
        """property for getting request headers"""
