# Import necessary libraries
import streamlit as st
import re
import nltk
import os
from nltk.corpus import stopwords
from nltk import FreqDist
from graphviz import Digraph

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

def remove_timestamps(text):
    return re.sub(r'\d{1,2}:\d{2}\n.*\n', '', text)

def extract_high_information_words(text, top_n=10):
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    freq_dist = FreqDist(filtered_words)
    return [word for word, _ in freq_dist.most_common(top_n)]

def create_relationship_graph(words):
    graph = Digraph()
    for index, word in enumerate(words):
        graph.node(str(index), word)
        if index > 0:
            graph.edge(str(index - 1), str(index), label=str(index))
    return graph

def display_relationship_graph(words):
    graph = create_relationship_graph(words)
    st.graphviz_chart(graph)

def extract_context_words(text, high_information_words):
    words = nltk.word_tokenize(text)
    context_words = []
    for index, word in enumerate(words):
        if word.lower() in high_information_words:
            before_word = words[index - 1] if index > 0 else None
            after_word = words[index + 1] if index < len(words) - 1 else None
            context_words.append((before_word, word, after_word))
    return context_words

def create_context_graph(context_words):
    graph = Digraph()
    for index, (before_word, high_info_word, after_word) in enumerate(context_words):
        graph.node(f'before{index}', before_word, shape='box') if before_word else None
        graph.node(f'high{index}', high_info_word, shape='ellipse')
        graph.node(f'after{index}', after_word, shape='diamond') if after_word else None
        if before_word:
            graph.edge(f'before{index}', f'high{index}')
        if after_word:
            graph.edge(f'high{index}', f'after{index}')
    return graph

def display_context_graph(context_words):
    graph = create_context_graph(context_words)
    st.graphviz_chart(graph)

def display_context_table(context_words):
    table = "| Before | High Info Word | After |\n|--------|----------------|-------|\n"
    for before, high, after in context_words:
        table += f"| {before if before else ''} | {high} | {after if after else ''} |\n"
    st.markdown(table)

# Load example files
def load_example_files():
    example_files = [f for f in os.listdir() if f.endswith('.txt')]
    selected_file = st.selectbox("📄 Select an example file:", example_files)
    if st.button(f"📂 Load {selected_file}"):
        with open(selected_file, 'r', encoding="utf-8") as file:
            return file.read()
    return None

# Main code for UI
uploaded_file = st.file_uploader("📁 Choose a .txt file", type=['txt'])

example_text = load_example_files()

if example_text:
    file_text = example_text
elif uploaded_file:
    file_text = uploaded_file.read().decode("utf-8")
else:
    file_text = ""

if file_text:
    text_without_timestamps = remove_timestamps(file_text)
    top_words = extract_high_information_words(text_without_timestamps, 10)

    with st.expander("📊 Top 10 High Information Words"):
        st.write(top_words)

    with st.expander("📈 Relationship Graph"):
        display_relationship_graph(top_words)

    context_words = extract_context_words(text_without_timestamps, top_words)

    with st.expander("🔗 Context Graph"):
        display_context_graph(context_words)

    with st.expander("📑 Context Table"):
        display_context_table(context_words)