import re
import os
import streamlit as st
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import io
import plotly.graph_objs as go


# Load environment variables
load_dotenv()

# Configure API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key not found. Please set GOOGLE_API_KEY in your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

def gen_response(text):
    """Generate response using Gemini model"""
    response = model.generate_content(text)
    return response.text

def pdfreader(uploaded_file):
    """Read PDF file and extract text"""
    try:
        # Convert Streamlit's UploadedFile to a file-like object
        pdf_file = io.BytesIO(uploaded_file.getvalue())
        
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages])
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""
    
def extract_match_percentage(analysis):
    """Extract match percentage from analysis text"""
    match = re.search(r'(\d+)%', analysis)
    return int(match.group(1)) if match else 0    

def create_circular_gauge(match_score):
    """Create a circular gauge plot for match score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = match_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': 'Resume Match Score', 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"},
            'steps' : [
                {'range': [0, 50], 'color': "lightcoral"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "lightgreen"}
            ],
            'threshold' : {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': match_score
            }
        }
    ))

    fig.update_layout(height=400, margin=dict(l=50, r=50, t=0, b=0))
    return fig

def final_prompt(text, jd):

    prompt = f""" As an experienced ATS (Applicant Tracking System), 
    proficient in the technical domain encompassing Software Engineering, Data Science, 
    Data Analysis, Big Data Engineering, Web Developer, Mobile App Developer, DevOps 
    Engineer, Machine Learning Engineer, Cybersecurity Analyst, Cloud Solutions Architect, Database Administrator,
    Network Engineer, AI Engineer, Systems Analyst, Full Stack Developer, UI/UX Designer, IT Project Manager, and additional 
    specialized areas, your objective is to meticulously assess resumes against provided job descriptions. In a fiercely competitive
    job market, your expertise is crucial in offering top-notch guidance for resume enhancement. Assign precise matching percentages 
    based on the JD (Job Description) and meticulously identify any missing keywords with utmost accuracy. 
    resume: {text}
    description: {jd}
    I want the response in the following structure: 
    The first line indicates the percentage match with the job description (JD). 
    The second line presents a list of missing keywords.
    The third section provides a profile summary. 

    Mention the title for all the three sections. While generating the response put some space to separate all the three sections.
    """
    
    return prompt

def main():
    st.title("Advanced ATS Resume Checker : Best in the Buisness")
    
    # Job Description Input
    st.subheader("Job Description (JD)")
    jd = st.text_input("Enter your job description")
    
    # File Upload with Validation
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
    
    # Analysis Button
    if st.button("Analyze Resume"):
        if not uploaded_file:
            st.warning("Please upload a PDF resume.")
            return
        
        if not jd:
            st.warning("Please enter a job description.")
            return
        
        # Extract text from PDF
        resume_text = pdfreader(uploaded_file)
        
        if not resume_text:
            st.error("Could not extract text from the PDF. Please check the file.")
            return
        
        # Generate prompt and get response
        try:
            prompt = final_prompt(resume_text, jd)
            analysis = gen_response(prompt)
            st.success("Resume Analysis Complete")

            match_score = extract_match_percentage(analysis)
            
            # Create circular gauge
            fig = create_circular_gauge(match_score)
            st.plotly_chart(fig, use_container_width=True)

            st.write(analysis)
        
        except Exception as e:
            st.error(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
