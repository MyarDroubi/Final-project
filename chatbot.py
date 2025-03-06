import requests

API_URL = "https://api-inference.huggingface.co/models/gpt2"  # GPT-2 model from Hugging Face
API_KEY = "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"  # Replace this with your API key
headers = {"Authorization": f"Bearer {API_KEY}"}

def ask_question(question):
    payload = {"inputs": question}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        try:
            return result[0]["generated_text"]
        except:
            return "Sorry, I couldn't understand the response."
    else:
        return f"Error: {response.status_code}, {response.text}"

print("Welcome to the Chatbot! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    answer = ask_question(user_input)
    print("Chatbot:", answer)
