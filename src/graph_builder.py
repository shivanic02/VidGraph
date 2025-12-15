import networkx as nx
from pyvis.network import Network
import textwrap

def visualize_knowledge_graph(data):
    """
    Generates the HTML for the graph with:
    1. Multi-line Labels (Full text, wrapped nicely)
    2. Aggressive 'Avoid Overlap' physics
    3. 'Relevance: 10%' Tooltips
    4. Fullscreen Button
    """
    
    # --- STEP 1: CALCULATE IMPORTANCE (PageRank) ---
    nx_graph = nx.Graph()
    for node in data['nodes']:
        nx_graph.add_node(node['id'], label=node['label'], type=node.get('type'))
    for edge in data['edges']:
        # NETWORKX FIX: Only add edge if both nodes exist in the data
        # (This prevents crashes if the AI hallucinates an edge)
        all_node_ids = [n['id'] for n in data['nodes']]
        if edge['source'] in all_node_ids and edge['target'] in all_node_ids:
            nx_graph.add_edge(edge['source'], edge['target'])
        
    try:
        pagerank_scores = nx.pagerank(nx_graph)
    except:
        pagerank_scores = {node['id']: 0.1 for node in data['nodes']}

    # --- STEP 2: BUILD VISUAL NETWORK ---
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", cdn_resources='remote')
    
    # Track added nodes to prevent edge errors
    added_node_ids = set()

    for node in data['nodes']:
        score = pagerank_scores.get(node['id'], 0.1)
        
        # Color Logic
        if node.get('type') == 'core':
            color = "#FF6B6B"  # Vibrant Coral
        else:
            color = "#4ECDC4"  # Fresh Teal
            
        size = 10 + (score * 80)
        
        # LABEL FIX: Wrap text nicely
        full_label = node['label']
        wrapped_label = "\n".join(textwrap.wrap(full_label, width=20)) 
        
        # TOOLTIP FIX: "Relevance: 10%"
        hover_text = f"{full_label}\nRelevance: {score:.0%}"
        
        net.add_node(
            node['id'], 
            label=wrapped_label, 
            title=hover_text,
            color=color, 
            size=size,
            shape="dot",
            borderWidth=2,
            font={'size': 14, 'face': 'sans-serif'}
        )
        added_node_ids.add(node['id'])
    
    # PYVIS FIX: Only add edge if both nodes were actually added to the graph
    for edge in data['edges']:
        if edge['source'] in added_node_ids and edge['target'] in added_node_ids:
            net.add_edge(edge['source'], edge['target'], color="#cccccc")
    
    # --- PHYSICS FIX: FORCE SEPARATION ---
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.3,
          "springLength": 300,
          "springConstant": 0.05,
          "damping": 0.09,
          "avoidOverlap": 1
        }
      }
    }
    """)
    
    # --- STEP 3: INJECT CUSTOM JAVASCRIPT ---
    try:
        html_string = net.generate_html()
        
        fullscreen_code = """
        <style>
            #fullscreen-btn {
                position: absolute;
                top: 15px;
                right: 15px;
                z-index: 1000;
                background-color: white;
                color: #333;
                border: 2px solid #ddd;
                padding: 8px 15px;
                cursor: pointer;
                border-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.2s ease;
            }
            #fullscreen-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0,0,0,0.15);
                border-color: #FF6B6B;
                color: #FF6B6B;
            }
        </style>
        
        <button id="fullscreen-btn" onclick="toggleFullScreen()">⛶ Fullscreen</button>
        
        <script>
            function toggleFullScreen() {
                var doc = window.document;
                var docEl = doc.getElementById('mynetwork'); 

                var requestFullScreen = docEl.requestFullscreen || docEl.mozRequestFullScreen || docEl.webkitRequestFullScreen || docEl.msRequestFullscreen;
                var cancelFullScreen = doc.exitFullscreen || doc.mozCancelFullScreen || doc.webkitExitFullscreen || doc.msExitFullscreen;

                if(!doc.fullscreenElement && !doc.mozFullScreenElement && !doc.webkitFullscreenElement && !doc.msFullscreenElement) {
                    requestFullScreen.call(docEl);
                }
                else {
                    cancelFullScreen.call(doc);
                }
            }
        </script>
        """
        html_string = html_string.replace("</body>", f"{fullscreen_code}</body>")
        return html_string
        
    except Exception as e:
        return f"<div>Error generating graph: {e}</div>"