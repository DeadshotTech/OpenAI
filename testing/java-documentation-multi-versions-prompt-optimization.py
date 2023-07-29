import openai
import spacy
import numpy as np

# Set up your OpenAI API key
openai.api_key = "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"
# Load the SpaCy model for English language
nlp = spacy.load("en_core_web_lg")

# Preprocess the Java documentation to create a context mapping
context_map = {}
# Java version documentations
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
    20: "https://docs.oracle.com/en/java/javase/20/docs/api/",
}

# Topics that have been defined on broad level for the java topics
topic_classifiers = [
    "basics - class, oop, object, oriented, programming, model, variables, model classes",
    "collections - list, set, map, hashmap, array, arraylist, linked list",
    "streams - lambda, lambda expressions, foreach, iterate, filter, collect",
    "records - model classes, data transfer objects",
]

# Create a mapping of release documentation versions to the topics as a configurator
for version, url in versions_urls.items():
    # Here, we manually define the common topics for each version as an example
    if version <= 8:
        context_map[version] = [
            topic_classifiers[0],
            topic_classifiers[1],
            topic_classifiers[2],
        ]
    if version > 8 and version <= 11:
        context_map[version] = [topic_classifiers[0], topic_classifiers[2]]
    if version > 11 and version <= 15:
        context_map[version] = [topic_classifiers[0], topic_classifiers[3]]
    if version > 15:
        context_map[version] = [topic_classifiers[0], topic_classifiers[3]]


# Calculate similarity of question to the topics defined for different versions
def calculate_similarity(topic, question):
    topic_embedding = nlp(topic.lower()).vector
    question_embedding = nlp(question.lower()).vector
    similarity_score = np.dot(topic_embedding, question_embedding) / (
        np.linalg.norm(topic_embedding) * np.linalg.norm(question_embedding)
    )
    # print(f"Similarity score for the topic: {topic} is: {similarity_score}")
    return similarity_score


# Decide and filter out and pick the latest version that are avaialble for each topic
def choose__documentation_versions(question):
    versions_for_topics = {}  # Store the highest version for each topic found

    for version, topics in context_map.items():
        for topic in topics:
            similarity_score = calculate_similarity(topic, question)
            # You can set a threshold for similarity score to determine if a topic is present
            # Here, we use a threshold of 0.5, but you can adjust this based on your data
            if similarity_score > 0.7:
                # print(f"Similarity score for the topic: {topic} is: {similarity_score}")
                if (
                    topic not in versions_for_topics
                    or version > versions_for_topics[topic]
                ):
                    versions_for_topics[topic] = version

    print(f"Versions chosen by 1.0 logic {versions_for_topics}")

    # This actually increase the size of the prompts by adding all the documentation link for all the topics
    # we would want to get evaluatedbut this should be done in house,
    # instead of passing all the information to the prmopt
    # If no topic found, use the latest Java version
    # for topics in context_map.values():
    #     for topic in topics:
    #         if topic not in versions_for_topics:
    #             versions_for_topics[topic] = max(versions_urls.keys())

    # print(f"Versions chosen by 2.0 logic {versions_for_topics}")

    return sorted(set(versions_for_topics.values()), reverse=True)


# Benefits of using Java records for model classes over the classes declared using Java basics
# Construct a dynamic prompt template to be reused
def construct_prompt(versions, question):
    prompt = ""
    for version in versions:
        print(f"Adding documentation to the version: {version}")
        prompt += f"Java Documentation ({version}): {versions_urls[version]}\n"
    prompt += f"Question: {question}\nAnswer:"
    return prompt


# Create the flow for asking the bot questions and getting answers
def ask_bot(question):
    versions = choose__documentation_versions(question)
    print(f"Versions to be chosen from documentation {versions}")
    prompt = construct_prompt(versions, question)
    print(f"Prompt generated for the question: {question} is: '{prompt}'")
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        stop=None,
    )
    answer = response.choices[0].text.strip()
    return answer


# Configure working of the bot
def main():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Answer the user's question using the prompt template
        answer = ask_bot(user_input)
        print("Bot:", answer)


if __name__ == "__main__":
    main()
