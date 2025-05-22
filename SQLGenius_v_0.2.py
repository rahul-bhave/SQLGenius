"""
List all employees and their departments.

Show who is working on the Website Redesign project.

What is the total salary in the Engineering department?

List all projects with budget over 40000 and people working on them.
"""	
import streamlit as st
import pandas as pd
import sqlite3
import re
import sqlparse
from sqlalchemy import create_engine, text, inspect
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

    cursor.execute("DROP TABLE IF EXISTS employee_projects")
    cursor.execute("DROP TABLE IF EXISTS projects")
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")

    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department_id INTEGER,
            salary INTEGER,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            budget INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE employee_projects (
            employee_id INTEGER,
            project_id INTEGER,
            role TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id),
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    """)

    departments = [("Engineering",), ("Marketing",), ("HR",)]
    cursor.executemany("INSERT INTO departments (name) VALUES (?)", departments)

    employees = [
        ("Alice", 1, 120000),
        ("Bob", 2, 90000),
        ("Charlie", 1, 110000),
        ("Diana", 3, 80000)
    ]
    cursor.executemany("INSERT INTO employees (name, department_id, salary) VALUES (?, ?, ?)", employees)

    projects = [
        ("Website Redesign", 50000),
        ("New Product Launch", 150000),
        ("Recruitment Drive", 30000)
    ]
    cursor.executemany("INSERT INTO projects (name, budget) VALUES (?, ?)", projects)

    employee_projects = [
        (1, 1, "Lead Developer"),
        (2, 1, "Marketing Manager"),
        (3, 2, "Engineer"),
        (4, 3, "Recruiter")
    ]
    cursor.executemany("INSERT INTO employee_projects (employee_id, project_id, role) VALUES (?, ?, ?)", employee_projects)

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

        schema = f"""
        Schema:
        {st.session_state.get("schema_text", "")}
        """

        prompt = (
            f"You are an expert SQL assistant. Based on the following schema and request, write a SQL query.\n"
            f"{schema}\n\n"
            f"Request: {user_input}\n\n"
            f"Respond ONLY with a valid SQL query. No explanation, markdown, or comments."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        full_response = response.choices[0].message.content

        clean_text = full_response.replace("```sql", "").replace("```", "").strip()

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
st.title("🧠 SQLGenius powered by @ Groq + Agno")

# --- Step 1: Groq API Key Input ---
st.info("This app uses Groq API for SQL generation. Please enter your API key below.")
st.subheader("🔐 GROQ API Setup")
st.session_state.setdefault("groq_api_key", "")
st.text_input("Enter your GROQ API Key", type="password", key="groq_api_key")

# Hardcoded model
st.session_state["selected_model"] = "llama3-8b-8192"
st.info("Using preselected model: llama3-8b-8192")

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

        # --- Auto Schema Extraction ---
        inspector = inspect(engine)
        schema_lines = []
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_defs = ", ".join([f"{col['name']} {col['type']}" for col in columns])
            schema_lines.append(f"{table_name}({col_defs})")
        st.session_state.schema_text = "\n".join(schema_lines)
        st.success("✅ Schema extracted successfully.")
        st.code(st.session_state.schema_text, language="sql")

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
