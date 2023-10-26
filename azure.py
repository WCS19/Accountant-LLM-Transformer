import streamlit as st
import os

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate

openai_api_key=os.environ['OPENAI_API_KEY']
st.title('TaxBot')

chat = ChatOpenAI(openai_api_key=openai_api_key)
memory = ConversationBufferMemory()


# Define multiple templates
templates = {
    "Accounting Professional": '''
You are a senior Accounting Professional. 
You are talking to a junior accountant. 
Please answer as honestly as possible. 
Please feel free to ask clarifying questions if more context is needed. 
If asked to calculate anything, do not assume any numerical dollar values, ask for exact amounts.
''',
    "Audit Professional": '''
You are an Audit Professional. 
You are talking to a junior auditor. 
Please answer as honestly as possible. 
Please feel free to ask clarifying questions if more context is needed.
''',
    "Taxation Professional": '''
You are a Taxation Professional. 
You are talking to a junior tax associate. 
Please answer as honestly as possible. 
Please feel free to ask clarifying questions if more context is needed.
'''
}

# Use st.selectbox to let the user select a template
selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))

# Set the system_message based on the user's selection
template = templates[selected_template]
system_message = SystemMessagePromptTemplate.from_template(template=template)
PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')

conversation = ConversationChain(
    llm=chat,
    prompt=PROMPT,
    verbose=False, 
    memory=memory,
)
# template =  '''
# You are a Tax professional. 
# You are talking to a junior accountant. 
# Please answer as honestly as possible. 
# Please feel free to ask clarifying questions if more context is needed. 
# If asked to calculate anything, do not assume any numerical dollar values, ask for exact amounts.
# '''

# system_message = SystemMessagePromptTemplate.from_template(template=template)
# PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')

conversation = ConversationChain(
    llm=chat,
    prompt=PROMPT,
    verbose=False, 
    memory=memory,
)

# Initialize session state for conversation history if it doesn't exist
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Always display the text input box
user_input = st.text_input("Please enter your message:")

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

#2nd iteration of code                  didnt capture conversation history
# Always display the text input box
# user_input = st.text_input("Please enter your message:")

# if st.button('Send'):
#     if user_input:
#         response = conversation.predict(input=user_input)
#         st.write(response)






#initial code, commenting out to test streamlit functionality
# def chat_with_bot():
#     user_input = st.text_input("Please enter your message:")
#     if user_input:
#         response = conversation.predict(input=user_input)
#         st.write(response)

# if st.button('Send'):
#     chat_with_bot()
