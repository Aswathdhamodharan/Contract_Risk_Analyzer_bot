import streamlit as st
import config

# Page Config - Must be the first Streamlit command
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
import utils
from contract_analyzer import ContractAnalyzer
import template_generator
import datetime
import json

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
    }
    .risk-high {
        background-color: #FEE2E2;
        padding: 5px;
        border-radius: 5px;
        border-left: 5px solid #DC2626;
    }
    .risk-medium {
        background-color: #FEF3C7;
        padding: 5px;
        border-radius: 5px;
        border-left: 5px solid #D97706;
    }
    .risk-low {
        background-color: #D1FAE5;
        padding: 5px;
        border-radius: 5px;
        border-left: 5px solid #059669;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title(f"{config.APP_ICON} Legalis")
    st.markdown("### AI Contract Assistant")
    
    api_key_input = st.text_input("Google API Key", type="password", help="Enter your Gemini API key from Google AI Studio")
    
    if api_key_input:
        api_key = api_key_input.strip()
    else:
        api_key = config.GOOGLE_API_KEY
        if "YOUR_API_KEY" in api_key:
            st.warning("⚠️ Please provide a Google API Key to analyze contracts.")
            api_key = None
            
    # Model Selection (Fix for 404 errors)
    model_options = ["gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro-latest"]
    selected_model = st.selectbox("Select Model", model_options, index=0, help="Try switching if you get a 404 error.")
            
    st.markdown("---")
    st.markdown("### 📝 How to Use")
    st.info("""
    1. Upload a contract (PDF, DOCX)
    2. Click 'Analyze Contract'
    3. Review Risks & Suggestions
    4. Download Report
    """)
    st.markdown("---")
    st.markdown("### 🏛️ Templates")
    template_type = st.selectbox("Select Template", ["Employment Agreement", "Vendor Agreement", "Office Lease"])
    if st.button("Generate Template"):
        if template_type == "Employment Agreement":
            st.download_button("Download Template", template_generator.get_employment_agreement_template(), "employment_template.txt")
        elif template_type == "Vendor Agreement":
            st.download_button("Download Template", template_generator.get_vendor_service_template(), "vendor_template.txt")
        elif template_type == "Office Lease":
            st.download_button("Download Template", template_generator.get_lease_template(), "lease_template.txt")

# Main Content
st.markdown(f'<div class="main-header">{config.APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown("GenAI-powered legal assistant for Indian SMEs")

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Input Section
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx", "txt"])

with col2:
    st.markdown("### OR")
    if st.button("Load Sample Contract"):
        # Create a dummy sample logic
        st.session_state.sample_loaded = True
        st.success("Sample contract loaded! Click Analyze.")

if uploaded_file or st.session_state.get("sample_loaded"):
    if uploaded_file:
        file_obj = uploaded_file
        contract_text = utils.extract_text(uploaded_file)
    else:
        # Dummy text for sample
        file_obj = None
        contract_text = template_generator.get_vendor_service_template() # Use one of our templates as sample
        
    st.text_area("Contract Preview", contract_text[:1000] + "...", height=150)
    
    # Language Detection
    lang = utils.detect_language(contract_text)
    if lang == "Hindi":
        st.info("🇮🇳 Hindi Language Detected. The bot will translate and analyze in English.")
    
    if st.button("🔍 Analyze Contract"):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        else:
            with st.spinner("🤖 Beep Boop... analyzing risks and clauses..."):
                analyzer = ContractAnalyzer(api_key, model_name=selected_model)
                
                # Double check to prevent using placeholder key if user forgot
                if "YOUR_API_KEY" in analyzer.api_key:
                     st.error("Invalid API Key. Please update config.py or enter key in sidebar.")
                else:
                    result = analyzer.analyze_contract(contract_text)
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.analysis_result = result
                        st.success("Analysis Complete!")

# Results Display
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    
    # Dashboard Metrics
    st.markdown("## 📊 Risk Dashboard")
    
    risk_meta = res.get("risk_metadata", {})
    score = risk_meta.get("score", 0)
    level = risk_meta.get("level", "Unknown")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Overall Risk Score", f"{score}/10", delta_color="inverse" if score > 6 else "normal")
    m2.metric("Risk Level", level)
    m3.metric("High Risk Clauses", risk_meta.get("high_risk_clauses", 0))
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "⚠️ Risk Analysis", "📋 Clauses", "📉 Visuals"])
    
    with tab1:
        st.subheader("Contract Summary")
        st.write(res.get("summary", "No summary available."))
        
        st.subheader("Key Details")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Type:**", res.get("contract_type", "Unknown"))
            st.write("**Jurisdiction:**", res.get("jurisdiction", "Unknown"))
        with col_b:
            st.write("**Parties:**", ", ".join(res.get("parties", [])))
            st.write("**Date:**", res.get("contract_date", "Unknown"))
            
    with tab2:
        st.subheader("Risk Assessment")
        
        clauses = res.get("clauses", [])
        risky_clauses = [c for c in clauses if c.get("risk_level", "Low").lower() in ["high", "medium"] or c.get("risk_score", 0) > 4]
        
        if not risky_clauses:
            st.success("No high risk clauses detected.")
        
        for c in risky_clauses:
            r_level = c.get("risk_level", "Medium")
            css_class = "risk-high" if r_level.lower() == "high" else "risk-medium"
            
            with st.container():
                st.markdown(f"""
                <div class="{css_class}">
                    <h4>{c.get('title', 'Clause')} ({r_level} Risk)</h4>
                    <p><b>Text:</b> {c.get('text', '')}</p>
                    <p><b>Why it's risky:</b> {c.get('explanation', '')}</p>
                    <p><b>Recommendation:</b> {c.get('recommendation', '')}</p>
                </div>
                <br>
                """, unsafe_allow_html=True)
                
    with tab3:
        st.subheader("Full Clause Analysis")
        for c in res.get("clauses", []):
            with st.expander(f"{c.get('id', '#')} - {c.get('title', 'Clause')}"):
                st.write(c.get('text'))
                st.info(f"Analysis: {c.get('explanation')}")
                
    with tab4:
        st.subheader("Risk Logic Visualization")
        # Ensure we have data for the chart
        clauses = res.get("clauses", [])
        if clauses:
            df = pd.DataFrame(clauses)
            if 'risk_score' in df.columns and 'title' in df.columns:
                fig = px.bar(df, x='title', y='risk_score', color='risk_score', 
                             title="Risk Score per Clause", range_y=[0, 10],
                             color_continuous_scale=['green', 'orange', 'red'])
                st.plotly_chart(fig)
            else:
                st.info("Insufficient data for visualization.")
        else:
            st.info("No clauses found.")

    # Audit Log / Export
    st.markdown("---")
    st.header("🖨️ Actions")
    
    # Audit Log logic (stored in local JSON as requested)
    if st.button("Save to Audit Log"):
        log_entry = {
            "timestamp": str(datetime.datetime.now()),
            "score": score,
            "summary": res.get("summary")
        }
        with open("audit_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        st.success("Analysis saved to audit log.")
        
    # PDF Export Mock
    st.download_button("Export Report as PDF", data=json.dumps(res, indent=2), file_name="contract_analysis_report.json", mime="application/json", help="Download raw analysis data")

