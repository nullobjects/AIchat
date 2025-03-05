from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langgraph.graph import START, END, StateGraph
from typing import List
from config import *
from langchain.chains import RetrievalQA

prompt_template = ChatPromptTemplate([
    ("system", MODEL_PROMPT),
    ("human", "{question}")
])

class State:
    session: dict
    context: str
    query: str
    context_chunks: List[str]
    vector_store: FAISS
    result: str

    def __init__(self, session, context: str, query: str, result: str = None, context_chunks: List[str] = None, vector_store=None):
        self.session = session
        self.context = context
        self.query = query
        self.result = result
        self.context_chunks = context_chunks
        self.vector_store = vector_store

    def to_dict(self):
        return self.__dict__.copy()

class WorkFlow:
    def __init__(self):
        # Note: The Memory for the chatbot is stored per session
        # This way we don't create multiple instances of the model
        self.model = ChatOpenAI(model=OPENAI_MODEL)

        self.graph = StateGraph(State)
        self.graph.add_node("split_context", self.CreateContextChunks)
        self.graph.add_node("create_vector_store", self.GetOrCreateVectorStore)
        self.graph.add_node("llm_result", self.CallModel)

        self.graph.add_edge(START, "split_context")
        self.graph.add_edge("split_context", "create_vector_store")
        self.graph.add_edge("create_vector_store", "llm_result")
        self.graph.add_edge("llm_result", END)

        self.compiled_graph = self.graph.compile()
    
    def Run(self, session, context: str, query: str):
        #state = State(session=session, context=context, query=query)
        response = self.compiled_graph.invoke({
            "session": session,
            "context": context,
            "query": query
        })

        return response["result"]

    def GetOrCreateVectorStore(self, state: State) -> State:
        name = "faiss_index_" + state.session["session_id"]
        try:
            vector_store = FAISS.load_local(folder_path=PERSISTENT_DIRECTORY, index_name=name, embeddings=EMBEDDING_FUNCTION)
        except Exception as e:
            vector_store = FAISS.from_documents(state.context_chunks, embedding=EMBEDDING_FUNCTION)
            vector_store.save_local(PERSISTENT_DIRECTORY, index_name=name)
        state.vector_store = vector_store

        return {
            "vector_store": state.vector_store,
        }

    def CreateContextChunks(self, state: State) -> State:
        if not state.context_chunks:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 200,
                chunk_overlap = 20
            )

            state.context_chunks = text_splitter.create_documents([state.context])

        return {
            "context_chunks": state.context_chunks
        }

    def CallModel(self, state: State) -> State:
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.model,
            retriever=state.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": prompt_template},
        )

        response = qa_chain.invoke({"query": state.query})
        state.result = response["result"]

        return {
            "result": state.result,
        }