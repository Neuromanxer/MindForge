from flask import Flask, request, jsonify, render_template_string
import json
import time
from openai import OpenAI
from tavily import TavilyClient

app = Flask(__name__)

client = OpenAI(api_key=os.get("OPENAI_KEY"))
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

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

def print_messages_from_thread(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages:
        print(f"{msg.role}: {msg.content[0].text.value}")

assistant = client.beta.assistants.create(
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
                    "query": {"type": "string", "description": "The search query to use. For example: 'Effective study techniques for visual learners'"},
                },
                "required": ["query"]
            }
        }
    }]
)
assistant_id = assistant.id
print(f"Assistant ID: {assistant_id}")

thread = client.beta.threads.create()
print(f"Thread: {thread}")

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
        <form action="/ask" method="post">
            <label for="user_input">Please ask the agent to determine your study strategy:</label>
            <input type="text" id="user_input" name="input">
            <input type="submit" value="Submit">
        </form>
        <div id="response">
            {% if response %}
                <h3>Response from Chatbot:</h3>
                <pre>{{ response }}</pre>
            {% endif %}
        </div>
    ''')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form.get('input', '')
    print(f"User Input: {user_input}")

    #create a message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    #create a run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    print(f"Run ID: {run.id}")

    #wait for run to complete
    run = wait_for_run_completion(thread.id, run.id)

    if run.status == 'failed':
        print(f"Run failed with error: {run.error}")
        return jsonify({"error": run.error}), 500
    elif run.status == 'requires_action':
        run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
        run = wait_for_run_completion(thread.id, run.id)

    #get messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response_messages = [{"role": msg.role, "content": msg.content[0].text.value} for msg in messages]
    
    #print the response to the console
    print("Response Messages:")
    for message in response_messages:
        print(f"{message['role']}: {message['content']}")

    #render response in HTML
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
    app.run(port=5000, debug=True)  # Enable debug mode for detailed error logs
