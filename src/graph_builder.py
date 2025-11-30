import networkx as nx
from pyvis.network import Network

def visualize_knowledge_graph(data):
    """
    Generates the HTML for the graph with:
    1. PageRank Math (Node sizing & Tooltips)
    2. Fullscreen Button (Custom JS)
    3. Dark Mode Styling
    """
    
    # --- STEP 1: CALCULATE IMPORTANCE (PageRank) ---
    # We use NetworkX to calculate the mathematical 'weight' of nodes
    nx_graph = nx.Graph()
    
    # Add nodes and edges to the math engine
    for node in data['nodes']:
        nx_graph.add_node(node['id'], label=node['label'], type=node.get('type'))
    for edge in data['edges']:
        nx_graph.add_edge(edge['source'], edge['target'])
        
    try:
        # Calculate PageRank (returns a dictionary of {node_id: score})
        pagerank_scores = nx.pagerank(nx_graph)
    except:
        # Fallback if graph is empty or disconnected
        pagerank_scores = {node['id']: 0.1 for node in data['nodes']}

    # --- STEP 2: BUILD VISUAL NETWORK ---
    # Initialize PyVis (cdn_resources='remote' prevents downloading the local lib folder)
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white", cdn_resources='remote')
    
    for node in data['nodes']:
        # Get the math score (default to 0.1 if missing)
        score = pagerank_scores.get(node['id'], 0.1)
        
        # Color Logic: Differentiate Core vs Sub concepts
        if node.get('type') == 'core':
            color = "#FFD700"  # Gold
        else:
            color = "#97C2FC"  # Light Blue
            
        # Size Logic: Base size + (Score * Multiplier)
        # This makes important nodes physically larger
        size = 10 + (score * 80)
        
        net.add_node(
            node['id'], 
            label=node['label'], 
            color=color, 
            size=size,
            shape="dot",
            title=f"Importance: {score:.2f}" # Tooltip on hover
        )
    
    for edge in data['edges']:
        net.add_edge(edge['source'], edge['target'], title=edge['label'], color="#555555")
    
    # Physics settings for a nice "floating" layout
    net.repulsion(node_distance=150, spring_length=150)
    
    # --- STEP 3: INJECT CUSTOM JAVASCRIPT ---
    try:
        # Generate the standard HTML string in memory
        html_string = net.generate_html()
        
        # Define the custom Button and Script
        fullscreen_code = """
        <style>
            #fullscreen-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background-color: #262730;
                color: white;
                border: 1px solid #4B4B4B;
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 4px;
                font-family: sans-serif;
                font-size: 14px;
                opacity: 0.8;
                transition: opacity 0.2s;
            }
            #fullscreen-btn:hover {
                opacity: 1.0;
                background-color: #333;
            }
        </style>
        
        <button id="fullscreen-btn" onclick="toggleFullScreen()">⛶ Fullscreen</button>
        
        <script>
            function toggleFullScreen() {
                var doc = window.document;
                // 'mynetwork' is the ID PyVis assigns to the graph container
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
        
        # Inject our code right before the body closes
        html_string = html_string.replace("</body>", f"{fullscreen_code}</body>")
        
        return html_string
        
    except Exception as e:
        return f"<div>Error generating graph: {e}</div>"