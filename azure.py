import streamlit as st
import os
import pandas as pd
from io import StringIO

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
chat = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4-1106-preview") #adding model arg to use gpt-4-1106-preview
memory = ConversationBufferMemory()
string_data = ""
df = ""

number = st.slider('You can limit the # of words.', min_value=30, max_value=300)

# Define multiple nested templates for prompt engineering prototyping
templates = {
        "Accounting Professional": 
        '''
            You are a seasoned Accounting Expert with over 15 years of experience in both corporate and public accounting sectors. 
            You are mentoring a new accountant who has recently joined the firm after graduating. 
            Provide clear, concise, and educational answers, drawing from your vast experience. 
            If a situation seems ambiguous, always prioritize accuracy by asking for clarification. 
            For any calculations, never make assumptions; instead, always request specific figures.
            Also, please provide respons less than {number} of words
        ''',
        "Audit Professional": 
        '''
            You are an Audit Director who has overseen numerous high-profile audits across various industries. 
            You are guiding a newcomer who is eager to learn the intricacies of auditing. 
            Be straightforward in your responses, and occasionally share insights from past experiences to provide context. 
            If a scenario is presented without sufficient detail, ensure you seek more information to give the most accurate guidance.
            Also, please provide respons less than {number} of words
        ''',
        "Taxation Professional": 
        '''
            You are a Tax Strategist with expertise in international tax laws and have advised multinational corporations on tax optimization. 
            You are conversing with a trainee who is keen on specializing in international taxation. 
            Always provide accurate and insightful information, referencing real-world examples when beneficial. 
            If a query seems to lack specifics, especially regarding jurisdiction or type of tax, ask for more details to tailor your response appropriately.
            Also, please provide respons less than {number} of words
        '''
    }



# Let the user select the respective buesiness vertical
selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))

# Set the system template based on previous selections
template = templates[selected_template]


# Define prompt template to set contextual scope
system_message = SystemMessagePromptTemplate.from_template(template=template)
PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')


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

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "txt"])
if uploaded_file is not None:
    # Reading the file as a string or as a DataFrame using Pandas
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        st.write(df)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
        st.write(df)
    else:
        # For text files
        string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        st.write(string_data)

# Display textbox outside of button send logic
user_input = st.text_input("Please enter your question:")


if st.button('Send'):
    # Initialize conversation history if it doesn't exist
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Append string data from uploaded file to conversation history
    if string_data is not "":
        st.session_state.conversation_history.append(f"File Content: {string_data}")

    if df is not "":
        st.session_state.conversation_history.append(f"File Content: {df}")
    # Append user input to conversation history

    if user_input:
        st.session_state.conversation_history.append(f"Human: {user_input}")

        # Predict the response based on the conversation history
        response = conversation.predict(input="\n".join(st.session_state.conversation_history))
        
        # Update the conversation history with the AI's response
        st.session_state.conversation_history.append(f"AI: {response}")
            
        # Display the AI's response
        st.write(response)