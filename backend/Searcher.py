import asyncio
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import AsyncDDGS

class Searcher:
    async def aget_results(self, word):
        results = await AsyncDDGS(proxies=None).text(word, max_results=5)
        links = [result['href'] for result in results]
        return links

    def get_content(self, url):
        response = requests.get(url)
        return response.text

    def parse_html(self, content) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        text.replace("\n\n", "\n")
        return text

    async def search_and_get_links(self, word):
        links = await self.aget_results(word)
        print(links)

    async def search_and_get_content(self, word):
        links = await self.aget_results(word)
        parsed_contents = []
        for link in links:
            content = self.get_content(link)
            parsed_content = self.parse_html(content)
            parsed_contents.append(parsed_content)
        return parsed_contents
