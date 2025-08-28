#!/usr/bin/env uv run

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "crewai",
#     "crewai-tools",
#     "python-dotenv",
#     "youtube-transcript-api",
# ]
# ///

from youtube_transcript_api import YouTubeTranscriptApi
from crewai.tools import BaseTool
from crewai import Agent, LLM, Task, Crew, Process
import os
import re
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

# Use Gemini 2.5 Pro Experimental model
gemini_llm = LLM(
    model='gemini/gemini-2.0-flash',
    api_key=gemini_api_key,
    provider='google',
    temperature=0.1  # Lower temperature for more consistent results.
)


class fetchYoutubeTranscript(BaseTool):
    name: str = "Fetch YouTube Transcript"
    description: str = "Fetches the transcript of a youtube video using the provided link"

    def _run(self, link: str) -> str:
        video_id = re.search(r'(?:v=|/shorts/|youtu\.be/)([A-Za-z0-9_-]{6,})', link)
        if not video_id:
            raise ValueError("Could not parse YouTube video id from URL")
        video_id = video_id.group(1)

        ytt_api = YouTubeTranscriptApi()
        transcript_raw = ytt_api.fetch(video_id)

        transcript_clean = ""

        for snippet in transcript_raw:
            transcript_clean += snippet.text.replace("\n", " ") + " "

        return transcript_clean


fetch_youtube_transcript = fetchYoutubeTranscript()


# 1. Content Planner
content_planner = Agent(
    role="Content Planner",
    goal="Create a clear outline of the YouTube video transcript with relevant headings and subheadings.",
    backstory=(
        "You are an expert content strategist who specializes in extracting "
        "the structure and key talking points from transcripts to make them "
        "easy to digest as outlines."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 2. Video Summarizer
video_summarizer = Agent(
    role="YouTube Video Summarizer",
    goal="Summarize the YouTube transcript into a clear, structured summary with required headings and subheadings.",
    backstory=(
        "You specialize in condensing long YouTube transcripts into readable "
        "summaries. You emphasize clarity, brevity, and proper formatting."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[fetch_youtube_transcript],
    llm=gemini_llm  # <-- your configured Gemini LLM
)

# 3. Editor (Fact Checker)
editor = Agent(
    role="Editor & Fact Checker",
    goal=(
        "Proofread and fact-check the final summary against the transcript. "
        "Ensure grammar, spelling, and structure are correct, and validate "
        "that all key points in the transcript are accurately represented."
    ),
    backstory=(
        "You are a meticulous editor with a keen eye for detail. "
        "You check not only for readability but also for accuracy, ensuring "
        "the summary faithfully reflects the transcript."
    ),
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)


# 1. Fetch Transcript
fetch_transcript_task = Task(
    description=(
        "Fetch the transcript for the provided YouTube video link: {youtube_link}. "
        "Return only the raw transcript text."
    ),
    expected_output="The complete transcript text of the YouTube video.",
    agent=video_summarizer,
    tools=[fetch_youtube_transcript],
)

# 2. Content Outline
content_planner_task = Task(
    description=(
        "Using the transcript, create an outline of the video. "
        "The outline must contain clear headings and subheadings "
        "that represent the main topics and sections of the transcript."
    ),
    expected_output="An organized outline with relevant headings and subheadings.",
    agent=content_planner,
)

# 3. Summarization
summarization_task = Task(
    description=(
        "Using the transcript, write a structured summary of the YouTube video. "
        "Include headings and subheadings as appropriate, and keep it concise "
        "while preserving key details. Make sure to markdown the output"
    ),
    expected_output="A clear, structured summary of the transcript.",
    agent=video_summarizer,
)

# 4. Editing & Fact Checking
editing_task = Task(
    description=(
        "Proofread and fact-check the structured summary against the transcript. "
        "Ensure grammar, spelling, and readability are excellent. "
        "Verify that all important points in the transcript are covered accurately. "
        "Your final answer MUST be the polished, fact-checked summary."
    ),
    expected_output="A polished and fact-checked final summary.",
    agent=editor,
)


crew = Crew(
    agents=[content_planner, video_summarizer, editor],
    tasks=[fetch_transcript_task, content_planner_task, summarization_task, editing_task],
    process=Process.sequential,
)


if __name__ == '__main__':
    url = input()
    result = crew.kickoff(inputs={'youtube_link': url})

    with open("youtube_summary.md", "w", encoding="utf-8") as f:
        f.write(result.raw)