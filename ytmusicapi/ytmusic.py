import gettext
import os
import asyncio
import orjson
import aiohttp
from requests.structures import CaseInsensitiveDict
from functools import partial
from contextlib import suppress
from typing import Dict
from ytmusicapi.helpers import *
from ytmusicapi.parsers import browsing
from ytmusicapi.setup import setup
from ytmusicapi.mixins.browsing import BrowsingMixin
from ytmusicapi.mixins.search import SearchMixin
from ytmusicapi.mixins.watch import WatchMixin
from ytmusicapi.mixins.explore import ExploreMixin
from ytmusicapi.mixins.library import LibraryMixin
from ytmusicapi.mixins.playlists import PlaylistsMixin
from ytmusicapi.mixins.uploads import UploadsMixin


class YTMusic(
    BrowsingMixin,
    SearchMixin,
    WatchMixin,
    ExploreMixin,
    LibraryMixin,
    PlaylistsMixin,
    UploadsMixin,
):
    """
    Allows automated interactions with YouTube Music by emulating the YouTube web client's requests.
    Permits both authenticated and non-authenticated requests.
    Authentication header data must be provided on initialization.
    """

    def __init__(
        self,
        auth: str = None,
        user: str = None,
        client_session=None,
        proxies: dict = None,
        language: str = "en",
    ):
        """
        Create a new instance to interact with YouTube Music.

        :param auth: Optional. Provide a string or path to file.
          Authentication credentials are needed to manage your library.
          Should be an adjusted version of `headers_auth.json.example` in the project root.
          See :py:func:`setup` for how to fill in the correct credentials.
          Default: A default header is used without authentication.
        :param user: Optional. Specify a user ID string to use in requests.
          This is needed if you want to send requests on behalf of a brand account.
          Otherwise the default account is used. You can retrieve the user ID
          by going to https://myaccount.google.com/brandaccounts and selecting your brand account.
          The user ID will be in the URL: https://myaccount.google.com/b/user_id/
        :param requests_session: A Requests session object or a truthy value to create one.
          Default sessions have a request timeout of 30s, which produces a requests.exceptions.ReadTimeout.
          The timeout can be changed by passing your own Session object::

            s = requests.Session()
            s.request = functools.partial(s.request, timeout=3)
            ytm = YTMusic(session=s)

          A falsy value disables sessions.
          It is generally a good idea to keep sessions enabled for
          performance reasons (connection pooling).
        :param proxies: Optional. Proxy configuration in requests_ format_.

            .. _requests: https://requests.readthedocs.io/
            .. _format: https://requests.readthedocs.io/en/master/user/advanced/#proxies

        :param language: Optional. Can be used to change the language of returned data.
            English will be used by default. Available languages can be checked in
            the ytmusicapi/locales directory.
        """
        self.auth = auth

        if isinstance(client_session, aiohttp.ClientSession):
            self._session = client_session
        else:
            self._session = aiohttp.ClientSession(json_serialize=orjson.dumps)
            self._session.request = partial(self._session.request, timeout=30)

        self.proxies = proxies
        self.cookies = {"CONSENT": "YES+1"}

        # prepare headers
        if auth:
            try:
                if os.path.isfile(auth):
                    file = auth
                    with open(file) as json_file:
                        self.headers = CaseInsensitiveDict(orjson.load(json_file))
                else:
                    self.headers = CaseInsensitiveDict(orjson.loads(auth))

            except Exception as e:
                print(
                    "Failed loading provided credentials. Make sure to provide a string or a file path. "
                    "Reason: " + str(e)
                )

        else:  # no authentication
            self.headers = initialize_headers()

        if "x-goog-visitor-id" not in self.headers:
            self.headers.update(
                asyncio.gather([get_visitor_id(self._send_get_request)])[0]
            )

        # prepare context
        self.context = initialize_context()
        self.context["context"]["client"]["hl"] = language
        locale_dir = os.path.abspath(os.path.dirname(__file__)) + os.sep + "locales"
        supported_languages = [f for f in os.listdir(locale_dir)]
        if language not in supported_languages:
            raise Exception(
                "Language not supported. Supported languages are "
                ", ".join(supported_languages)
            )
        self.language = language
        try:
            locale.setlocale(locale.LC_ALL, self.language)
        except locale.Error:
            with suppress(locale.Error):
                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        self.lang = gettext.translation(
            "base", localedir=locale_dir, languages=[language]
        )
        self.parser = browsing.Parser(self.lang)

        if user:
            self.context["context"]["user"]["onBehalfOfUser"] = user

        # verify authentication credentials work
        if auth:
            try:
                cookie = self.headers.get("cookie")
                self.sapisid = sapisid_from_cookie(cookie)
            except KeyError:
                raise Exception(
                    "Your cookie is missing the required value __Secure-3PAPISID"
                )

    async def _send_request(
        self, endpoint: str, body: Dict, additionalParams: str = ""
    ) -> Dict:
        body.update(self.context)
        if self.auth:
            origin = self.headers.get("origin", self.headers.get("x-origin"))
            self.headers["Authorization"] = get_authorization(
                self.sapisid + " " + origin
            )
        async with self._session.post(
            YTM_BASE_API + endpoint + YTM_PARAMS + additionalParams,
            json=body,
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        ) as response:
            response_text = await response.json(loads=orjson.loads)
            if response.status >= 400:
                message = (
                    "Server returned HTTP "
                    + str(response.status_code)
                    + ": "
                    + response.reason
                    + ".\n"
                )
                error = response_text.get("error", {}).get("message")
                raise Exception(message + error)
            return response_text

    async def _send_get_request(self, url: str, params: Dict = None):
        async with self._session.get(
            url,
            params=params,
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        ) as response:

            return response.text

    def _check_auth(self):
        if not self.auth:
            raise Exception("Please provide authentication before using this function")

    @classmethod
    def setup(cls, filepath: str = None, headers_raw: str = None) -> Dict:
        """
        Requests browser headers from the user via command line
        and returns a string that can be passed to YTMusic()

        :param filepath: Optional filepath to store headers to.
        :param headers_raw: Optional request headers copied from browser.
            Otherwise requested from terminal
        :return: configuration headers string
        """
        return setup(filepath, headers_raw)

    def __enter__(self):
        return self

    def __exit__(self, execType=None, execValue=None, trackback=None):
        pass
