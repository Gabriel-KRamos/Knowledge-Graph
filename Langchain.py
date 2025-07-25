from neo4j import GraphDatabase
import pandas as pd

NEO4J_URI = "NEO4J_URI"
NEO4J_USERNAME = "NEO4J_USERNAME"
NEO4J_PASSWORD = "NEO4J_PASSWORD"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def import_characters(tx, row):
    tx.run("""
        MERGE (p:Person {nome: $nome})
        MERGE (h:Casa {nome: $casa})
        MERGE (p)-[:BELONGS_TO]->(h)
        SET p.sangue = $sangue, p.patrono = $patrono
    """, nome=row['nome'], casa=row['casa'], sangue=row['sangue'], patrono=row['patrono'])

df = pd.read_csv("characters.csv")

with driver.session() as session:
    for _, row in df.iterrows():
        session.write_transaction(import_characters, row)

print("Dados inseridos com sucesso.")

from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["GOOGLE_API_KEY"] = "GOOGLE_API_KEY"

graph = Neo4jGraph(
    url="NEO4J_URI",
    username="NEO4J_USERNAME"",
    password="NEO4J_PASSWORD"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

question = "Quem tem sangue Sangue puro?"
resposta = chain.invoke(question)

nomes = [row.get("p.nome") for row in resposta.get("context", []) if "p.nome" in row]