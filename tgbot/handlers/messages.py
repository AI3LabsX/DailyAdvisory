"""
This module contains handlers that handle messages from users

Handlers:
    echo_handler    - echoes the user's message

Note:
    Handlers are imported into the __init__.py package handlers,
    where a tuple of HANDLERS is assembled for further registration in the application
"""
import asyncio
from typing import Any

import openai
import tiktoken
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.vectorstores import FAISS

from tgbot.utils.environment import env

openai.api_key = env.get_openai_api()


async def generate_category(topic, description, level):
    prompt = f"Given the topic '{topic}', a short description '{description}', and the user's level '{level}', identify a specific category for advice."
    category = await generate_completion(prompt)
    return category.strip()


async def search_google_for_data(category, topic):
    search_query = f"Recent developments in {category} related to {topic}"
    search_results = await search_token(search_query)
    return search_results


async def generate_advice(user_data, google_data):
    prompt = f"Create an advice based on ypu knowledge, the following user data: {user_data}, and the information gathered from the internet: {google_data}"
    advice = await generate_chat_completion(prompt)
    return advice


async def create_advice(topic, description, level):
    # Step 1: Generate a category from the topic
    category = await generate_category(topic, description, level)

    # Step 2: Google search for data about the category
    google_data = await search_google_for_data(category, topic)

    # Step 3: Generate advice using the GPT model
    user_data = {
        "topic": topic,
        "description": description,
        "level": level,
        "category": category
    }
    advice = await generate_advice(user_data, google_data)

    return advice


async def search_token(prompt: str) -> Any:
    search = GoogleSearchAPIWrapper()

    tool = Tool(
        name="Google Search",
        description="Search Google for recent results.",
        func=search.run,  # Synchronous method
    )

    # Run the synchronous code in a thread pool executor
    return await asyncio.get_event_loop().run_in_executor(None, tool.run, prompt)


async def generate_chat_completion(input_data):
    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {
                "role": "system",
                "content": "You will be given a task by user to create advices on some topic based on you train data "
                           "and given google search data. You have to generate good structured advice text for "
                           "telegram format. "
            },
            {
                "role": "user",
                "content": input_data
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
        "prompt": query,
        "temperature": 0,
        "max_tokens": 500,
        "top_p": 0,
        "frequency_penalty": 0.43,
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
