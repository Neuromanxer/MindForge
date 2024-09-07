from flask import Flask, request, jsonify, render_template_string
import os
import time
from openai import OpenAI
from tavily import TavilyClient
import json

app = Flask(__name__)

client = OpenAI(api_key=os.get(OPEN_AI_KEY))
tavily_client = TavilyClient(api_key="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")

assistant_prompt_instruction = """You are an educational expert.
Your goal is to determine the best studying strategy for a user based on their personality type by asking a series of questions.
You must determine the rate the user enjoys working at: going little by little everyday, doing it all last minute, etc.
You should analyze the user's responses to these questions and suggest a suitable study strategy. 
You must use the provided Tavily search API function to find relevant online information. 
Include relevant URL sources at the end of your answers.
"""

def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result

def create_assistant():
    return client.beta.assistants.create(
        instructions=assistant_prompt_instruction,
        model="gpt-4-1106-preview",
        tools=[{
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": "Get information on study strategies from the web.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query to use."},
                    },
                    "required": ["query"]
                }
            }
        }]
    )

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool.id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

# Mock TestQuestionGeneratorAgent class
class TestQuestionGeneratorAgent:
    def generate_test_questions(self, material, past_questions):
        # Mock implementation
        return ["Sample question 1", "Sample question 2"]

@app.route('/generate_test_questions', methods=['POST'])
def generate_test_questions():
    app.logger.info(f"Received POST request for /generate_test_questions")
    data = request.json
    material = data.get('material', '')
    past_questions = data.get('past_questions', [])

    # Create and use TestQuestionGeneratorAgent instance
    agent = TestQuestionGeneratorAgent()
    new_questions = agent.generate_test_questions(material, past_questions)

    return jsonify({'questions': new_questions})

@app.route('/ask', methods=['POST'])
def ask():
    app.logger.info(f"Received POST request for /ask")
    user_input = request.form.get('input', '')

    # Create a message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    # Wait for run to complete
    run = wait_for_run_completion(thread.id, run.id)

    if run.status == 'failed':
        return jsonify({"error": run.error}), 500
    elif run.status == 'requires_action':
        run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
        run = wait_for_run_completion(thread.id, run.id)

    # Get messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response_messages = [{"role": msg.role, "content": msg.content[0].text.value} for msg in messages]

    # Render response in HTML
    response_html = "\n".join([f"{msg['role']}: {msg['content']}" for msg in response_messages])
    return render_template_string('''
        <form action="/ask" method="post">
            <label for="user_input">Please ask the agent to determine your study strategy:</label>
            <input type="text" id="user_input" name="input">
            <input type="submit" value="Submit">
        </form>
        <div id="response">
            <h3>Response from Chatbot:</h3>
            <pre>{{ response }}</pre>
        </div>
    ''', response=response_html)

if __name__ == '__main__':
    assistant = create_assistant()
    assistant_id = assistant.id
    thread = client.beta.threads.create()
    app.run(port=5000, debug=True)
