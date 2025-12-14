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
        # Latin-1 fix: Replace characters that might crash the PDF generator
        safe_body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, safe_body)
        self.ln()

def create_pdf(summary_text, graph_data, quiz_data):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Executive Summary
    pdf.chapter_title("1. Executive Summary")
    pdf.chapter_body(summary_text)
    
    # 2. Key Concepts (Graph Data)
    pdf.chapter_title("2. Key Concepts (Knowledge Graph)")
    for node in graph_data['nodes']:
        label = node['label']
        prefix = "[CORE]" if node.get('type') == 'core' else "-"
        pdf.chapter_body(f"{prefix} {label}")
        
    # 3. Practice Quiz
    pdf.add_page()
    pdf.chapter_title("3. Practice Quiz")
    
    for i, q in enumerate(quiz_data):
        pdf.set_font('Arial', 'B', 11)
        # Sanitize question text
        q_text = q['question'].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, f"Q{i+1}: {q_text}")
        
        pdf.set_font('Arial', '', 11)
        for opt in q['options']:
            # Sanitize option text
            opt_clean = opt.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 6, f"   - {opt_clean}", 0, 1)
        pdf.ln(2)
        
    # 4. Answer Key
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, "--- Answer Key ---", 0, 1)
    for i, q in enumerate(quiz_data):
        ans_clean = q['answer'].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Q{i+1}: {ans_clean}", 0, 1)
        
    return pdf.output(dest='S').encode('latin-1')