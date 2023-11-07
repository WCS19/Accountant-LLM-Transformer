from config import openai_api_key
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts import MessagesPlaceholder



chat = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4-1106-preview") #adding model arg to use gpt-4-1106-preview


memory = ConversationBufferMemory()

# Define prompt template to set contextual scope
template =  '''
You are a Tax professional. 
You are talking  to a junior accountant. 
Please answer as honestly as possible. 
Please feel free to ask clarifying questions if more context is needed. 
If asked to calculate anything, do not assume any numerical dollar values, ask for exact amounts.
'''

system_message = SystemMessagePromptTemplate.from_template(template=template)
PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')

# Define a conversation
conversation = ConversationChain(
    llm=chat,
    prompt=PROMPT,
    verbose=False, 
    memory=memory,
)

while True:
    # Prompt the user for their input
    user_input = input("Please enter your message (or type 'exit' to quit): ")
    
    # Check if the user wants to exit
    if user_input.lower() in ['exit', 'quit']:
        break

    # Use the user's input in the conversation.predict() method
    response = conversation.predict(input=user_input)

    print(response)