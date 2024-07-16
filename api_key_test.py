import requests
import os
from dotenv import load_dotenv


def get_openai_response(prompt):
    load_dotenv()
    API_KEY = os.getenv("OPENAI_KEY")

    if not API_KEY:
        return "API key not provided. Please set the OPENAI_KEY environment variable.", True

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
        response_json = response.json()

        if 'choices' in response_json and 'message' in response_json['choices'][0]:
            return response_json['choices'][0]['message']['content']
        else:
            return "No valid response in 'choices'.", True  # True indicates an error occurred
    except Exception as e:
        return f"An error occurred: {str(e)}", True


if __name__ == "__main__":
    prompt_text = "what is the capital of UK?"
    #prompt_text = input()
    result = get_openai_response(prompt_text)
    print("Response from OpenAI:")
    print(result)
