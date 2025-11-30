import networkx as nx
from pyvis.network import Network

def visualize_knowledge_graph(data):
    # 1. Create a NetworkX graph object first (for the math)
    nx_graph = nx.Graph()
    
    for node in data['nodes']:
        nx_graph.add_node(node['id'], label=node['label'], type=node.get('type'))
    for edge in data['edges']:
        nx_graph.add_edge(edge['source'], edge['target'])
        
    # 2. Calculate PageRank (The "Google" Algorithm for importance)
    # This gives every node a score between 0 and 1
    pagerank_scores = nx.pagerank(nx_graph)
    
    # 3. Build the Visual Graph
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white", cdn_resources='remote')
    
    for node in data['nodes']:
        # Get the math score
        score = pagerank_scores.get(node['id'], 0.1)
        
        # Dynamic Sizing: Base size + (Score * Multiplier)
        # Important nodes become physically larger
        size = 10 + (score * 80) 
        
        # Color logic (keep your gold/blue logic)
        color = "#FFD700" if node.get('type') == 'core' else "#97C2FC"
        
        net.add_node(
            node['id'], 
            label=node['label'], 
            color=color, 
            size=size, # <-- APPLIED MATH HERE
            title=f"Importance Score: {score:.2f}" # Show the math on hover
        )
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'])

    return net.generate_html()