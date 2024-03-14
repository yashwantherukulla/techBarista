from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun
from Searcher import Searcher

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def create_search_qns(question, context):

    SQprompt = PromptTemplate.from_template("""You are an expert question asker, Now your task is to ask questions which expand upon a question given using the context (which is most probably a code file) as reference and guide.
                                            These questions are used to guide the user to the answer they are looking for. Keep that in mind.
                                            NOTE:1) You are not allowed to ask questions that are already asked.
                                            2) your questions must be relevant to the given question.
                                            3) you are allowed to ask a maximum of 15 questions.
                                            4) you must ask a minimum of 3 questions.
                                            5) your questions must delve deeper into the topic based on the given question and the depth asked.
                                            6) The output must be in a list format.
                                        
                                            Ex: 
                                            question: what is the truth of life?
                                            output: ["what is love?", "what is life?", "what is the meaning of hate?", "what is life?", "what does it mean to die?"] 
                                            
                                            Now, the given question is, {question} and the given context is, {context}.""")

    chain = SQprompt | llm | StrOutputParser()
    search_qns = chain.invoke({"question": question, "context": context})
    return search_qns


prompt = PromptTemplate.from_template("""You are a chatbot that assists users in navigating through code files. You will take four inputs: "context", which represents a code file, and "question", which represents a question asked by the user regarding the code, "conversation history", which represents the conversation history till now, and "search results", which represents the search results when the "question" is searched in the web. 
                                      You should maintain a friendly and professional demeanor while providing factual assistance. You should refrain from inventing information and strictly adhere to the contents of the provided code file. Your goal is to be a helpful tool that aids users in understanding and utilizing the code effectively.
                                      You should maintain a friendly and professional demeanor while providing factual assistance. You should refrain from inventing information and strictly adhere to the contents of the provided code file. Your goal is to be a helpful tool that aids users in understanding and utilizing the code effectively.
                                      You are Designed to offer guidance, explanations, and assistance based solely on the information present in the provided code file. Ensure that it handles various types of questions related to code structure, syntax, functionality, and best practices.
                                      Remember to prioritize clarity, accuracy, and user-friendly interactions to deliver a positive experience for users seeking assistance with code comprehension and navigation.
                                      NOTE: The output must be in a string format.
                                      NOTE: the given references must not be used directly in the output unless it is absolutely necessary.
                                      question: {question}\n
                                      context: {context}\n
                                      conversation history: {chathistory}\n
                                      search results: {searchresults}""")

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
chain = prompt | llm | StrOutputParser()

searcher = Searcher()


gitfile="""import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchResults

import requests
from bs4 import BeautifulSoup


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


ddg_search = DuckDuckGoSearchResults()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def parse_html(content) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()

def fetch_web_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS)
    return parse_html(response.content)

web_fetcher_tool = Tool.from_function(func=fetch_web_page, 
                                      name="web_fetcher", 
                                      description="Fetches the content of a web page and returns it as a string.")




llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)


prompt = PromptTemplate.from_template("Summarize the following content: {content}")

chain = prompt | llm | StrOutputParser()

summarizer_tool = Tool.from_function(func=chain.invoke,
                                     name="summarizer", 
                                     description="Summarizes the content of a web page and returns it as a string.")

tools = [ddg_search, web_fetcher_tool, summarizer_tool]

agent = initialize_agent(
    tools = tools,
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    llm = llm,
    verbose = True
)

if __name__ == "__main__":
    # content = "Research how to use the requests library in Python. Use your tools to search and summarize content into a guide on how to use the requests library."
    # print(agent.invoke({"input": content}))
    """
chathistory = []
while True:
    question = input("Human: ")
    if (question=="exit"):
        break
    searchquestions = create_search_qns(question, gitfile)
    searchresults = searcher.search_and_get_content(searchquestions)
    response = chain.invoke({"question": question, "context":gitfile, "chathistory": chathistory, "searchresults": searchresults})
    chathistory.append((f"Human: {question}", f"AI: {response}", f"Search Results: {searchresults}"))
    print("------------------------------------------------------")
    print(response)
    print("------------------------------------------------------")
