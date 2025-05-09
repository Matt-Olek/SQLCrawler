from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from db_analyst import analyze_database
from db_utility import PostgresDB
from config import LIMIT_QUERY_RESULTS
import time

@tool
def get_current_time_tool():
    '''Get the current time'''
    return "The current time is " + time.strftime("%Y-%m-%d %H:%M:%S")

@tool
def search_database(plain_text_query: str):
    '''Search the database for the given query'''
    llm = ChatOpenAI(model="gpt-4o-mini")
    schema_info = analyze_database(save_to_file=False)
    prompt = f"""
                You are a database expert that converts natural language queries into SQL.
                Database Schema Information:
                {schema_info}

                Natural Language Query: {plain_text_query}

                Generate a SQL query that will answer this question. Return ONLY the SQL query, nothing else juste the raw sql query. No markdown formatting, no ```sql tags, and no other text. Just return the raw SQL query.
                """
    llm_response = llm.invoke(prompt)
    sql_query = llm_response.content
    db = PostgresDB()
    db.connect()
    results = db.execute_query(sql_query)
    db.close()
    full_results = str(results)
    truncated_results = full_results[:LIMIT_QUERY_RESULTS]
    truncated_message = " (truncated)" if len(full_results) > LIMIT_QUERY_RESULTS else ""
    return f"SQL Query executed : {sql_query}\n\nResults : {truncated_results}{truncated_message}"