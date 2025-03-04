from transformers import AutoTokenizer, TFAutoModelForQuestionAnswering, AutoModelForSeq2SeqLM
import tensorflow as tf
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from typing import List
from config import *

def GetOrCreateVectorStore(persistent_directory, embedding_function):
    try:
        vector_store = FAISS(persist_directory=persistent_directory, embedding_function=embedding_function)
    except Exception as e:
        vector_store = FAISS.from_documents([], embedding_function=EMBEDDING_FUNCTION, persist_directory=PERSISTENT_DIRECTORY)
    
    return vector_store

class Chatbot:
    def __init__(self):
        if USE_LANGCHAIN:
            # Note: The Memory for the chatbot is stored per session
            # This way we don't create multiple instances of the model
            self.model = ChatOpenAI(model=OPENAI_MODEL)
            self.vector_store = GetOrCreateVectorStore(PERSISTENT_DIRECTORY, EMBEDDING_FUNCTION)
            self.conversation_chain = ConversationChain.
        else:
            model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
            self.AnswerModel = {
                "tokenizer": AutoTokenizer.from_pretrained(model_name),
                "model": TFAutoModelForQuestionAnswering.from_pretrained(model_name),
            }

            model_name = "google/flan-t5-large"
            self.QuestionsModel = {
                "tokenizer": AutoTokenizer.from_pretrained(model_name),
                "model": AutoModelForSeq2SeqLM.from_pretrained(model_name),
            }

    def ChunkContext(context: str) -> List[str]: 
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 200,
            chunk_overlap = 20
        )

        return text_splitter.create_documents([context])

    def GetContextChunks(session, context: str):
        if not session["context_chunks"]:
            session["context_chunks"] = ChunkContext(context)
        return session["context_chunks"]

    def GenerateAnswer(self, session, question, context):
        if USE_LANGCHAIN:
            memory = session["memory"]
            #prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

        else:
            tokenizer = self.AnswerModel["tokenizer"]
            model = self.AnswerModel["model"]

            inputs = tokenizer(question, context, return_tensors="tf", padding=True, truncation=True)
            
            outputs = model(**inputs)

            start_logits = outputs.start_logits
            end_logits = outputs.end_logits

            start_index = tf.argmax(start_logits, axis=-1).numpy()[0]
            end_index = tf.argmax(end_logits, axis=-1).numpy()[0]

            answer_tokens = inputs.input_ids[0][start_index:end_index + 1]
            
            answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)

            if answer in ["[CLS]", "[SEP]", ""]:
                return "Sorry, I couldn't find an answer to your question in the provided context."

            return answer
    
    def GenerateQuestions(self, session, context):
        if USE_LANGCHAIN:
            print("hello")
        else:
            tokenizer = self.QuestionsModel["tokenizer"]
            model = self.QuestionsModel["model"]

            inputs = tokenizer("Generate 3 questions based on the following context: " + context, return_tensors="pt", padding=True, truncation=True)

            outputs = model.generate(
                inputs['input_ids'],
                min_length=6,
                max_length=20,
                num_return_sequences=3,
                do_sample=True,
                temperature=1.2,
            )

            generated_questions = tokenizer.batch_decode(outputs, skip_special_tokens=True)

            return generated_questions