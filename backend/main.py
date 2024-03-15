from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Searcher import Searcher
import requests
import base64
import asyncio

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ghtoken = ""
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
                                      search results: {searchresults}""")


def summarize_repo(api_response, token):
    # parsed_response = api_response.json()
    file_info = {}
    for item in api_response['blob']['content']:
        if item['type'] == 'file':
            file_info[item['url']] = item['path']

    
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



chathistory=[]
async def main(question:str, codeurl) -> str:
    if (question=="exit"):
        return "Goodbye"
    gitfile = get_github_file_content(codeurl, ghtoken)
    searchquestions = create_search_qns(question, gitfile)
    # print("------------------------------------------------------")
    # print(searchquestions)
    # print("------------------------------------------------------")
    searchresults = {}
    for qn in searchquestions:
        searchresults[qn] = await searcher.search_and_get_content(qn)
        # print(f"{await searcher.search_and_get_content(qn)}\n\n\n\n\n")
    # print("------------------------------------------------------")
    # print(searchresults)
    # print("------------------------------------------------------")
    
    # response = summarize_chain.invoke({"question": question, "context":gitfile, "chathistory": chathistory[:10], "searchresults": searchresults})

    response = chain.invoke({"question": question, "context":gitfile, "chathistory": chathistory[:10], "searchresults": searchresults})
    chathistory.append((f"Human: {question}", f"AI: {response}", f"Search Results: {searchresults}"))
    return response


# print(asyncio.run(main("what is this about?", "https://api.github.com/repos/yashwantherukulla/SpeakBot/contents/va_bing.py")))


api_response = {
  "blob": {
    "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
    "content": [
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": ".eslintrc.json",
        "path": ".eslintrc.json",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/.eslintrc.json"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": ".gitignore",
        "path": ".gitignore",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/.gitignore"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "README copy.md",
        "path": "README copy.md",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/README%20copy.md"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "README.md",
        "path": "README.md",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/README.md"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "next.config.js",
        "path": "next.config.js",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/next.config.js"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "package-lock.json",
        "path": "package-lock.json",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/package-lock.json"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "package.json",
        "path": "package.json",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/package.json"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages",
        "content": [
          {
            "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages/rd",
            "content": [
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages/rd",
                "content": None,
                "name": "[data].tsx",
                "path": "pages/rd/[data].tsx",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/pages/rd/[data].tsx"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages/rd",
                "content": None,
                "name": "redirect.module.css",
                "path": "pages/rd/redirect.module.css",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/pages/rd/redirect.module.css"
              }
            ],
            "name": "rd",
            "type": "dir",
            "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages/rd"
          }
        ],
        "name": "pages",
        "type": "dir",
        "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/pages"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "postcss.config.js",
        "path": "postcss.config.js",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/postcss.config.js"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public",
        "content": [
          {
            "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public/data",
            "content": [
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public/data/redirect",
                "content": [
                  {
                    "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public/data/redirect",
                    "content": None,
                    "name": "redirect.json",
                    "path": "public/data/redirect/redirect.json",
                    "type": "file",
                    "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/public/data/redirect/redirect.json"
                  }
                ],
                "name": "redirect",
                "type": "dir",
                "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public/data/redirect"
              }
            ],
            "name": "data",
            "type": "dir",
            "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public/data"
          },
          {
            "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public",
            "content": None,
            "name": "next.svg",
            "path": "public/next.svg",
            "type": "file",
            "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/public/next.svg"
          },
          {
            "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public",
            "content": None,
            "name": "vercel.svg",
            "path": "public/vercel.svg",
            "type": "file",
            "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/public/vercel.svg"
          }
        ],
        "name": "public",
        "type": "dir",
        "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/public"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src",
        "content": [
          {
            "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app",
            "content": [
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app",
                "content": None,
                "name": "favicon.ico",
                "path": "src/app/favicon.ico",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/favicon.ico"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app",
                "content": None,
                "name": "globals.css",
                "path": "src/app/globals.css",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/globals.css"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app",
                "content": None,
                "name": "layout.tsx",
                "path": "src/app/layout.tsx",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/layout.tsx"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app",
                "content": None,
                "name": "page.tsx",
                "path": "src/app/page.tsx",
                "type": "file",
                "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/page.tsx"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/projects",
                "content": [
                  {
                    "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/projects",
                    "content": None,
                    "name": "page.tsx",
                    "path": "src/app/projects/page.tsx",
                    "type": "file",
                    "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/projects/page.tsx"
                  }
                ],
                "name": "projects",
                "type": "dir",
                "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/projects"
              },
              {
                "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/rd",
                "content": [
                  {
                    "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/rd",
                    "content": None,
                    "name": "page.tsx",
                    "path": "src/app/rd/page.tsx",
                    "type": "file",
                    "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/src/app/rd/page.tsx"
                  }
                ],
                "name": "rd",
                "type": "dir",
                "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app/rd"
              }
            ],
            "name": "app",
            "type": "dir",
            "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src/app"
          }
        ],
        "name": "src",
        "type": "dir",
        "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/src"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "tailwind.config.js",
        "path": "tailwind.config.js",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/tailwind.config.js"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "tailwind.config.ts",
        "path": "tailwind.config.ts",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/tailwind.config.ts"
      },
      {
        "api_url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/",
        "content": None,
        "name": "tsconfig.json",
        "path": "tsconfig.json",
        "type": "file",
        "url": "https://github.com/sarveshdakhore/sarveshdakhore/blob/main/tsconfig.json"
      }
    ],
    "name": "sarveshdakhore",
    "type": "dir",
    "url": "https://api.github.com/repos/sarveshdakhore/sarveshdakhore/contents/"
  }
}

import requests
import json

# Your data to be sent as POST request's body

data = {
    "key": "https://github.com/devHarshShah/techBarista"
}

json_data = json.dumps(data)

try:
    response = requests.post('http://127.0.0.1:5000/get_structure_comb', data=json_data, headers={'Content-Type': 'application/json'})
    response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
    # Handle the error here or re-raise if you want to stop the program in case of error

else:
    print("POST request was successful.")
    print(response.json())

print(type(api_response))
print(summarize_repo(api_response, ghtoken))