from pyvis.network import Network

def visualize_knowledge_graph(data):
    """Generates the HTML for the graph with hierarchy colors."""
    
    # Dark mode physics graph
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white", cdn_resources='remote')
    
    for node in data['nodes']:
        # LOGIC: Highlight Core concepts
        if node.get('type') == 'core':
            color = "#FFD700"  # Gold for Main Topics
            size = 25
            shape = "dot"
        else:
            color = "#97C2FC"  # Light Blue for details
            size = 15
            shape = "dot"
            
        net.add_node(
            node['id'], 
            label=node['label'], 
            color=color, 
            size=size,
            shape=shape,
            title=node['id']
        )
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'], title=edge['label'], color="#555555")
    
    # Physics settings for a "bouncy" feel
    net.repulsion(node_distance=150, spring_length=150)
    
    try:
        return net.generate_html()
    except Exception as e:
        return f"<div>Error: {e}</div>"