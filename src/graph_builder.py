import networkx as nx
from pyvis.network import Network
import textwrap

def visualize_knowledge_graph(data):
    """
    Generates the HTML for the graph with:
    1. Multi-line Labels (Full text, wrapped nicely)
    2. Increased Spacing (Physics adjustment)
    3. PageRank Math & Fullscreen Button
    """
    
    # --- STEP 1: CALCULATE IMPORTANCE (PageRank) ---
    nx_graph = nx.Graph()
    for node in data['nodes']:
        nx_graph.add_node(node['id'], label=node['label'], type=node.get('type'))
    for edge in data['edges']:
        nx_graph.add_edge(edge['source'], edge['target'])
        
    try:
        pagerank_scores = nx.pagerank(nx_graph)
    except:
        pagerank_scores = {node['id']: 0.1 for node in data['nodes']}

    # --- STEP 2: BUILD VISUAL NETWORK ---
    # THEME: White background, Dark text
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", cdn_resources='remote')
    
    for node in data['nodes']:
        score = pagerank_scores.get(node['id'], 0.1)
        
        # Color Logic
        if node.get('type') == 'core':
            color = "#FF6B6B"  # Vibrant Coral
        else:
            color = "#4ECDC4"  # Fresh Teal
            
        size = 10 + (score * 80)
        
        # LABEL FIX: Wrap text instead of shortening it
        # This keeps the full meaning but makes the node "taller" rather than "wider"
        full_label = node['label']
        wrapped_label = "\n".join(textwrap.wrap(full_label, width=20)) 
        
        net.add_node(
            node['id'], 
            label=wrapped_label, # Shows full text on multiple lines
            title=f"Importance: {score:.2f}",
            color=color, 
            size=size,
            shape="dot",
            borderWidth=2,
            font={'size': 14, 'face': 'sans-serif'}
        )
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'], color="#cccccc")
    
    # PHYSICS FIX: Increase distance significantly to handle multi-line text
    net.repulsion(
        node_distance=250,  # Push nodes much further apart
        spring_length=250,  # Make edges longer
        central_gravity=0.1 # Relax gravity
    )
    
    # --- STEP 3: INJECT CUSTOM JAVASCRIPT ---
    try:
        html_string = net.generate_html()
        
        # Custom Fullscreen Button Styling
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