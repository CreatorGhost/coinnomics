from database.vectordb import VectorDB
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from pydantic import BaseModel, Field
import pandas as pd
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pprint import pprint

from langchain.schema import HumanMessage, SystemMessage

gpt_model = "gpt-4-1106-preview"
llm = ChatOpenAI(model=gpt_model, temperature=0)


def generate_article():
    # Load data
    df = pd.read_csv("clean.csv")
    titles = df["title"].to_list()

    # Initialize language model

    # Load documents into vector database
    vectordb = VectorDB()
    vectorstore = vectordb.load_documents_to_redis(
        "clean.csv", ["tags", "url", "timestamp"]
    )

    # Initialize retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    # Define prompt template
    template = """
    You are an AI language model assistant. Your task is to write an SEO-friendly news article about the given cryptocurrency topic, using the provided context as a reference. Make sure to follow all the best practices for SEO, including using the right keywords, creating engaging content, and ensuring readability.and also make a quniue title based on the title provided

    Context: {context}

    Topic: {topic}

    SEO-friendly News Article:
    Make sure to provide the response in a json format with keys as title,article,tags
    """

    # Define function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Initialize prompt
    custom_rag_prompt = PromptTemplate.from_template(template)

    # Define chain
    rag_chain = (
        {"context": retriever | format_docs, "topic": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | JsonOutputParser()
    )

    # Invoke chain and print result
    art = rag_chain.invoke(titles[0])
    return art


# Call the function
import json

# article = generate_article()
# with open('article.json', 'w') as json_file:
#     json.dump(article, json_file)

with open("article.json", "r") as json_file:
    article = json.load(json_file)


def generate_image_prompts(article):
    messages = [
        SystemMessage(
            content="You are an AI assistant. Your task is to generate a prompt for an image that visually represents the main theme of the Blockchain-based news article. Remember, you are only generating the prompt, not the actual image. The generated prompt will be passed to a DALLE for image generation"
        ),
        SystemMessage(
            content="Now, generate 5 distinct prompts for images that highlight key events or facts mentioned in the cryptocurrency news article. Each prompt should be unique, cover a different aspect of the article, and start on a new line. Remember, you are only generating the prompts, not the actual images. Avoid using any numbering at the start of the prompts. Each line should start with just the prompt and be as descriptive as possible. The generated prompts will be passed to a DALLE for image generation"
        ),
        HumanMessage(content=article),
    ]

    message = llm.invoke(messages)
    prompts = message.content
    return prompts.split("\n")


def get_top_titles(titles: List[str], k: int = 5):
    # Define prompt template
    string_titles = "\n".join(titles)
    messages = [
        SystemMessage(
            content="You are an AI assistant. Your task is to rank the following news article titles based on their potential to attract user attention and SEO effectiveness. Please identify the top 5 titles that are most likely to attract users. Feel free to modify the titles to make them more engaging, catchy, and SEO-friendly. Return only the titles, starting each with 'Title: '."
        ),
        HumanMessage(content=string_titles),
    ]

    # Invoke chain and get result
    result = llm.invoke(messages)

    # Split the result into lines and take the top k
    ranked_titles = result.content.split("\n")[:k]
    ranked_titles = [title.replace('Title: "', '').rstrip('"') for title in ranked_titles]
    return ranked_titles


df = pd.read_csv("clean.csv")
titles = df["title"].to_list()

title_lst = get_top_titles(titles=titles)

pprint(title_lst)
