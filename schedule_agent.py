import Flask, request, jsonify
import os
import json
import PyPDF2
from langchain_openai import ChatOpenAI

app = Flask(__name__)

# Initialize OpenAI model once
openai_api_key = ###
llm = ChatOpenAI(api_key=openai_api_key)

class SchedulingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = """
        You are an expert scheduling agent. Given the file descriptions below, the user's grade level, and task difficulty, calculate the estimated time required to complete the assignment and create a detailed schedule.
        
        File Descriptions:
        {files_description}
        
        Grade Level: {grade_level}
        Task Difficulty: {task_difficulty}
        
        Please provide a detailed schedule and time estimation.
        """

    def generate_schedule(self, files_description, grade_level, task_difficulty):
        try:
            prompt = self.prompt_template.format(
                files_description=files_description,
                grade_level=grade_level,
                task_difficulty=task_difficulty
            )
            response = self.llm(prompt).content.strip()
            return response
        except Exception as e:
            print(f"Error generating schedule: {e}")
            return ""

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
    return text

@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.json
    files = data.get("files_description", [])
    grade_level = data.get("grade_level", 1)
    task_difficulty = data.get("task_difficulty", 1)

    agent = SchedulingAgent(llm)

    # Process each file and create a description
    files_description = []
    for file_path in files:
        file_text = extract_text_from_pdf(file_path)
        file_description = f"File: {file_path}\nContent Preview: {file_text[:500]}..."  # Preview first 500 chars
        files_description.append(file_description)

    # Generate schedule and time estimation
    schedule = agent.generate_schedule("\n".join(files_description), grade_level, task_difficulty)
    return jsonify({"schedule": schedule})

if __name__ == "__main__":
    app.run()  # Enable debug mode for detailed error logs
