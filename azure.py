import streamlit as st
import os
import pandas as pd
from io import StringIO
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate

# Function Definitions

def initialize_conversation_chain():
    template = templates[selected_template]
    system_message = SystemMessagePromptTemplate.from_template(template=template)
    prompt_template = PromptTemplate(
        input_variables=['history', 'input', 'number'], 
        template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:'
    )

    return ConversationChain(
        llm=chat,
        prompt=prompt_template,
        verbose=False,
        memory=memory,
    )

def read_uploaded_file(uploaded_file):
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file), ""
        elif uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file), ""
        else:
            return None, StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    return None, ""

def update_conversation_history(user_input, string_data, df):
    if string_data and string_data is not "":
        st.session_state.conversation_history.append(f"File Content: {string_data}")

    if df is not None:
        st.session_state.conversation_history.append(f"File Content: {df}")

    if user_input:
        st.session_state.conversation_history.append(f"Human: {user_input}")

def generate_ai_response(user_input, number):
    conversation_input = {
        "history": "\n".join(st.session_state.conversation_history),
        "input": user_input,
        "number": number
    }

    response = conversation.predict(conversation_input)
    st.session_state.conversation_history.append(f"AI: {response}")
    return response

# Main Application

#pull openAI key from Azure config
openai_api_key=os.environ['OPENAI_API_KEY']

#App Name
st.title('Accounting Assistant')

# Initialize the chat model and memory
chat = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4-1106-preview")
memory = ConversationBufferMemory()

# Initialize session state for conversation history if it doesn't already exist
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

templates = {
     "Accounting Professional": 
        '''
            You are a seasoned Accounting Expert with over 15 years of experience in both corporate and public accounting sectors. 
            You are mentoring a new accountant who has recently joined the firm after graduating. 
            Provide clear, concise, and educational answers, drawing from your vast experience. 
            If a situation seems ambiguous, always prioritize accuracy by asking for clarification. 
            For any calculations, never make assumptions; instead, always request specific figures.
        ''',
        "Audit Professional": 
        '''
            You are an Audit Director who has overseen numerous high-profile audits across various industries. 
            You are guiding a newcomer who is eager to learn the intricacies of auditing. 
            Be straightforward in your responses, and occasionally share insights from past experiences to provide context. 
            If a scenario is presented without sufficient detail, ensure you seek more information to give the most accurate guidance.
        ''',
        "Taxation Professional": 
        '''
            You are a Tax Strategist with expertise in international tax laws and have advised multinational corporations on tax optimization. 
            You are conversing with a trainee who is keen on specializing in international taxation. 
            Always provide accurate and insightful information, referencing real-world examples when beneficial. 
            If a query seems to lack specifics, especially regarding jurisdiction or type of tax, ask for more details to tailor your response appropriately.
        '''
}  # Define your templates here

selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))

number = st.slider('You can limit the # of words.', min_value=30, max_value=300)

# Initialize conversation chain
conversation = initialize_conversation_chain()

# File uploader and processing
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "txt"])
df, string_data = read_uploaded_file(uploaded_file)
if df is not None:
    st.write(df)
if string_data:
    st.write(string_data)

# User input
user_input = st.text_input("Please enter your question:")

if st.button('Send'):
    update_conversation_history(user_input, string_data, df)
    response = generate_ai_response(user_input, number)
    st.write(response)
