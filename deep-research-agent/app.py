import streamlit as st
import os
import sys
import json
import time
import re
from io import BytesIO
from dotenv import load_dotenv
from fpdf import FPDF

# Load env vars *before* importing scaledown to ensure keys are picked up
load_dotenv()

# Ensure scaledown and local agents are in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from agents import create_research_graph
import scaledown
scaledown.set_api_key(os.getenv("SCALEDOWN_API_KEY"))

st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS for UI Fixes ===
st.markdown("""
    <style>
    /* Fix horizontal scrolling and ensure text wraps */
    .stMarkdown, .stTextArea, div[data-testid="stExpander"] {
        overflow-x: hidden !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    
    /* Ensure long references or blocks don't force width */
    pre, code {
        white-space: pre-wrap !important;
        word-break: break-all !important;
    }
    </style>
""", unsafe_allow_html=True)

def sanitize_text(text):
    """
    Replaces common Unicode characters that are not supported by standard PDF fonts (latin-1)
    with their nearest ASCII equivalents.
    """
    if not text:
        return ""
    
    # Map of Unicode characters to ASCII/Latin-1 equivalents
    replacements = {
        '\u2014': '--',  # em dash
        '\u2013': '-',   # en dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2022': '*',   # bullet point
        '\u2026': '...', # ellipsis
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
        
    # Final fallback: encode to latin-1 and ignore remaining problematic characters
    # This prevents the "Character X is outside range" error from crashing the app
    return text.encode('latin-1', 'replace').decode('latin-1')

# === IEEE PDF Generator Class ===
class IEEEPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('Times', 'I', 8)
            self.cell(0, 10, sanitize_text('Proceedings of the International Conference on Edge Computing and Applications (ICECAA 2022)'), 0, 1, 'C')
            self.ln(-6)
            self.cell(0, 10, sanitize_text('IEEE Xplore Part Number: CFP22BV8-ART; ISBN: 978-1-6654-8232-5'), 0, 1, 'C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_title(self, title):
        self.set_font('Times', 'B', 24)
        self.multi_cell(0, 15, sanitize_text(title), 0, 'C')
        self.ln(10)

    def add_author_block(self):
        self.set_font('Times', '', 11)
        self.cell(0, 5, "Deep Research Agent Swarm", 0, 1, 'C')
        self.set_font('Times', 'I', 10)
        self.cell(0, 5, "ScaleDown Multi-Agent Laboratory", 0, 1, 'C')
        self.cell(0, 5, "autonomous-research@scaledown.ai", 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('Times', 'B', 11)
        # Convert markdown headers to IEEE style (Roman numerals or just Bold Caps)
        self.cell(0, 10, sanitize_text(label.upper()), 0, 1, 'L')
        self.ln(1)

    def chapter_body(self, text):
        self.set_font('Times', '', 10)
        self.multi_cell(0, 5, sanitize_text(text), 0, 'J')
        self.ln()

def generate_ieee_pdf(report_md, task_name):
    pdf = IEEEPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Extract Title from markdown or use task
    title = task_name
    lines = report_md.split('\n')
    if lines[0].startswith('# '):
        title = lines[0].replace('# ', '').strip()
        report_md = '\n'.join(lines[1:])

    pdf.add_title(title)
    pdf.add_author_block()

    # Simple Markdown to PDF mapping
    sections = re.split(r'\n##\s+', report_md)
    
    # Handle the first part (Abstract/Intro before the first ##)
    first_part = sections[0].strip()
    if first_part:
        if first_part.lower().startswith('abstract'):
             # Special formatting for Abstract
             pdf.set_font('Times', 'BI', 10)
             pdf.write(5, "Abstract—")
             pdf.set_font('Times', 'B', 10)
             # Abstract text after 'Abstract' and potential separator
             abstract_content = re.sub(r'^(?i)abstract[\s—:-]*', '', first_part).strip()
             pdf.chapter_body(abstract_content)
        else:
             pdf.chapter_body(first_part)

    for section in sections[1:]:
        lines = section.split('\n', 1)
        if len(lines) == 2:
            header, content = lines
            pdf.chapter_title(header.strip())
            # Clean up nested markdown (minimal)
            content = content.replace('### ', '').replace('**', '').replace('* ', '- ')
            pdf.chapter_body(content.strip())

    return bytes(pdf.output())

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report" not in st.session_state:
    st.session_state.report = None
if "task_query" not in st.session_state:
    st.session_state.task_query = ""
if "metrics" not in st.session_state:
    st.session_state.metrics = {"iteration": 0, "confidence": 0.0, "tokens_saved": 0}

# Sidebar Configuration
with st.sidebar:
    st.title("🧠 Deep Research Agent")
    st.markdown("Powered by **ScaleDown** & **LangGraph**")
    
    st.subheader("Configuration")
    
    api_key_status = "✅ Configured" if os.getenv("OPENROUTER_API_KEY") else "❌ Missing"
    sd_key_status = "✅ Configured" if os.getenv("SCALEDOWN_API_KEY") else "⚠️ Optional (Missing)"
    
    st.text(f"LLM API: {api_key_status}")
    st.text(f"ScaleDown API: {sd_key_status}")
    
    st.divider()
    
    st.markdown("### Metrics")
    iter_placeholder = st.sidebar.empty()
    conf_placeholder = st.sidebar.empty()
    
    # Initialize placeholders
    iter_placeholder.metric("Iteration", st.session_state.metrics["iteration"])
    conf_placeholder.metric("Confidence", f"{st.session_state.metrics['confidence']:.2f}")
    st.metric("ScaleDown Optimization", "Active")

st.title("Collaborative AI Research Team")
st.markdown("Enter a research topic below to initialize the multi-agent workflow.")

query = st.text_area("Research Query", height=100, placeholder="e.g. Advancements in Solid State Batteries in 2024")

start_btn = st.button("Start Research", type="primary")

if start_btn and query:
    st.session_state.messages = [] # Clear previous run
    st.session_state.report = None
    st.session_state.task_query = query
    st.session_state.metrics = {"iteration": 0, "confidence": 0.0, "tokens_saved": 0}
    
    # Update placeholders immediately on start
    iter_placeholder.metric("Iteration", 0)
    conf_placeholder.metric("Confidence", "0.00")
    
    # Create Graph
    try:
        graph = create_research_graph()
    except Exception as e:
        st.error(f"Failed to initialize agent graph: {e}")
        st.stop()
        
    inputs = {"task": query, "iteration": 0}
    
    # Main Execution Loop
    with st.status("Initializing Agents...", expanded=True) as status:
        try:
            for output in graph.stream(inputs):
                for key, value in output.items():
                    # Update Metrics in session state AND real-time placeholders
                    if "iteration" in value:
                        st.session_state.metrics["iteration"] = value["iteration"]
                        iter_placeholder.metric("Iteration", value["iteration"])
                    if "confidence" in value:
                        st.session_state.metrics["confidence"] = value["confidence"]
                        conf_placeholder.metric("Confidence", f"{value['confidence']:.2f}")
                        
                    # Display Step Info
                    if key == "researcher":
                        status.update(label="🔍 Researcher is gathering data...", state="running")
                        with st.expander(f"Researcher Thinking (Iter {value.get('iteration', '?')})", expanded=False):
                            st.json(value.get("research_data", {}))
                            
                    elif key == "critic":
                        status.update(label="⚖️ Critic is reviewing evidence...", state="running")
                        conf = value.get("confidence", 0.0)
                        if conf < 0.7:
                             st.toast(f"Critic rejected some claims. Confidence: {conf:.2f}. Retrying...", icon="🔄")
                        else:
                             st.toast(f"Critic verified claims! Confidence: {conf:.2f}. Proceeding...", icon="✅")
                             
                        with st.expander("Critic Feedback", expanded=False):
                            st.json(value.get("critique", {}))
                            
                    elif key == "synthesizer":
                        status.update(label="🧩 Synthesizer is compressing context...", state="running")
                        with st.expander("Synthesized Context (ScaleDown)", expanded=False):
                            st.json(value.get("synthesis", {}))
                            
                    elif key == "writer":
                        status.update(label="✍️ Writer is generating final report...", state="running")
                        report = value.get("report", "")
                        st.session_state.report = report
                
                # No longer using st.rerun here to avoid breaking the event loop
                pass
            
            # Keep expanded=True so the "Thinking" expanders stay visible!
            status.update(label="Research Complete!", state="complete", expanded=True)
            # Final sync for persistence
            st.rerun() if hasattr(st, "rerun") else st.experimental_rerun()
            
        except Exception as e:
            st.error(f"Error during execution: {e}")
            # Ensure it stays expanded even on failure to see what went wrong
            status.update(label="Execution Failed", state="error", expanded=True)

# Display Final Report
if st.session_state.report:
    st.divider()
    st.subheader("📄 Research Report")
    st.markdown(st.session_state.report)
    
    # PDF Generation
    try:
        pdf_bytes = generate_ieee_pdf(st.session_state.report, st.session_state.task_query)
        
        st.download_button(
            label="Download IEEE Research Paper (PDF)",
            data=pdf_bytes,
            file_name=f"IEEE-Research-{int(time.time())}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Could not generate PDF: {e}")
        st.download_button(
            label="Download Raw Report (Markdown)",
            data=st.session_state.report,
            file_name="research_report.md",
            mime="text/markdown"
        )

