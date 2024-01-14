#!/bin/bash

# Navigate to the project directory
cd /path/to/your/crypto-news-scraper

# Activate your Python environment if you have one
# source /path/to/your/env/bin/activate

# Run the scraper
python scraper/scraper.py

# Load data into the vector database
python database/loader.py

# Query the database and select top news titles
python database/query.py

# Generate articles using the selected news titles
python generator/generator.py

# Post the articles
python poster/poster.py

# Cleanup Redis and CSV
python poster/cleanup.py

# Deactivate the Python environment if you used one
# deactivate