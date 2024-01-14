from database.vectordb import VectorDB
from langchain.chains import LLMChain
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser

df = pd.read_csv("clean.csv")
titles = df["title"].to_list()

gpt_model = "gpt-4-1106-preview"

llm = ChatOpenAI(model=gpt_model, temperature=0)

vectordb = VectorDB()
vectorstore = vectordb.load_documents_to_redis("clean.csv", ["tags", "url", "timestamp"])

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
from langchain_core.prompts import PromptTemplate

print(titles[0])

template = """You are an AI language model assistant. Your task is to write an SEO-friendly news article about the given cryptocurrency topic, using the provided context as a reference. Make sure to follow all the best practices for SEO, including using the right keywords, creating engaging content, and ensuring readability.and also make a quniue title based on the title provided

Context: {context}

Topic: {topic}

SEO-friendly News Article:"""


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


custom_rag_prompt = PromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever | format_docs, "topic": RunnablePassthrough()}
    | custom_rag_prompt
    | llm
)

art = rag_chain.invoke(titles[0])

print(art)