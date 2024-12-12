# pylint: skip-file
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()  # Load all the environment variables

import streamlit as st
import os
import sqlite3

import google.generativeai as genai

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt, db_contents):
    # Add database state information to the prompt
    db_info = "\n".join([
        f"Table: {table_name}\nColumns: {', '.join(table_data['columns'])}\nRows: {len(table_data['rows'])}"
        for table_name, table_data in db_contents.items()
    ])
    full_prompt = prompt[0] + "\n\nCurrent Database State:\n" + db_info
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([full_prompt, question])
    return response.text

# Function to retrieve and execute multiple queries from the database
def execute_multiple_sql_queries(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    results = []

    try:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
                if statement.lower().startswith("select"):
                    results.append(cur.fetchall())
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.commit()
        conn.close()

    return results

# Function to get all tables and their contents from the database
def get_database_contents(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Get all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    database_contents = {}

    for table in tables:
        table_name = table[0]
  