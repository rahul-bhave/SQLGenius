import streamlit as st
import pandas as pd
import sqlite3
import re
import sqlparse
from sqlalchemy import create_engine, text
from agno.agent import Agent
from groq import Groq

# ----------- DB Helper -----------
def get_engine(db_type, config):
    if db_type == "SQLite":
        return create_engine("sqlite:///sample.db")
    elif db_type == "PostgreSQL":
        return create_engine(
            f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
        )
    elif db_type == "MySQL":
        return create_engine(
            f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
        )

def setup_sqlite():
    conn = sqlite3.connect("sample.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            salary INTEGER
        )
    """)
    cursor.execute("DELETE FROM employees")
    cursor.executemany(
        "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
        [("Alice", "Engineering", 120000), ("Bob", "HR", 80000), ("Charlie", "Marketing", 95000)]
    )
    conn.commit()
    conn.close()

# ----------- Agents -----------
class SQLConnectorAgent(Agent):
    def connect(self, engine):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "✅ Connection successful!"
        except Exception as e:
            return f"❌ Connection failed: {str(e)}"

class SQLCreatorAgent(Agent):
    def generate_sql(self, user_input):
        client = Groq(api_key=st.session_state.groq_api_key)
        model = st.session_state.selected_model
        prompt = (
            f"Convert this business request to SQL for {st.session_state.db_type}. "
            f"Respond with ONLY the SQL query. No explanation, no markdown, no comments:\n\n"
            f"{user_input}"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        full_response = response.choices[0].message.content

        # Remove markdown/code block
        clean_text = full_response.replace("```sql", "").replace("```", "").strip()

        # Extract valid SQL
        parsed = sqlparse.parse(clean_text)
        if parsed and len(parsed) > 0:
            return str(parsed[0]).strip()
        else:
            return "-- Error: No valid SQL statement found."

class SQLRunnerAgent(Agent):
    def run_query(self, query, engine):
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            return df
        except Exception as e:
            return f"Error running query: {str(e)}"

# ----------- Streamlit UI -----------
st.set_page_config(page_title="Agentic SQL App", layout="centered")
st.title("🧠 Agentic SQL Team Workflow (Groq + Agno)")

# --- Step 1: Groq API Key Input ---
st.subheader("🔐 GROQ API Setup")
st.session_state.setdefault("groq_api_key", "")
st.session_state.setdefault("selected_model", "")
st.text_input("Enter your GROQ API Key", type="password", key="groq_api_key")

available_models = []
if st.session_state.groq_api_key:
    try:
        groq_client = Groq(api_key=st.session_state.groq_api_key)
        models_response = groq_client.models.list()
        available_models = [m.id for m in models_response.data]
        st.session_state.available_models = available_models
    except Exception as e:
        st.error(f"Error fetching Groq models: {str(e)}")

if "available_models" in st.session_state and st.session_state.available_models:
    selected_model = st.selectbox("🧠 Choose a Groq Model", st.session_state.available_models)
    st.session_state.selected_model = selected_model

# --- Step 2: Select DB Type ---
st.subheader("🗄️ Database Configuration")
db_type = st.selectbox("Select Database Type", ["SQLite", "PostgreSQL", "MySQL"])
st.session_state.db_type = db_type

db_config = {}
if db_type == "SQLite":
    st.info("SQLite uses a local file `sample.db`.")
    if st.button("🔧 Setup Sample SQLite Database"):
        setup_sqlite()
        st.success("Sample data loaded into SQLite.")
else:
    db_config["host"] = st.text_input("Host", value="localhost")
    db_config["port"] = st.text_input("Port", value="5432" if db_type == "PostgreSQL" else "3306")
    db_config["user"] = st.text_input("Username", value="postgres" if db_type == "PostgreSQL" else "root")
    db_config["password"] = st.text_input("Password", type="password")
    db_config["dbname"] = st.text_input("Database Name")

# --- Step 3: Connect to DB ---
if st.button("🔌 Connect to Database"):
    try:
        engine = get_engine(db_type, db_config)
        st.session_state.engine = engine
        connector = SQLConnectorAgent(name="SQLConnector")
        result = connector.connect(engine)
        st.info(result)
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# --- Step 4: Business Requirement Input ---
st.subheader("📋 Enter Business Requirement")
user_input = st.text_area("Describe what you want from the data in natural language:")

# --- Step 5: Generate SQL from Requirement ---
if st.button("🧠 Generate SQL from Prompt"):
    if not st.session_state.get("groq_api_key") or not st.session_state.get("selected_model"):
        st.warning("Please enter your Groq API Key and select a model.")
    elif user_input.strip() == "":
        st.warning("Please enter a business requirement.")
    else:
        creator = SQLCreatorAgent(name="SQLCreator")
        generated_sql = creator.generate_sql(user_input)
        st.session_state.generated_sql = generated_sql

# --- Step 6: Edit SQL Query ---
if "generated_sql" in st.session_state:
    st.subheader("📝 Review and Approve SQL")
    edited_sql = st.text_area("Edit SQL if needed:", value=st.session_state.generated_sql, height=150, key="edited_sql")
    if st.button("✅ Approve and Run SQL"):
        if "engine" not in st.session_state:
            st.error("Please connect to a database first.")
        else:
            runner = SQLRunnerAgent(name="SQLRunner")
            result = runner.run_query(edited_sql, st.session_state.engine)
            if isinstance(result, pd.DataFrame):
                st.dataframe(result)
            else:
                st.error(result)
