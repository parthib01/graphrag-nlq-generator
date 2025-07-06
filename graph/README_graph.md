# 📊 Knowledge Graph Builder from Retail DB Schema

This module is responsible for extracting the database schema from `retail.db` and converting it into a **knowledge graph** in **Neo4j**. It forms the backbone for enabling **GraphRAG-based SQL generation** in later phases.

---

## 📁 Folder Structure
graph/
├── graph_utils.py # Extracts schema: tables, columns, foreign keys
├── load_graph.py # Loads schema into Neo4j as knowledge graph

How It Works

1. graph_utils.py
Connects to retail.db

Extracts:

All table names

Column names, types, primary keys

Foreign key relationships

Returns schema as a Python dictionary

2. load_graph.py
Connects to Neo4j at bolt://localhost:7687

Clears old graph (optional)

Creates nodes:

(:Table {name})

(:Column {name, type, pk})

Creates relationships:

(:Table)-[:HAS_COLUMN]->(:Column)

(:Column)-[:FOREIGN_KEY]->(:Column)


How to Run
Install Neo4j software (https://neo4j.com/download/neo4j-desktop/?edition=desktop&flavour=winstall64&release=2.0.1&offline=false)
Open and Create Instance using the name "GrpahDB" and password as "Parthib@0103"
Then in vs code run python load_graph.py, output: ✅ Knowledge graph loaded to Neo4j.

After that go to query and run the following cypher to check if it's working:
Example Cypher Queries (Neo4j Browser)

// View all tables
MATCH (t:Table) RETURN t;

// View columns of each table
MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
RETURN t.name, collect(c.name);

// View foreign keys
MATCH (c1:Column)-[:FOREIGN_KEY]->(c2:Column)
RETURN c1.name, c2.name;

Then if you want to see the visual representation of the Graph(database), then go to the following link (ensure the GraphDB instance is running in Neo4j): http://localhost:7474, Credentials: neo4j / password (Parthib@0103)
