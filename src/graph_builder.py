import networkx as nx
from pyvis.network import Network

def visualize_knowledge_graph(data):
    """
    Generates the HTML for the graph with:
    1. PageRank Math (Node sizing & Tooltips)
    2. Fullscreen Button (Custom JS)
    3. Modern Light Theme (White BG, Vibrant Nodes)
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
    # THEME UPDATE: White background, Dark text
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", cdn_resources='remote')
    
    for node in data['nodes']:
        score = pagerank_scores.get(node['id'], 0.1)
        
        # COLOR UPDATE: Lively "Candy" Palette
        if node.get('type') == 'core':
            color = "#FF6B6B"  # Vibrant Coral (Core)
        else:
            color = "#4ECDC4"  # Fresh Teal (Sub)
            
        size = 10 + (score * 80)
        
        net.add_node(
            node['id'], 
            label=node['label'], 
            color=color, 
            size=size,
            shape="dot",
            title=f"Importance: {score:.2f}",
            borderWidth=2,
            font={'size': 14, 'face': 'sans-serif'}
        )
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'], title=edge['label'], color="#cccccc")
    
    net.repulsion(node_distance=120, spring_length=120)
    
    # --- STEP 3: INJECT CUSTOM JAVASCRIPT ---
    try:
        html_string = net.generate_html()
        
        # Update Button Styling for Light Mode
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