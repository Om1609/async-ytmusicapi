ytmusicapi: Unofficial API for YouTube Music
############################################

This is an async prototype of `ytmusicapi <https://github.com/sigma67/ytmusicapi>`_. Use with caution.

ytmusicapi is a Python 3 library to send requests to the YouTube Music API.
It emulates YouTube Music web client requests using the user's cookie data for authentication.

.. features

Features
--------

| **Browsing**:

* search (including all filters) and suggestions
* get artist information and releases (songs, videos, albums, singles, related artists)
* get user information (videos, playlists)
* get albums
* get song metadata
* get watch playlists (next songs when you press play/radio/shuffle in YouTube Music)
* get song lyrics

| **Exploring music**:

* get moods and genres playlists
* get latest charts (globally and per country)

| **Library management**:

* get library contents: playlists, songs, artists, albums and subscriptions, podcasts, channels
* add/remove library content: rate songs, albums and playlists, subscribe/unsubscribe artists
* get and modify play history

| **Playlists**:

* create and delete playlists
* modify playlists: edit metadata, add/move/remove tracks
* get playlist contents
* get playlist suggestions

| **Podcasts**:

* get podcasts
* get episodes
* get channels
* get episodes playlists

| **Uploads**:

* upload songs and remove them again
* list uploaded songs, artists and albums

| **Localization**:

* all regions are supported (see `locations FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html#which-values-can-i-use-for-locations>`__
* 16 languages are supported (see `languages FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html#which-values-can-i-use-for-languages>`__


If you find something missing or broken,
check the `FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html>`__ or
feel free to create an `issue <https://github.com/sigma67/ytmusicapi/issues/new/choose>`__.

Requirements
------------

- Python 3.8 or higher - https://www.python.org

Setup
-----

See the `Documentation <https://ytmusicapi.readthedocs.io/en/stable/usage.html>`_ for detailed instructions

Usage
------
.. code-block:: python

    import ytmusicapi
    import asyncio

    async def main():
        ytm = ytmusicapi.YTMusic()
        results = await ytm.search("coldpaly", filter="songs", limit=1)
        print(results)

    asyncio.run(main())

The `tests <https://github.com/sigma67/ytmusicapi/blob/master/tests/>`_ are also a great source of usage examples.

.. end-features

Contributing
------------

Pull requests are welcome. There are still some features that are not yet implemented.
Please, refer to `CONTRIBUTING.rst <https://github.com/sigma67/ytmusicapi/blob/master/CONTRIBUTING.rst>`_ for guidance.
