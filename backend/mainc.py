import json
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Searcher import Searcher
import requests
import base64
import asyncio

from chat_hist import chathistory

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ghtoken = "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"
def create_search_qns(question, context):

    SQprompt = PromptTemplate.from_template("""You are an expert question asker, Now your task is to ask questions which expand upon a question given using the context (which is most probably a code file) as reference and guide.
                                            These questions are used to guide the user to the answer they are looking for. Keep that in mind.
                                            NOTE:1) You are not allowed to ask questions that are already asked.
                                            2) your questions must be relevant to the given question and context.
                                            3) you are allowed to ask a maximum of 3 questions.
                                            4) you must ask a minimum of 1 questions.
                                            5) your questions must delve deeper into the topic based on the given question and the depth asked.
                                            6) The output must be in a list format.
                                            7) The output must be such that, those questions are most probable to be asked by a human based on context and question.
                                            8) The output MUST be relevant to the CONTEXT.
                                            9) The questions must be specific to the given context.
                                            10) In the output, DON'T use vague words (like this, that, over there, this file, etc.). Be specific and direct.
                                            Ex:
                                            question: "What is the purpose of this code?"
                                            context: "Assume, This is a code file that contains a class that is used to create a new user.(In reality it will be code)"
                                            output: ["What is a class?", "how to create a new class?", "what is the purpose of a class?", "how to manage users?"] 
                                        
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
                                      search results: {searchresults}""")


def summarize_repo(api_response:str, token):
    api_response = eval(api_response)
    file_info = {}
    def process_items(items, file_info):
        for item in items:
            if item['type'] == 'file':
                file_info[item['url']] = item['path']
            elif item['type'] == 'dir':
                process_items(item['content'], file_info)  # Recursive call

    file_info = {}
    process_items(api_response['blob']['content'], file_info)

    
    summarize_file_prompt = PromptTemplate.from_template("""You are a chatbot that assists users in navigating through code files.
                                                  you will get one input, "context", which represents a file in a git repository.
                                                  Now, you are an expert summarizer and your summaries are one the best.
                                                  You should provide a brief summary of the code file, including its purpose, functionality, and any other relevant information.
                                                  NOTE: The output must be in a string format and point wise.
                                                  context: {context}""")
    sum_file_chain = summarize_file_prompt | llm | StrOutputParser()
    file_summaries = []
    for fileurl, filepath in file_info.items():
        file = get_github_file_content(fileurl, token)
        summary = sum_file_chain.invoke({"context": file})
        file_summaries.append((filepath, summary))

    summarizer_prompt = PromptTemplate.from_template("""You are a chatbot that assists users in navigating through code files.
                                                    You will take one input: it is, "abt_files", which represents the file structure of the entire git repository with summaries of what each of them does.
                                                    Using the file structure, you should summarize the code files and provide a brief overview of the files and explain their relationship with other files.
                                                    In this task, you should provide a brief summary of the code files, including their purpose, functionality, how it fits in and any other relevant information.
                                                    You should maintain a friendly and professional demeanor while providing factual assistance. You should refrain from inventing information and strictly adhere to the contents of the provided code file. Your goal is to be a helpful tool that aids users in understanding and utilizing the code effectively.
                                                    You are Designed to offer guidance, explanations, and assistance based solely on the information present in the provided code file. Ensure that it handles various types of questions related to code structure, syntax, functionality, and best practices.
                                                    Remember to prioritize clarity, accuracy, and user-friendly interactions to deliver a positive experience for users seeking assistance with code comprehension and navigation.
                                                    NOTE: The output must be in a string format.
                                                    NOTE: the given references must not be used directly in the output unless it is absolutely necessary.
                                                    NOTE: The input will be in the form of a list of tuples, where each tuple contains the file path and the summary of the file.
                                                    NOTE: You must keep in mind the relationship between the files and provide a summary that reflects the same.
                                                    NOTE: Make use of the file structure given to provide a summary that reflects the relationship between the files. (Ex: if the path is /src/app/index.js, the summary should reflect the relationship between the index.js file and the app folder and everything else.)
                                                    information of the github repository: {abt_files}""")
    repo_sum_chain = summarizer_prompt | llm | StrOutputParser()
    repo_sum = repo_sum_chain.invoke({"abt_files": file_summaries})

    return repo_sum



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


async def main(question:str, codeurl) -> str:
    if question == "exit":
        return "Goodbye"
        
    gitfile = get_github_file_content(codeurl, ghtoken)
    searchquestions = create_search_qns(question, gitfile)
    searchresults = {}
    for qn in searchquestions:
        searchresults[qn] = await searcher.search_and_get_content(qn)
    response = chain.invoke({"question": question, "context":gitfile, "chathistory": chathistory[:10], "searchresults": searchresults})
    chathistory.append((f"Human: {question}", f"AI: {response}", f"Search Results: {searchresults}"))
    return response


# print(asyncio.run(main("what is this about?", "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/.eslintrc.json")))

import requests

# The URL of the endpoint
url = "http://127.0.0.1:8000/get_structure_comb"

# The data to send in the body
data = {
  "key": "https://github.com/devHarshShah/techBarista"
}

# Send the POST request
response = requests.post(url, json=data)

# Get the response as a Python dictionary
data = response.json()

print(type(data))  # This should print <class 'dict'>

# Access the 'content' field in the 'blob' field
print(data["blob"]["content"])