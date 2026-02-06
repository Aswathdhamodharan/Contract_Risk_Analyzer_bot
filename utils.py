import io
import re
import PyPDF2
import docx
import spacy
from typing import Tuple
import pandas as pd
import streamlit as st

# Load spaCy model
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Download if not present (although usually should be pre-installed)
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_nlp()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text(file_obj) -> str:
    """Dispatcher for text extraction based on file type."""
    if file_obj.name.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_obj.getvalue())
    elif file_obj.name.lower().endswith('.docx'):
        return extract_text_from_docx(file_obj.getvalue())
    elif file_obj.name.lower().endswith('.txt'):
        return file_obj.getvalue().decode("utf-8")
    else:
        return "Unsupported file format."

def detect_language(text: str) -> str:
    """Simple heuristic to detect Hindi content."""
    # Check for Devanagari script range
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = len(text)
    if total_chars == 0:
        return "English"
    
    ratio = hindi_chars / total_chars
    if ratio > 0.05: # Threshold for considering it Hindi
        return "Hindi"
    return "English"

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_entities_spacy(text: str):
    """Fallback entity extraction using spaCy if Claude fails or for augmentation."""
    doc = nlp(text[:100000]) # Limit to avoid memory issues
    entities = {
        "dates": [],
        "orgs": [],
        "money": [],
        "gpe": [] # Geo-political entities (jurisdicton usually)
    }
    
    for ent in doc.ents:
        if ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["orgs"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text)
        elif ent.label_ == "GPE":
            entities["gpe"].append(ent.text)
            
    # Deduplicate
    for key in entities:
        entities[key] = list(set(entities[key]))
        
    return entities
