import streamlit as st
import os
# from config import openai_api_key
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate

openai_api_key=os.environ['OPENAI_API_KEY']
st.title('TaxBot')

chat = ChatOpenAI(openai_api_key=openai_api_key)
memory = ConversationBufferMemory()

template =  '''
You are a Tax professional. 
You are talking to a junior accountant. 
Please answer as honestly as possible. 
Please feel free to ask clarifying questions if more context is needed. 
If asked to calculate anything, do not assume any numerical dollar values, ask for exact amounts.
'''

system_message = SystemMessagePromptTemplate.from_template(template=template)
PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')

conversation = ConversationChain(
    llm=chat,
    prompt=PROMPT,
    verbose=False, 
    memory=memory,
)

def chat_with_bot():
    user_input = st.text_input("Please enter your message:")
    if user_input:
        response = conversation.predict(input=user_input)
        st.write(response)

if st.button('Send'):
    chat_with_bot()
