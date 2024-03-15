import chromadb
from chromadb.utils import embedding_functions
import sqlite3

chroma_client = chromadb.PersistentClient(path="chroma_db/conversations")

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

collection = chroma_client.get_or_create_collection(name='conversations', embedding_function=embedding_function)

# Connect to the database
conn = sqlite3.connect('/Users/sarveshdakhore/Desktop/new/techBarista/backend/chroma.db')

# Create a table if it doesn't exist
conn.execute('''
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        response TEXT,
        search_results TEXT
    )
''')

# Insert the conversation into the table
# conn.execute('''
#     INSERT INTO conversation_history (question, response, search_results)
#     VALUES (?, ?, ?)
# ''', (question, response, searchresults))

# Commit the changes and close the connection
conn.commit()
conn.close()





def get_relevant_convo(question:str, context:str, chathistory:str, searchresults:str):
    rel_convo = []
    results = collection.query(
        query_texts=[question],
        n_results=6
    )

    for i in range(len(results['documents'][0])):
        if results['distances'][0][i] < 1.25:
            rel_convo.append(results['documents'][0][i])

    if len(rel_convo)==0 :
        rel_convo.append("No relevant Conversations. Use recent conversation history and context as a guide.")
    return rel_convo
