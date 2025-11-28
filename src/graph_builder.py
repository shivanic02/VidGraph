from pyvis.network import Network
import streamlit.components.v1 as components

def visualize_knowledge_graph(data):
    """
    Converts JSON data (nodes/edges) into an interactive PyVis graph
    and returns the HTML string for Streamlit to render.
    """
    # 1. Initialize the Graph
    # height="600px", width="100%", bgcolor="#222222" (Dark Mode), font_color="white"
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white")
    
    # 2. Add Nodes
    for node in data['nodes']:
        net.add_node(
            node['id'], 
            label=node['label'], 
            color=node['color'],
            title=node['id'] # Tooltip when hovering
        )
    
    # 3. Add Edges
    for edge in data['edges']:
        net.add_edge(
            edge['source'], 
            edge['target'], 
            title=edge['label'], # Tooltip shows relationship
            width=2
        )
    
    # 4. Set Physics (This makes the nodes float nicely)
    net.repulsion(
        node_distance=200, 
        central_gravity=0.33, 
        spring_length=150, 
        spring_strength=0.10, 
        damping=0.95
    )
    
    # 5. Export to HTML string
    try:
        # Save momentarily to read back as string
        path = "tmp_graph.html"
        net.save_graph(path)
        
        with open(path, 'r', encoding='utf-8') as f:
            html_string = f.read()
        return html_string
        
    except Exception as e:
        return f"<div>Error generating graph: {e}</div>"