import asyncio
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import AsyncDDGS

class Searcher:
    async def aget_results(self, word):
        results = await AsyncDDGS(proxies=None).text(word, max_results=2)
        links = [result['href'] for result in results]
        return links

    def get_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the response contains an HTTP error status code
        except requests.exceptions.RequestException as e:
            # print(f"Error getting content from {url}: {e}")
            return ""

        return response.text

    def parse_html(self, content) -> str:
        # soup = BeautifulSoup(content, 'html.parser')
        # text = soup.get_text()
        # text.replace("\n", " ")
        # return text
        soup = BeautifulSoup(content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(paragraph.get_text() for paragraph in paragraphs)
        words = text.split()
        truncated_text = ' '.join(words[:500])
        return truncated_text

    async def search_and_get_links(self, word):
        links = await self.aget_results(word)
        return links

    async def search_and_get_content(self, word):
        links = await self.aget_results(word)
        parsed_contents = []
        for link in links:
            content = self.get_content(link)
            parsed_content = self.parse_html(content)
            parsed_contents.append(parsed_content)
        return parsed_contents


# searcher = Searcher()
# async def main():
#     a1 = await searcher.search_and_get_links("how to create a class in python")
#     a2 =  await searcher.search_and_get_content("how to create a class in python")
#     return a1, a2
# searcher = Searcher()
# async def main():
#     a1 = await searcher.search_and_get_links("how to create a class in python")
#     a2 =  await searcher.search_and_get_content("how to create a class in python")
#     return a1, a2

# print(asyncio.run(main()))
# print(asyncio.run(main()))