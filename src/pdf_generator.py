from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'VidGraph.ai - Study Guide', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def create_pdf(transcript, graph_data, quiz_data):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.chapter_title("1. Summary")
    # In a real app, you'd ask Gemini to summarize this. For now, we take the first 500 chars.
    summary = transcript[:1000] + "..."
    pdf.chapter_body(summary)
    
    # 2. Key Vocabulary (from Graph)
    pdf.chapter_title("2. Key Concepts")
    for node in graph_data['nodes']:
        label = node['label']
        # Simple logic to distinguish types
        prefix = "★" if node.get('type') == 'core' else "•"
        pdf.chapter_body(f"{prefix} {label}")
        
    # 3. Practice Quiz
    pdf.add_page()
    pdf.chapter_title("3. Practice Quiz")
    
    for i, q in enumerate(quiz_data):
        pdf.set_font('Arial', 'B', 11)
        pdf.multi_cell(0, 6, f"Q{i+1}: {q['question']}")
        pdf.set_font('Arial', '', 11)
        for opt in q['options']:
            pdf.cell(0, 6, f"   - {opt}", 0, 1)
        pdf.ln(2)
        
    # 4. Answer Key (Upside down or on new page)
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, "--- Answer Key ---", 0, 1)
    for i, q in enumerate(quiz_data):
        pdf.cell(0, 6, f"Q{i+1}: {q['answer']}", 0, 1)
        
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')