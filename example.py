import ytmusicapi
import asyncio

artists = ['coldplay', 'michael jackson', 'dr dre', 'imagine dragons', 'taylor swift', 'eminem', 'adele', 'ed sheeran']

async def main():
    ytm = ytmusicapi.YTMusic()
    async with ytm._session:
        results = await asyncio.gather(*[ytm.search(artist, filter="songs", limit=1) for artist in artists])
        print(*[f"{result[0]['artists'][0]['name']}: {result[0]['title']}" for result in results], sep="\n")

asyncio.run(main())