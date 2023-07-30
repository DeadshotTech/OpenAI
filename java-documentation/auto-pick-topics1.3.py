import openai
import spacy
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os
import json

# Set up your OpenAI API key
openai.api_key = "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"
# Load the SpaCy model for English language
# nlp = spacy.load("en_core_web_lg")
# model_directory = "path/to/model_directory"
# nlp = spacy.load(model_directory)

# Preprocess the Java documentation to create a context mapping
context_map = {}
# Java version documentations
versions_urls = {
    7: "https://docs.oracle.com/javase/7/docs/technotes/guides/language/enhancements.html#javase7",
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


def extract_topics_from_url(url):
    print(f"Started extraction of topics for the url: {url}")

    # Check if the topics have already been extracted and saved in the file
    topics_file = "topics.json"
    # Initialize topics_data as an empty dictionary
    topics_data = {}
    if os.path.exists(topics_file):
        with open(topics_file, "r") as file:
            topics_data = json.load(file)
            if url in topics_data:
                print(f"Using cached topics for the url: {url}")
                return topics_data[url]

    # Create the Edge webdriver
    edge_options = webdriver.EdgeOptions()
    # Add any desired options to the edge_options if needed
    edge_options.add_argument("--headless")

    driver = webdriver.Edge(options=edge_options)

    # Fetch the content of the URL
    driver.get(url)

    # Switch to the frame containing the desired content, if present
    try:
        frame_element = driver.find_element(
            "tag name", "frame"
        )  # Or use "iframe" if applicable
        driver.switch_to.frame(frame_element)
    except NoSuchElementException:
        # If no frame is found, the content is not restricted within a frame
        pass

    # Get the page source after switching to the frame (if applicable)
    content = driver.page_source

    # Switch back to the default content if we switched to a frame
    if "frame_element" in locals():
        driver.switch_to.default_content()

    # Close the Selenium browser
    driver.quit()

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(content, "html.parser")
    # Extract potential topics from headings, subheadings, or other relevant tags
    topics = [
        heading.text.strip()
        for heading in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "a"]
        )
    ]

    # Save the topics to the file
    topics_data[url] = topics
    with open(topics_file, "w") as file:
        json.dump(topics_data, file, indent=4)

    return topics


# def extract_topics_from_url(url):
#     print(f"Started extraction of topics for the url: {url}")
#     # Fetch the content of the URL
#     response = requests.get(url)
#     if response.status_code == 200:
#         content = response.text
#         # Use BeautifulSoup to parse the HTML content
#         soup = BeautifulSoup(content, "html.parser")
#         # Extract potential topics from headings, subheadings, or other relevant tags
#         topics = [
#             heading.text.strip()
#             for heading in soup.find_all(
#                 ["h1", "h2", "h3", "h4", "h5", "h6", "li", ]
#             )
#         ]
#         return topics
#     else:
#         return []


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

    topicsExtractedFromDocumentation = extract_topics_from_url(url)
    print(
        f"Tpoics extracted from version {version} are: {topicsExtractedFromDocumentation}"
    )


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
            # similarity_score = calculate_similarity(topic, question)
            # You can set a threshold for similarity score to determine if a topic is present
            # Here, we use a threshold of 0.5, but you can adjust this based on your data
            # if similarity_score > 0.7:
            # print(f"Similarity score for the topic: {topic} is: {similarity_score}")
            if topic not in versions_for_topics or version > versions_for_topics[topic]:
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
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=prompt,
    #     max_tokens=150,
    #     stop=None,
    # )
    # answer = response.choices[0].text.strip()
    # return answer


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
