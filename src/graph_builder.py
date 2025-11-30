from pyvis.network import Network

def visualize_knowledge_graph(data):
    """Generates the HTML for the graph with hierarchy colors and a Fullscreen button."""
    
    # 1. Build the Network
    # We set width to 100% so it fills the container (or fullscreen mode)
    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white", cdn_resources='remote')
    
    for node in data['nodes']:
        # Logic: Highlight Core concepts
        if node.get('type') == 'core':
            color = "#FFD700"  # Gold
            size = 25
            shape = "dot"
        else:
            color = "#97C2FC"  # Blue
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
    
    net.repulsion(node_distance=150, spring_length=150)
    
    # 2. Generate Base HTML
    try:
        # We generate the HTML string in memory
        html_string = net.generate_html()
        
        # 3. INJECT CUSTOM JAVASCRIPT FOR FULLSCREEN
        # We insert a style and button right before the closing </body> tag
        fullscreen_code = """
        <style>
            /* Style the button to look like a floating tool */
            #fullscreen-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000; /* Ensure it sits on top of the graph */
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
                // 'mynetwork' is the default ID used by PyVis for the graph container
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
        
        # Inject the code into the HTML
        html_string = html_string.replace("</body>", f"{fullscreen_code}</body>")
        
        return html_string
        
    except Exception as e:
        return f"<div>Error generating graph: {e}</div>"