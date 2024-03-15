from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Searcher import Searcher
import requests
import base64
import asyncio
from chroma import *

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ghtoken = "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"
def create_search_qns(question, context):

    SQprompt = PromptTemplate.from_template("""You are an expert question asker, Now your task is to ask questions which expand upon a question given using the context (which is most probably a code file) as reference and guide.
                                            These questions are used to guide the user to the answer they are looking for. Keep that in mind.
                                            NOTE:1) You are not allowed to ask questions that are already asked.
                                            2) your questions must be relevant to the given question.
                                            3) you are allowed to ask a maximum of 4 questions.
                                            4) you must ask a minimum of 2 questions.
                                            5) your questions must delve deeper into the topic based on the given question and the depth asked.
                                            6) The output must be in a list format.
                                        
                                            Ex: 
                                            question: what is the truth of life?
                                            output: ["what is love?", "what is life?", "what is the meaning of hate?", "what is life?", "what does it mean to die?"] 
                                            
                                            Now, the given question is, {question} and the given context is, {context}.""")

    chain = SQprompt | llm | StrOutputParser()
    search_qns = chain.invoke({"question": question, "context": context})
    search_qns = search_qns.split("\n")
    search_qns = [qn for qn in search_qns if qn]
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
                                      search results: {searchresults}
                                      relevent conversation: {rel_convo}""")

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
chain = prompt | llm | StrOutputParser()

searcher = Searcher()


def get_github_file_content(url:str, token:str):
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    response_json = response.json()

    if 'content' in response_json:
        content_base64 = response_json['content']
        content = base64.b64decode(content_base64).decode('utf-8')
        return content
    elif 'message' in response_json:
        return response_json['message']
    else:
        return "Error: Unexpected response"


chathistory=[]
async def main(question:str, codeurl) -> str:
    if question == "exit":
        collection.clear()
        return "Goodbye"
        
    gitfile = get_github_file_content(codeurl, ghtoken)
    searchquestions = create_search_qns(question, gitfile)
    # print("------------------------------------------------------")
    # print(searchquestions)
    # print("------------------------------------------------------")
    searchresults = {}
    for qn in searchquestions:
        result = await searcher.search_and_get_content(qn)
        searchresults[qn] = result
        # print(f"{result}\n\n\n\n\n")
    # print("------------------------------------------------------")
    # print(searchresults)
    # print("------------------------------------------------------")
    response = chain.invoke({"question": question, "context":gitfile, "chathistory": chathistory[:10], "searchresults": searchresults, "rel_convo": get_relevant_convo(question, gitfile, chathistory, searchresults)})
    chathistory.append((f"Human: {question}", f"AI: {response}", f"Search Results: {searchresults}"))
    # return ''
    return response

#print(asyncio.run(main("what is this about?", "https://api.github.com/repos/yashwantherukulla/SpeakBot/contents/va_bing.py")))