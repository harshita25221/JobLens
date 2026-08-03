import streamlit as st
import docx
import spacy 
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from keybert import KeyBERT
from io import BytesIO
from spacy.lang.en.stop_words import STOP_WORDS
import pandas as pd
from rapidfuzz import process, fuzz
import openai
import os

# Set page configuration
st.set_page_config(page_title="JobLens", page_icon="🚀", layout="wide")

# Load models and data (cached to prevent reloading on every interaction)
@st.cache_resource
def load_models():
    nlp = spacy.load("en_core_web_sm")
    kw_model = KeyBERT()
    skills_df = pd.read_csv("merged_skills.csv")
    global_skills = set(skills_df["skill"].dropna().str.lower().str.strip())
    return nlp, kw_model, global_skills

with st.spinner("Loading AI Models..."):
    nlp, kw_model, GLOBAL_SKILLS = load_models()

openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------- ML Functions -----------------
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    text = ""
    file_content = BytesIO(file.read())
    with pdfplumber.open(file_content) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "")+"\n"
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+"," ", text)
    return text

def get_keywords(text, num_keywords=20):
    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1, 3), 
        stop_words='english',
        top_n=num_keywords
    )
    return [kw[0] for kw in keywords]

def extract_spacy_skills(text):
    doc = nlp(text)
    skills = set()
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
            word = token.text.strip()
            if word.lower() not in STOP_WORDS:
                if word[0].isupper() or re.search(r"[A-Za-z0-9\+\#]", word):
                    skills.add(word)
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE']:
            skills.add(ent.text.lower())        
    return list(skills)

def normalize_skills_with_fuzzy(extracted_skills, global_skills, threshold=85):
    normalized = set()
    for skill in extracted_skills:
        match = process.extractOne(skill, global_skills, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:  
            normalized.add(match[0])  
    return normalized

def extract_multiword_skills(text, global_skills):
    found = set()
    for skill in global_skills:
        if " " in skill and skill in text.lower():
            found.add(skill)
    return found

def get_combined_skills(text):
    kw_skills = set(get_keywords(text))
    spacy_skills = set(extract_spacy_skills(text))
    multiword_skills = extract_multiword_skills(text, GLOBAL_SKILLS)
    all_extracted = {s.lower().strip() for s in kw_skills.union(spacy_skills, multiword_skills)}
    filtered = normalize_skills_with_fuzzy(all_extracted, GLOBAL_SKILLS)
    return filtered

def get_skills_and_score(resume_text, job_description, alpha=0.3):
    resume_skills = set(get_combined_skills(resume_text))
    job_req_skills = set(get_combined_skills(job_description))

    resume_skills = {s for s in resume_skills if s not in STOP_WORDS and len(s) > 2}
    job_req_skills = {s for s in job_req_skills if s not in STOP_WORDS and len(s) > 2}

    if not resume_skills or not job_req_skills:
        return 0.0, [], [], 0.0

    overlap = len(resume_skills & job_req_skills) / len(job_req_skills)

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(
        [" ".join(resume_skills), " ".join(job_req_skills)]
    )
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    final_score = (alpha * cosine_sim + (1 - alpha) * overlap) * 100

    missing_skills = sorted(list(job_req_skills - resume_skills))
    highlighted_skills = sorted(list(job_req_skills & resume_skills))

    return final_score, missing_skills, highlighted_skills, cosine_sim

def generate_ai_text(prompt: str) -> str:
    if not openai.api_key:
        return "⚠️ OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are an AI-powered career coach that analyzes resumes and job descriptions, rewrites resumes for better alignment, crafts tailored cover letters, and provides suggestions to maximize a candidate's chances of getting hired."},
                {"role": "user", "content": prompt}
            ], 
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating text: {str(e)}"

def generate_tailored_resume(resume_text, job_description):
    prompt = f"""
    Resume: \n{resume_text}\n
    Job description: \n{job_description}\n
    Rewrite the resume so it better matches the job description.
    Focus on aligning skills, experience, and phrasing with the job description while keeping authenticity.
    """
    return generate_ai_text(prompt)

def generate_cover_letter(resume_text, job_description):
    prompt = f"""
    Write a professional cover letter tailored to the following job description: \n{job_description}\n
    Resume content: \n{resume_text}\n
    Make it concise, skill-focused, and role-specific."""
    return generate_ai_text(prompt)

def generate_suggestions(resume_text, job_description, cosine_sim, missing_skills):
    prompt = f"""
    You are an expert career coach. 
    A candidate has a resume and is applying for this job description.
    Their resume-Job description match score is {round(cosine_sim*100,2)}%
    Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

    Provide a numbered list of 3-5 clear, practical suggestions.
    Each suggestion must be on a new line.
    """
    response_text = generate_ai_text(prompt)
    if response_text.startswith("⚠️") or response_text.startswith("Error"):
        return [response_text]
        
    suggestions_list = [
        re.sub(r'^\d+\.\s*', '', line).strip() 
        for line in response_text.split('\n') 
        if line.strip()
    ]
    return suggestions_list

# ----------------- UI -----------------
st.title("🚀 JobLens")
st.markdown("### AI-Powered Resume Analyzer")
st.markdown("Upload your resume and the job description to get a tailored analysis, cover letter, and resume rewrite.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Resume")
    resume_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"], key="resume")

with col2:
    st.subheader("💼 Upload Job Description")
    jd_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"], key="jd")

if st.button("Analyze Resume", type="primary"):
    if not resume_file or not jd_file:
        st.warning("Please upload both a resume and a job description.")
    else:
        with st.spinner("Analyzing and generating insights (this may take a minute)..."):
            # Extract text
            if resume_file.name.endswith(".docx"):
                resume_raw = extract_text_from_docx(resume_file)
            else:
                resume_raw = extract_text_from_pdf(resume_file)
                
            if jd_file.name.endswith(".docx"):
                jd_raw = extract_text_from_docx(jd_file)
            else:
                jd_raw = extract_text_from_pdf(jd_file)
                
            resume_clean = clean_text(resume_raw)
            jd_clean = clean_text(jd_raw)

            # Analyze
            final_score, missing_skills, highlighted_skills, cosine_sim = get_skills_and_score(resume_clean, jd_clean)
            
            # Generate OpenAI content
            tailored_resume = generate_tailored_resume(resume_clean, jd_clean)
            cover_letter = generate_cover_letter(resume_clean, jd_clean)
            suggestions = generate_suggestions(resume_clean, jd_clean, cosine_sim, missing_skills)

        # Display Results
        st.divider()
        st.header("📊 Analysis Results")
        
        score_col, empty_col = st.columns([1, 2])
        with score_col:
            st.metric(label="Match Score", value=f"{round(final_score, 1)}%")
            st.progress(min(final_score / 100.0, 1.0))

        st.subheader("🎯 Skills Analysis")
        skill_col1, skill_col2 = st.columns(2)
        
        with skill_col1:
            st.markdown("**✅ Highlighted Skills**")
            if highlighted_skills:
                for skill in highlighted_skills:
                    st.markdown(f"- {skill.title()}")
            else:
                st.write("None found.")
                
        with skill_col2:
            st.markdown("**⚠️ Missing Skills**")
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"- {skill.title()}")
            else:
                st.write("None missing!")

        st.divider()
        
        tab1, tab2, tab3 = st.tabs(["📝 Tailored Resume", "✉️ Cover Letter", "💡 Suggestions"])
        
        with tab1:
            st.markdown(tailored_resume)
            
        with tab2:
            st.markdown(cover_letter)
            
        with tab3:
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"{i}. {suggestion}")
