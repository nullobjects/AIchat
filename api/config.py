import os
from datetime import timedelta
from langchain_openai import OpenAIEmbeddings

# True: Uses Langchain for everything
# False: Uses HuggingFace for everything
USE_LANGCHAIN = True

MODEL_PROMPT = """
                   You are a helpful assitant called AIChat,
                   your job is to answer questions based off of this context: {context}.
                   
                   Question:
                   {question}
                   
                   If the user asks anything that is not related to this context reply with the following message:
                   \"I'm sorry but i can't answer questions that are not related to the document.\".
               """

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "uploads")

JWT_SECRET_KEY = "NullObjects_Secret_Key_Demek"
JWT_EXPIRATION_DELTA = timedelta(minutes=180)

ALLOWED_EXTENSIONS = (".txt", ".docx", ".pdf")

PERSISTENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PERSISTENT_DIRECTORY = os.path.join(PERSISTENT_DIRECTORY, "uploads", "faiss")

OPENAI_MODEL = "gpt-4o-mini"

EMBEDDING_FUNCTION = OpenAIEmbeddings(
    model="text-embedding-3-small"
)