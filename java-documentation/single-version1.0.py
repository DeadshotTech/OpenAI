import openai

# Set up your OpenAI API key
openai.api_key = "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"

def ask_bot(question, documentation_url):
    prompt = f"Java Documentation: {documentation_url}\nQuestion: {question}\nAnswer:"
    response = openai.Completion.create(
        engine="text-davinci-002",  # Use the appropriate GPT-3 engine here
        prompt=prompt,
        max_tokens=150,  # Adjust the max_tokens as per the response length you want
        stop=None,  # You can add custom stop sequences if needed
    )
    answer = response.choices[0].text.strip()
    return answer

def main():
    # Provide the URL of the Java documentation
    java_documentation_url = "https://docs.oracle.com/en/java/javase/15/docs/api/"

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Answer the user's question based on the Java documentation URL
        answer = ask_bot(user_input, java_documentation_url)
        print("Bot:", answer)

if __name__ == "__main__":
    main()
