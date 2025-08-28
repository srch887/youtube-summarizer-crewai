# YouTube Video Summarization Pipeline with CrewAI

This project uses **CrewAI** to orchestrate multiple AI agents that work together to:

- Fetch a transcript from a YouTube video  
- Plan an outline (headings & subheadings)  
- Summarize the transcript into a structured format  
- Edit & Fact-Check the final summary against the transcript  

The pipeline runs sequentially, ensuring **clean, accurate, and well-structured video summaries**.

---

## Project Structure
```bash
youtube_summary.py # Main script
app.py # FastAPI server
.env # Environment variables (YouTube link, API keys)
README.md # Documentation
```


---

## Features

- **Custom Tool** for fetching YouTube transcripts  
- **Content Planner Agent** → Creates structured outline  
- **Summarizer Agent** → Writes structured summaries with headers  
- **Editor Agent** → Proofreads + fact-checks summary against transcript  
- **Sequential CrewAI Workflow** → Agents execute in order  
- **FastAPI Integration** → REST API built with **FastAPI** for simple endpoints, async support, and deployment convenience  
- **Powered by Gemini** → Uses **Google’s `gemini-2.0-flash` LLM** for reasoning, summarization, and editing

---

## Agents

### 1. **Content Planner**
- **Role:** Extracts structure & main points from the transcript  
- **Output:** Outline with headings and subheadings  

### 2. **Video Summarizer**
- **Role:** Condenses transcript into a structured summary  
- **Output:** Clear, readable summary with logical formatting  

### 3. **Editor & Fact Checker**
- **Role:** Proofreads, checks grammar/style, and validates summary against transcript  
- **Output:** Polished, accurate, fact-checked summary  

---

##  Tasks

1. **Fetch Transcript Task** → Gets transcript text via custom tool  
2. **Content Planner Task** → Creates structured outline  
3. **Summarization Task** → Generates structured summary  
4. **Editing Task** → Proofreads + fact-checks final summary  

---

## Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
### 2. Set Environment Variables

Create a .env file:
```bash
GEMINI_API_KEY="your_api_key_here"
```
### 3. Run the local server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 
```
### 4. Hit the API on an HTTP client
```
curl -X POST "https://youtube-summarizer-crewai.onrender.com/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_link": "https://www.youtube.com/watch?v=XB4MIexjvY0"
  }'
```
