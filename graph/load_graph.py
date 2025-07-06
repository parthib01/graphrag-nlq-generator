from py2neo import Graph, Node, Relationship
from graph_utils import extract_schema

# Step 1: Connect to local Neo4j (update credentials if needed)
graph = Graph("neo4j://127.0.0.1:7687", auth=("neo4j", "Parthib@0103"))

# Optional: Clear existing graph
graph.delete_all()

# Step 2: Extract schema from SQLite
schema = extract_schema('../db/retail.db')

# Step 3: Create nodes and relationships
table_nodes = {}
column_nodes = {}

for table, details in schema.items():
    t_node = Node("Table", name=table)
    graph.create(t_node)
    table_nodes[table] = t_node

    for col in details['columns']:
        c_node = Node("Column", name=col["name"], type=col["type"], pk=col["pk"])
        graph.create(c_node)
        column_nodes[f"{table}.{col['name']}"] = c_node

        # HAS_COLUMN relation
        graph.create(Relationship(t_node, "HAS_COLUMN", c_node))

# Step 4: Add FOREIGN_KEY relations
for table, details in schema.items():
    for fk in details['foreign_keys']:
        from_col = column_nodes.get(f"{table}.{fk['from']}")
        to_col = column_nodes.get(f"{fk['to_table']}.{fk['to_column']}")

        if from_col and to_col:
            rel = Relationship(from_col, "FOREIGN_KEY", to_col)
            graph.create(rel)

print("✅ Knowledge graph loaded to Neo4j.")
