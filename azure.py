import streamlit as st
import os
import pandas as pd
from io import StringIO

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate


#Hardcoded open api key for local testing 
openai_api_key='sk-x'

def show_instructions_page(): 
    st.title("Application Overview & Instructions")
    st.write("Welcome to the Accounting Assistant!")
    st.markdown("""
        ### How to Use This Application
        - Choose a business vertical from the dropdown menu that best suites your business needs.
        - Set your preferred verbosity level, from Low, Medium, to High, to ensure the ouput response matches your needed level of detail.
        - Upload any relevant files (csv, xlsx, txt) if you need help with analysis.
        - Enter your question in the text input box.
        - Click 'Send' to get a response.
        - Use 'Reset Conversation' to start over and clear conversation history.
    """)

# Function to initialize the chat model and memory
def initialize_chat_model(api_key, model_name):
    chat = ChatOpenAI(openai_api_key=api_key, model=model_name)
    memory = ConversationBufferMemory()
    return chat, memory

# Function to get verbosity instruction
def get_verbosity_instruction(verbosity):
    if verbosity == 'Low':
        return 'Please respond in a concise manner. Keep your answer short and to the point.'
    elif verbosity == 'Medium':
        return 'Please provide a balanced response with enough detail to be clear, but not overly verbose.'
    elif verbosity == 'High':
        return 'Feel free to provide detailed and comprehensive responses, elaborating as much as necessary.'
    else:
        return ''

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

#Function to process user input
def process_user_input(conversation, df, string_data):
    user_input = st.text_input("Please enter your question:")
    if st.button('Send'):
        update_conversation_history(user_input, df, string_data)
        response = conversation.predict(input="\n".join(st.session_state.conversation_history))
        st.session_state.conversation_history.append(f"AI: {response}")
        # Display the entire conversation history
        for entry in st.session_state.conversation_history:
            st.write(entry)

# Function to update conversation history
def update_conversation_history(user_input, df=None, string_data=None):
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if string_data:
        st.session_state.conversation_history.append(f"File Content: {string_data}")
    if df is not None and not df.empty:
        st.session_state.conversation_history.append(f"File Content: {df}")
    if user_input:
        st.session_state.conversation_history.append(f"You: {user_input}")
        

# Function to reset the conversation
def reset_conversation():
    st.session_state.conversation_history = []
    initialize_chat_model(api_key=openai_api_key, model_name="gpt-4-1106-preview")


# Function to show the application page
def show_application_page():
    st.title('Accounting Assistant')
    # Initialize the chat model and memory
    #Pull openAI key from Azure config
    #openai_api_key=os.environ['OPENAI_API_KEY'] #uncomment to run on Azure
    openai_api_key = 'sk-x'
    chat, memory = initialize_chat_model(api_key=openai_api_key, model_name="gpt-4-1106-preview")
    # Retrieve templates
    templates = get_templates()
    # Add a slider for verbosity selection
    verbosity = st.select_slider("Select response verbosity", 
                                 options=['Low', 'Medium', 'High'],
                                 value='Medium')  # Default value set to 'Medium'
    # Get the verbosity instruction based on the selection
    verbosity_instruction = get_verbosity_instruction(verbosity)
    # User selects a business vertical
    selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))
    # Append the verbosity instruction to the selected template
    template_with_verbosity = templates[selected_template] + "\n\n" + verbosity_instruction
    # Set up the system message and prompt template
    system_message = SystemMessagePromptTemplate.from_template(template=template_with_verbosity)
    PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template_with_verbosity + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')
    # Create the conversation chain
    conversation = ConversationChain(llm=chat, prompt=PROMPT, verbose=False, memory=memory)
    # Handle file upload
    df, string_data = handle_file_upload()
    # Process user input
    process_user_input(conversation, df, string_data)
    # Add a reset button
    if st.button("Reset Conversation"):
        reset_conversation()

#Function to show navigation and application pages
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a Page", ["Application Instructions & Overview", "Accounting Assistant"])

    if page == "Application Instructions & Overview":
        show_instructions_page()
    elif page == "Accounting Assistant":
        show_application_page()


if __name__ == "__main__":
    main()

