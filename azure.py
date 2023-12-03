import streamlit as st
import os
import pandas as pd
from io import StringIO

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate

# Function to initialize the chat model and memory
def initialize_chat_model(api_key, model_name):
    chat = ChatOpenAI(openai_api_key=api_key, model=model_name)
    memory = ConversationBufferMemory()
    return chat, memory

# Function to define multiple nested templates
def get_templates():
    return {
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
    }

# Function to handle file uploads
def handle_file_upload():
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "txt"])
    df, string_data = None, None
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    return df, string_data

# Function to process and display user input and AI response
def process_user_input(conversation, df, string_data):
    user_input = st.text_input("Please enter your question:")
    if st.button('Send'):
        update_conversation_history(user_input, df, string_data)
        response = conversation.predict(input="\n".join(st.session_state.conversation_history))
        st.session_state.conversation_history.append(f"AI: {response}")
        st.write(response)

# Function to update conversation history
def update_conversation_history(user_input, df=None, string_data=None):
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if string_data:
        st.session_state.conversation_history.append(f"File Content: {string_data}")
    if df is not None and not df.empty:
        st.session_state.conversation_history.append(f"File Content: {df}")
    if user_input:
        st.session_state.conversation_history.append(f"Human: {user_input}")


# Main function to run the app
def main():
    st.title('Accounting Assistant')
    openai_api_key='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'
    chat, memory = initialize_chat_model(api_key=openai_api_key, model_name="gpt-4-1106-preview")
    templates = get_templates()
    selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))
    template = templates[selected_template]
    system_message = SystemMessagePromptTemplate.from_template(template=template)
    PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')
    conversation = ConversationChain(llm=chat, prompt=PROMPT, verbose=False, memory=memory)
    df, string_data = handle_file_upload()
    process_user_input(conversation, df, string_data)

if __name__ == "__main__":
    main()

