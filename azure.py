import streamlit as st
import os
import pandas as pd
from io import StringIO

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate


def show_instructions_page():
    st.title("Accounting Assistant Overview & Instructions")
    st.write("Welcome to the Accounting Assistant!")
    st.markdown("""
        ### How to Use This Application
        - Choose a business vertical from the dropdown menu that best suits your business needs.
        - Set your preferred verbosity level, from Low, Medium, to High, to ensure the output response matches your needed level of detail.
        - Upload any relevant files (csv, txt) if you need help with analysis.
        - Enter your question in the text input box.
        - Click 'Send' to get a response.
        - Use 'Reset Conversation' to start over and clear conversation history.
    """)
    st.markdown("""
         ### Example Questions:
        - Below are some example questions. Click on any of these to see a sample response:
                """
    )

    #Buttons lack logic to correctly select the corresponding template.
    if st.button('Accounting: Can you explain to me how to reconcile a bank statement?'):
        st.session_state['preset_input'] = 'Can you explain to me how to reconcile a bank statement'
        st.session_state['current_page'] = 'Application'  # Set the current page to Application

    if st.button('Audit: How do I test depreciation?'):
        st.session_state['preset_input'] = 'How do I test depreciation?'
        st.session_state['current_page'] = 'Application'  # Set the current page to Application

    if st.button('Taxation: How do I determine the number of dependents?'):
        st.session_state['preset_input'] = 'How do I determine the number of dependents?'
        st.session_state['current_page'] = 'Application'  # Set the current page to Application
        


    st.markdown("""
                To view a sample response:
            - Click on the example you're interested in.
            - Please manually switch to the 'Application' page.
            - There, you'll find the selected example query already running.
            - A sample response based on the chosen query will be displayed.
            - If you would like to begin asking the Chat Bot question, hit "Reset Conversation".
            - If you wish to return to this page or navigate to other sections, use the navigation bar on the sidebar.
""")

# Function to initialize the chat model and memory
def initialize_chat_model(api_key, model_name):
    openai_api_key=os.environ['OPENAI_API_KEY']
    chat = ChatOpenAI(openai_api_key=openai_api_key, model=model_name)
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
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "txt"])
    df, string_data = None, None
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    return df, string_data


# Function to process and display user input and AI response
def process_user_input(conversation, df, string_data, preset_input=None):
    if preset_input:
        user_input = preset_input
    else:
        user_input = st.text_input("Please enter your question:")

    if st.button('Send') or preset_input:
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
    openai_api_key=os.environ['OPENAI_API_KEY']
    st.session_state.conversation_history = []
    initialize_chat_model(api_key=openai_api_key, model_name="gpt-4-1106-preview")



# Function to show the application page
def show_application_page():                                          #Version with CHAT BOT WRITTEN AT TOP
    st.title('Accounting Assistant')
    openai_api_key=os.environ['OPENAI_API_KEY']  
    openai_api_key = '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'
    chat, memory = initialize_chat_model(api_key=openai_api_key, model_name="gpt-4-1106-preview")

    templates = get_templates()
    verbosity = st.select_slider("Select response verbosity", 
                                 options=['Low', 'Medium', 'High'],
                                 value='Medium')  # Default value set to 'Medium'
    verbosity_instruction = get_verbosity_instruction(verbosity)
    selected_template = st.selectbox("Choose a business vertical to continue:", list(templates.keys()))

    template_with_verbosity = templates[selected_template] + "\n\n" + verbosity_instruction

    # system_message = SystemMessagePromptTemplate.from_template(template=template_with_verbosity)
    PROMPT = PromptTemplate(input_variables=['history', 'input'], template=template_with_verbosity + '.\n\nCurrent conversation:\n{history}\nHuman: {input}\nAI:')
    conversation = ConversationChain(llm=chat, prompt=PROMPT, verbose=False, memory=memory)

    df, string_data = handle_file_upload()

    # Chat Divider and Subheader
    st.divider()
    st.subheader("🤖💬 Chat Bot")

    # Check for and handle preset input
    if 'preset_input' in st.session_state and st.session_state['preset_input']:
        process_user_input(conversation, df, string_data, st.session_state['preset_input'])
        st.session_state['preset_input'] = None  # Reset the preset input
    else:
        process_user_input(conversation, df, string_data)

    if st.button("Reset Conversation"):
        reset_conversation()



def main():
    st.sidebar.title("Navigation")
    # Initialize the current page in session_state if not already set
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Instructions'
    page = st.sidebar.radio("Select a Page", ["Instructions", "Application"])
    # Check for manual page switch
    if page != st.session_state['current_page']:
        st.session_state['current_page'] = page
    # Display the selected page
    if st.session_state['current_page'] == "Instructions":
        show_instructions_page()
    elif st.session_state['current_page'] == "Application":
        show_application_page()


if __name__ == "__main__":
    main()





