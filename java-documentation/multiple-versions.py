import openai

# Set up your OpenAI API key
openai.api_key = "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"


def ask_bot(question, versions_urls):
    sorted_versions = sorted(
        versions_urls.keys(), reverse=True
    )  # Sort versions in reverse order
    prompt = ""
    for version in sorted_versions:
        url = versions_urls[version]
        prompt += f"Java Documentation ({version}): {url}\n"

    prompt += f"Question: {question}\nAnswer:"

    response = openai.Completion.create(
        engine="text-davinci-002",  # Use the appropriate GPT-3 engine here
        prompt=prompt,
        max_tokens=150,  # Adjust the max_tokens as per the response length you want
        stop=None,  # You can add custom stop sequences if needed
    )
    answer = response.choices[0].text.strip()
    return answer


def main():
    # Provide the URLs of the Java documentation for different versions
    versions_urls = {
        7: "https://docs.oracle.com/javase/7/docs/",
        8: "https://docs.oracle.com/javase/8/docs/api/",
        9: "https://docs.oracle.com/javase/9/docs/api/",
        10: "https://docs.oracle.com/javase/10/docs/api/",
        11: "https://docs.oracle.com/en/java/javase/11/docs/api/",
        12: "https://docs.oracle.com/en/java/javase/12/docs/api/",
        13: "https://docs.oracle.com/en/java/javase/13/docs/api/",
        14: "https://docs.oracle.com/en/java/javase/14/docs/api/",
        15: "https://docs.oracle.com/en/java/javase/15/docs/api/",
        16: "https://docs.oracle.com/en/java/javase/16/docs/api/",
        17: "https://docs.oracle.com/en/java/javase/17/docs/api/",
        18: "https://docs.oracle.com/en/java/javase/18/docs/api/",
        19: "https://docs.oracle.com/en/java/javase/19/docs/api/",
        20: "https://docs.oracle.com/en/java/javase/20/docs/api/"
        # Add more versions and URLs as needed
    }

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Answer the user's question based on the multiple Java documentation URLs
        answer = ask_bot(user_input, versions_urls)
        print("Bot:", answer)


if __name__ == "__main__":
    main()
