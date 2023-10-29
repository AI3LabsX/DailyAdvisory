"""
This module contains handlers that handle messages from users

Handlers:
    echo_handler    - echoes the user's message

Note:
    Handlers are imported into the __init__.py package handlers,
    where a tuple of HANDLERS is assembled for further registration in the application
"""
import openai
import tiktoken
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from tgbot.utils.environment import env

openai.api_key = env.get_openai_api()


async def get_user_data():
    ...

async def generate_chat_completion():
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "system",
                "content": f""
            },
            {
                "role": "user",
                "content": f""
            }
        ],
        "temperature": 0,
        "max_tokens": 500,
        "top_p": 0.4,
        "frequency_penalty": 1.5,
        "presence_penalty": 1
    }
    response = await openai.ChatCompletion.acreate(**data)

    responses = response['choices'][0]['message']['content']

    return responses


async def generate_completion(query: str) -> str:
    data = {
        "engine": "text-davinci-003",
        "prompt": "",
        "temperature": 0,
        "max_tokens": 500,
        "top_p": 0,
        "requency_penalty": 0.43,
        "presence_penalty": 0.35,
        "best_of": 2
    }
    response = await openai.Completion.acreate(**data)
    # Extract the bot's response from the generated text
    answer = response['choices'][0]['text']
    return answer


def ask_question(qa, question: str, chat_history):
    query = f""

    result = qa({"question": query, "chat_history": chat_history})
    print(result)
    print("Question:", question)
    print("Answer:", result["answer"])

    print(result)

    return result["answer"]


async def generate_response(query: str, vectorstore) -> str:
    knowledge = []
    # TODO: Test different things like similarity
    for doc in vectorstore.max_marginal_relevance_search(query, k=10):
        knowledge.append(doc)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": ()
            },
            {
                "role": "system",
                "content": f""
            },
            {
                "role": "user",
                "content": f" "
            }
        ],

        temperature=0,
        max_tokens=3000,
        top_p=0.4,
        frequency_penalty=1.5,
        presence_penalty=1
    )
    bot_response = response['choices'][0]['message']['content']
    return bot_response


def tiktoken_len(text: str) -> int:
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


def process_recursive(documents) -> FAISS:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=200,
        length_function=tiktoken_len,
        separators=['\n\n', '\n', ' ', '']
    )
    embeddings = OpenAIEmbeddings()
    text_chunks = text_splitter.split_text(documents)
    db = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return db


# Create a vector store indexes from the pdfs
def get_vectorstore(text_chunks: list[str]) -> FAISS:
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


