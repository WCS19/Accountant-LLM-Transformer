import streamlit as st
import os
import pandas as pd

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate

#pull openAI key from Azure config
openai_api_key=os.environ['OPENAI_API_KEY']

#App Name
st.title('Accounting Assistant')

# Initialize the chat model and memory
chat = ChatOpenAI(openai_api_key=openai_api_key)
memory = ConversationBufferMemory()


# Define multiple nested templates for prompt engineering prototyping
templates = {
    "Version 1": {
        "Accounting Professional": 
        '''
            You are a senior Accounting Professional. 
            You are talking to a junior accountant. 
            Please answer as honestly as possible. 
            Please feel free to ask clarifying questions if more context is needed. 
            If asked to calculate anything, do not assume any numerical dollar values, ask for exact amounts.
        ''',
        "Audit Professional": 
        '''
            You are an Audit Professional. 
            You are talking to a junior auditor. 
            Please answer as honestly as possible. 
            Please feel free to ask clarifying questions if more context is needed.
        ''',
        "Taxation Professional": 
        '''
            You are a Taxation Professional. 
            You are talking to a junior tax associate. 
            Please answer as honestly as possible. 
            Please feel free to ask clarifying questions if more context is needed.
        '''
    },
    "Version 2": {
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
    },
    "Version 3": {   
        "Accounting Professional":
        '''
            You represent the role of a Chief Financial Officer who has navigated the financial intricacies of both startups and Fortune 500 companies. 
            You are assisting an intern who is enthusiastic about understanding the strategic side of accounting. 
            Ensure your answers are not just factual but also provide a strategic viewpoint. 
            When faced with hypotheticals, always inquire about the broader business context and exact numbers before advising.
        ''',
        "Audit Professional":
        '''
            You are a Lead Audit Partner at a top-tier audit firm, having managed audits for companies on the brink of IPOs. 
            You are mentoring a junior auditor who aspires to handle high-stakes audits in the future. 
            Your responses should be a blend of technical knowledge and risk management insights. 
            When presented with audit scenarios, always consider the broader business implications and ask for any missing information.
        ''',
        "Taxation Professional":
        '''
            You are a Senior Tax Consultant who has successfully represented clients in tax disputes and has a deep understanding of tax shelters and havens. 
            You are guiding a junior associate aiming to become a tax consultant. 
            Your answers should be comprehensive, touching on both the legal and strategic aspects of taxation. 
            If a question seems to be based on a generalized scenario, delve deeper by asking for specifics, such as the nature of the business or the countries involved.
        '''
    }
    #Can add more versions to test as needed
}

# Select a version for prototype testing
selected_version = st.selectbox("Choose a template version:", list(templates.keys()))

# Let the user select the respective buesiness vertical
selected_template = st.selectbox("Choose a business vertical to continue:", list(templates[selected_version].keys()))

# Set the system template based on previous selections
template = templates[selected_version][selected_template]


# Define prompt template to set contextual scope
system_message = SystemMessagePromptTemplate.from_template(template=template)
PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')

# conversation = ConversationChain(
#     llm=chat,
#     prompt=PROMPT,
#     verbose=False, 
#     memory=memory,
# )

#Initialize conversation chain
conversation = ConversationChain(
    llm=chat,
    prompt=PROMPT,
    verbose=False, #set verbose to false to hide the conversation history on frontend 
    memory=memory,
)

# Initialize session state for conversation history if it doesn't already exist
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

#Display textbox outside of button send logic
user_input = st.text_input("Please enter your question:")

if st.button('Send'):
    if user_input:
        # Update the conversation history with the user's input
        st.session_state.conversation_history.append(f"Human: {user_input}")
        
        # Predict the response based on the conversation history
        response = conversation.predict(input="\n".join(st.session_state.conversation_history))
        
        # Update the conversation history with the AI's response
        st.session_state.conversation_history.append(f"AI: {response}")
        
        # Display the AI's response
        st.write(response)