# Legalis - Contract Analysis & Risk Assessment Bot

Legal contract analyst bot designed for Indian SMEs. Built for the GUVI Hackathon.

## Features
- **Upload & Analyze**: Supports PDF, DOCX, TXT.
- **AI-Powered Risk Assessment**: Identifies high-risk clauses (Penalties, Indemnity, etc.).
- **Plain English Summaries**: Explanations for complex legal jargon.
- **Clause Scoring**: 0-10 risk score for every clause.
- **Templates**: Generate standard contract templates.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure API Key**
   - Open `config.py` and set your `ANTHROPIC_API_KEY`.
   - OR run the app and enter the key in the sidebar.

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

## Project Structure
- `app.py`: Main Streamlit application.
- `contract_analyzer.py`: Integrates with Claude API.
- `risk_scorer.py`: Logic for risk scoring.
- `utils.py`: Helper functions for file reading and NLP.
- `templates/`: Sample contracts.

## Key Technologies
- **Frontend**: Streamlit
- **LLM**: Anthropic Claude API
- **NLP**: spaCy

## Contact
Team Antigravity
