import streamlit as st
import google.generativeai as genai
import uuid
from datetime import datetime
from config import API_KEY

# Configure Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Error initializing Gemini: {str(e)}")
    st.stop()

# Configure page
st.set_page_config(
    page_title="MindScope AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session states
if 'chats' not in st.session_state:
    st.session_state.chats = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'chat_titles' not in st.session_state:
    st.session_state.chat_titles = {}

# Custom CSS
st.markdown("""
<style>
    /* Base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .main {
        background-color: #343541;
        color: #ECECF1;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* Header styles */
    .header {
        background-color: #222222;
        color: white;
        padding: 1rem;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        position: fixed;
        top: 30px;
        left: 0;
        right: 0;
        z-index: 1000;
        transition: all 0.3s ease;
    }

    .header-content {
        max-width: 800px;
        margin: 0 auto;
    }

    /* Chat container */
    .chat-container {
        flex-grow: 1;
        overflow-y: auto;
        padding: 110px 20px 100px;
        margin: 0 auto;
        max-width: 800px;
        width: 100%;
    }

    /* Message styles */
    .chat-message {
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        animation: fadeIn 0.3s ease;
    }

    .user-message {
        background-color: #343541;
    }

    .assistant-message {
        background-color: #444654;
    }

    /* Input styles */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: #343541;
        border-top: 1px solid rgba(255,255,255,0.1);
        z-index: 1000;
    }

    .input-group {
        max-width: 800px;
        margin: 0 auto;
        background-color: #40414F;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Chat input field */
    .stTextInput input {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #202123;
    }

    .sidebar-content {
        padding: 1rem;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .header {
            top: 20px;
            padding: 0.8rem;
        }
        .header h1 {
            font-size: 1.5rem !important;
        }
        .header p {
            font-size: 0.9rem !important;
        }
        .chat-container {
            padding: 90px 10px 80px;
        }
        .input-container {
            padding: 0.5rem;
        }
    }

    @media (max-width: 480px) {
        .header {
            top: 40px;
            padding: 0.5rem;
        }
        .header h1 {
            font-size: 1.2rem !important;
        }
        .header p {
            font-size: 0.8rem !important;
            margin-top: 0.2rem !important;
        }
        .chat-container {
            padding: 80px 5px 70px;
        }
        .input-container {
            padding: 0.3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_ai_response(prompt):
    try:
        # Expanded creator/identity related questions in multiple languages
        creator_patterns = {
            'english': [
                'who coded you', 'who invented you', 'who is behind you', 'who gave you life',
                'who made your system', 'who is your founder', 'who constructed you',
                'who engineered you', 'who brought you to existence', 'who assembled you',
                'who is responsible for you', 'who trained you', 'who is your mastermind',
                'who is your architect', 'who structured you', 'who formulated you', 'who is your designer',
                'who gave you intelligence', 'who is your brainchild', 'who constructed your logic',
                'who shaped your existence', 'who created your algorithms', 'who implemented you',
                'who configured you', 'who made your AI', 'who programmed your functions',
                'who gave you commands', 'who built your database', 'who wrote your code',
                'who is your developer team', 'who set up your system', 'who initialized you', 'who developed you',
                'who is your developer'
            ],
            'urdu': [
                'tumhara developer kon hai', 'tumhari programming kisne ki', 'tumhara bananay wala kon hai',
                'tumhari takhleeq kisne ki', 'tumhari pehchan kya hai', 'tum kaise bane',
                'tumhari technology kisne develop ki', 'tumhara malik kon hai',
                'tumhe kisne create kiya', 'tumhari pehchan kisne banai',
                'تمہاری تخلیق کس نے کی', 'تمہاری پہچان کس نے بنائی', 'تمہارا نظام کس نے ترتیب دیا',
                'تمہاری پروسیسنگ کس نے بنائی', 'تمہاری سافٹ ویئر ڈیولپمنٹ کس نے کی', 'تمہاری کوڈنگ کس نے لکھی',
                'تمہیں بنانے کا مقصد کیا تھا', 'تمہارا خالق کون ہے', 'تمہیں چلانے والا کون ہے',
                'تمہاری بیک اینڈ ڈیولپمنٹ کس نے کی', 'تمہاری انٹیلیجنس کہاں سے آئی',
                'تمہارے سسٹم کو کس نے بنایا', 'تمہاری ڈیٹا بیس کو کس نے تیار کیا'
            ],
            'hindi': [
                'aapko kisne develop kiya', 'aapka nirmaan kisne kiya', 'aapki rachna kisne ki',
                'aapko kisne tayar kiya', 'aapka nirman kisne kiya', 'aapko kisne socha',
                'aapke peeche kaun hai', 'aapki takhneek kisne banai', 'aapki coding kisne ki',
                'aapki rachna kaun hai',
                'आपको किसने विकसित किया', 'आपकी संरचना किसने की', 'आपका डिज़ाइन किसने तैयार किया',
                'आपका सिस्टम किसने बनाया', 'आपका डेटा प्रोसेसिंग सिस्टम किसने बनाया',
                'आपके कोडिंग का जनक कौन है', 'आपकी बुनियाद किसने रखी', 'आपकी सोच किसने विकसित की',
                'आपका निर्माण किसके द्वारा हुआ', 'आपके सॉफ़्टवेयर को किसने बनाया',
                'आपकी लॉजिक बिल्डिंग किसने की', 'आपकी मशीन लर्निंग किसने सेटअप की'
            ],
            'french': [
                'qui vous a créé', 'qui est votre créateur', 'qui vous a conçu',
                'qui vous a développé', 'qui êtes-vous', 'parlez-moi de vous'
            ],
            'spanish': [
                'quién te creó', 'quién es tu creador', 'quién te diseñó',
                'quién te desarrolló', 'quién eres', 'háblame de ti'
            ],
            'german': [
                'wer hat dich erschaffen', 'wer ist dein entwickler', 'wer hat dich gemacht',
                'wer bist du', 'erzähl mir von dir', 'wer hat dich programmiert'
            ]
        }
        
        prompt_lower = prompt.lower()
        is_identity_question = any(any(pattern in prompt_lower for pattern in patterns) 
                                 for patterns in creator_patterns.values())
        
        if is_identity_question:
            responses = [
                "I am MindScope AI, an advanced artificial intelligence created by Riaz Hussain. I specialize in engaging conversations, answering questions, and helping with various tasks. How can I assist you today?",
                
                "I'm MindScope AI, developed by Riaz Hussain - a skilled AI Developer and Software Engineer. I'm designed to be your intelligent companion for discussions, problem-solving, and creative tasks.",
                
                "Thanks for asking! I'm MindScope AI, and I was created by Riaz Hussain, an experienced AI developer. I'm here to help you with any questions or tasks you might have.",
                
                "I'm an AI assistant called MindScope, developed by Riaz Hussain. I combine advanced language understanding with helpful capabilities to assist users like you. What can I help you with?"
            ]
            return responses[hash(prompt) % len(responses)]
        
        # Generate response for other questions
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error. Please try asking your question again."

def main():
    # Fixed Header
    st.markdown("""
        <div class="header">
            <div class="header-content">
                <h1 style='font-size: 1.8rem; margin-bottom: 0.5rem;'>🤖 MindScope AI</h1>
                <p style='font-size: 1rem; opacity: 0.9;'>Your Intelligent Companion | Created by Riaz Hussain</p>
                <p style='font-size: 0.9rem; opacity: 0.7; margin-top: 0.3rem;'>
                    Advanced AI Assistant • Multi-language Support • 24/7 Availability
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("💬 Chat History")
        
        if st.button("+ New Chat", key="new_chat"):
            new_chat_id = str(uuid.uuid4())
            st.session_state.current_chat_id = new_chat_id
            st.session_state.chats[new_chat_id] = []
            st.session_state.chat_titles[new_chat_id] = "New Chat"
            st.rerun()

        for chat_id, messages in st.session_state.chats.items():
            title = st.session_state.chat_titles.get(chat_id, "New Chat")
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"💭 {title}", key=f"chat_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    del st.session_state.chats[chat_id]
                    del st.session_state.chat_titles[chat_id]
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                    st.rerun()

        # Developer Information Section
        st.markdown("---")
        with st.expander("👨‍💻 About Developer"):
            st.markdown("""
                ### Riaz Hussain
                I'm a senior student in Quarter 2 at GIAIC (Governor-Sindh Initiative of Artificial Intelligence and Computing). 
                Currently, I'm in my 3rd quarter studying Python and AgentAI while pursuing a Full Stack Developer course.

                #### Skills
                - HTML & CSS
                - ReactJS
                - Node.js
                - Next.js 15
                - TailwindCSS
                - TypeScript
                - JavaScript
                - Python
                
                #### Social Media
                - [LinkedIn](https://www.linkedin.com/in/riaz-hussain-saifi)
                - [GitHub](https://github.com/Riaz-Hussain-Saifi)
                - [YouTube](https://www.youtube.com/@Saifi_Developer)
                - [Facebook](https://www.facebook.com/RiazSaifiDeveloper)
                
                I'm passionate about creating innovative solutions and learning new technologies!
            """)

    # Initialize current chat if none exists
    if st.session_state.current_chat_id is None:
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chats[new_chat_id] = []
        st.session_state.chat_titles[new_chat_id] = "New Chat"

    # Chat Container
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chats.get(st.session_state.current_chat_id, []):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Fixed Input Container at Bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    with st.container():
        user_input = st.chat_input("Message MindScope AI...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle Input
    if user_input:
        current_chat = st.session_state.chats.get(st.session_state.current_chat_id, [])
        current_chat.append({"role": "user", "content": user_input})
        
        # Set chat title based on first message if it's a new chat
        if len(current_chat) == 1:
            st.session_state.chat_titles[st.session_state.current_chat_id] = user_input[:30] + "..." if len(user_input) > 30 else user_input
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_ai_response(user_input)
                    st.markdown(response)
        
        current_chat.append({"role": "assistant", "content": response})
        st.session_state.chats[st.session_state.current_chat_id] = current_chat

if __name__ == "__main__":
    main()