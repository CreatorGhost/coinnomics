import os
from langchain_community.vectorstores.redis import Redis
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import pandas as pd

class VectorDB:
    def __init__(self, redis_host=None, redis_port=None, redis_username=None, redis_password=None, index_name='crypto_news'):
        load_dotenv()  # Load environment variables from .env file
        
        # Use provided credentials or fall back to environment variables
        self.redis_host = redis_host if redis_host is not None else os.getenv('REDIS_HOST')
        self.redis_port = redis_port if redis_port is not None else os.getenv('REDIS_PORT')
        self.redis_username = redis_username if redis_username is not None else os.getenv('REDIS_USERNAME')
        self.redis_password = redis_password if redis_password is not None else os.getenv('REDIS_PASSWORD')
        self.index_name = index_name
        
        self.redis_url = f"redis://{self.redis_username}:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        self.redis_client = None
        self.check_redis_connection()

    def check_redis_connection(self):
        try:
            # Attempt to create a Redis client and ping the server
            self.redis_client = Redis(redis_url=self.redis_url)
            ping_response = self.redis_client.ping()
            if ping_response:
                print("Connected to Redis successfully!")
            else:
                print("Failed to connect to Redis.")
        except Exception as e:
            print(f"An error occurred while connecting to Redis: {e}")
            self.redis_client = None

    def load_documents_to_redis(self, file_path, metadata_columns):
        if not self.redis_client:
            print("Not connected to Redis.")
            return None

        csv_loader = CSVLoader(file_path=file_path, metadata_columns=metadata_columns)
        documents = csv_loader.load()
        embeddings = OpenAIEmbeddings()

        try:
            # Try to load from existing index
            document_store = Redis.from_existing_index(
                embedding=embeddings,
                redis_url=self.redis_url,
                index_name=self.index_name,
                schema="redis_schema.yaml"
            )
            print("Loaded from existing index.")
        except Exception as e:
            # If the index does not exist, create a new one
            document_store = Redis.from_documents(
                documents=documents,
                embedding=embeddings,
                redis_url=self.redis_url,
                index_name=self.index_name
            )
            print("Created a new index.")
            document_store.write_schema("redis_schema.yaml")

        return document_store

    def delete_redis_index(self):
        if not self.redis_client:
            print("Not connected to Redis.")
            return

        try:
            # Delete the index using the class method `drop_index`
            Redis.drop_index(index_name=self.index_name, delete_documents=True, redis_url=self.redis_url)
            print(f"Index '{self.index_name}' deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting the index: {e}")






vectordb = VectorDB()
vectordb.load_documents_to_redis("clean.csv", ["tags", "url", "timestamp"])
# vectordb.delete_redis_index()