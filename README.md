🚀 JobLens: AI-Powered Resume Analyzer



Welcome to JobLens, an intelligent and visually stunning web application designed to help job seekers optimize their resumes for any job description. By leveraging advanced Natural Language Processing (NLP) and cutting-edge Generative AI, JobLens provides deep insights, actionable feedback, and automated tailoring to maximize your chances of landing an interview.

---

🔗 Live Website
Experience the live application here: [https://joblens-1-uim8.onrender.com](https://joblens-1-uim8.onrender.com]

---

✨ Key Features

* 🔍 Smart Skill Extraction: Utilizes SpaCy, YAKE, and RapidFuzz to precisely extract and normalize skills from both resumes and job descriptions.
* 📊 Match Scoring algorithm: Calculates a dynamic compatibility score using TF-IDF and Cosine Similarity, providing a realistic assessment of your fit.
* 🎯 Tailored AI Suggestions: Powered by the highly reliable **Groq API**, JobLens gives you 3-5 personalized, actionable steps to improve your resume instantly.
* 📝 Automated Cover Letter Generation: Instantly drafts a professional, role-specific cover letter using the alignment between your resume and the job description.
* 📄 Automated Resume Rewriting: Generates an optimized, highly-tailored version of your resume content that seamlessly aligns with the target role.
* 🎨 Premium UI/UX: Built with React, Tailwind CSS, Framer Motion, and modern glassmorphic design principles to provide an immersive, fluid user experience.

---

🛠️ Technology Stack

 Frontend
-React 18 (Vite)
-TypeScript
-Tailwind CSS
-Framer Motion (Micro-animations)
-Lucide React (Icons)
-Recharts (Data Visualization)

 Backend
  -Python 3.10+ (Flask)
  -SpaCy & YAKE (NLP Skill Extraction)
  -Scikit-Learn (TF-IDF & Cosine Similarity)
  -RapidFuzz (Fuzzy String Matching)
  -Groq API (Llama-3.1 for Generative AI Text)
  -PDFPlumber & Python-Docx (Document Parsing)

---

 🚀 How to Run Locally

If you'd like to run JobLens on your local machine, follow these steps:

 1. Clone the Repository
```bash
git clone https://github.com/harshita25221/JobLens.git
cd JobLens
```

 2. Set up the Backend
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt

# Add your Groq API Key
# Create a .env file or export it directly
export GROQ_API_KEY="your_groq_api_key_here"

# Run the Flask API
python backend/app.py
```




