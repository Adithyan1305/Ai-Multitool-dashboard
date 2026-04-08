import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --- THE NEW IMPORTS ---
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper

# 1. INITIALIZE FLASK APP
app = Flask(__name__)

# 2. LOAD ENVIRONMENT
load_dotenv(override=True)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("⚠️ WARNING: GROQ_API_KEY not found in .env file!")

# --- THE NEW LLM: Meta's Llama 3 running on Groq ---
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0
)

# --- ROUTE 1: SERVE THE FRONTEND ---
@app.route('/')
def home():
    return render_template('index.html')

# --- ROUTE 2: WEATHER API ---
@app.route('/api/weather', methods=['POST'])
def get_weather():
    try:
        data = request.get_json() 
        location = data.get('location', '')
        
        url = f"https://wttr.in/{location}?format=3"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        prompt = PromptTemplate.from_template("Turn this raw weather data into a polite, one-sentence forecast: {weather_data}")
        chain = prompt | llm
        result = chain.invoke({"weather_data": response.text})
        
        return jsonify({"result": result.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE 3: MATH API (Simple Quota-Safe Chain) ---
@app.route('/api/math', methods=['POST'])
def get_math():
    try:
        data = request.get_json() 
        query = data.get('query', '')
        
        prompt = PromptTemplate.from_template(
            "You are a highly accurate math calculator. "
            "Solve the following math problem and provide the answer clearly in one sentence.\n\n"
            "Problem: {problem}"
        )
        chain = prompt | llm
        result = chain.invoke({"problem": query})
        
        return jsonify({"result": result.content.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE 4: WORKFLOW API (Research -> Summarize -> Email) ---
@app.route('/api/research', methods=['POST'])
def run_workflow():
    try:
        data = request.get_json() 
        topic = data.get('topic', '')
        
        wiki = WikipediaAPIWrapper()
        raw_research = wiki.run(topic)
        
        summary_prompt = PromptTemplate.from_template(
            "Extract 3 concise bullet points from this research:\n\n{research}"
        )
        summary_chain = summary_prompt | llm
        summary_result = summary_chain.invoke({"research": raw_research[:4000]}) 
        summary_text = summary_result.content
        
        email_prompt = PromptTemplate.from_template(
            "Write a short, professional email to my team sharing these research bullet points. Include a subject line.\n\n{summary}"
        )
        email_chain = email_prompt | llm
        email_result = email_chain.invoke({"summary": summary_text})
        
        return jsonify({
            "summary": summary_text,
            "email": email_result.content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)