from pyvis.network import Network

def visualize_knowledge_graph(data):
    """Generates the HTML for the graph."""
    # cdn_resources='remote' prevents the 'lib' folder creation
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white", cdn_resources='remote')
    
    for node in data['nodes']:
        net.add_node(node['id'], label=node['label'], color=node['color'], title=node['id'])
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'], title=edge['label'])
    
    net.repulsion(node_distance=200, spring_length=150)
    
    try:
        return net.generate_html()
    except Exception as e:
        return f"<div>Error: {e}</div>"