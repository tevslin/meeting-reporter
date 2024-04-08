import os

import streamlit as st
import mm_agent
#import ststreamer
from contextlib import redirect_stdout


def process_form(form_number,article):
    def set_value():
        print("set value",st.session_state.url)
        st.session_state["newvalues"]={"url":st.session_state.url}
        
    if form_number==0:
        st.text_input("Enter the URL of your source document:",key="url",
                                                           on_change=set_value)
    elif form_number==1:
        header = article["title"]
        st.title(header)
        
        # Instructions (if any)
        instruction_text = "You can edit either the article or the critique.\n Clear the critique to use the article as displayed. "
        if instruction_text:
            st.write(instruction_text)
        
        # Text Boxes and Labels
        initial_contents = [article["body"],article["critique"]]  
        titles = ["Draft Article", "Critique"] 
        
        text_boxes = []
        for content, title in zip(initial_contents, titles):
            st.subheader(title)
            text_input = st.text_area("", value=content, height=150 if titles.index(title) == 0 else 50)
            text_boxes.append(text_input)
        
        link_text = "Click here to open source document in browser."
        link_url = article["url"]
        if link_text and link_url:
            st.markdown(f"[{link_text}]({link_url})", unsafe_allow_html=True)

        # OK Button
        if st.button('OK'):
            # Perform actions based on the form submission here
            # For example, print or store the contents of text_boxes

            st.session_state["newvalues"]={"body":text_boxes[0],"critique":text_boxes[1],"button":"OK"}
        
        

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = None
    st.session_state['dm'] = None
    st.session_state['result']=None
    st.session_state["newvalues"]=None

# App title
st.title("AI-Human Collaboration with Reflection Agent")

# Sidebar for API key input


with st.sidebar:
    st.session_state['api_key'] = st.text_input("Enter your ChatGPT API key (Tier 1 or higher account):", type="password")
    

if st.session_state['api_key'] and st.session_state["dm"] is None:
    os.environ['OPENAI_API_KEY'] = st.session_state['api_key']
    st.session_state['dm'] = mm_agent.StateMachine(st=st)
    st.session_state["result"]=st.session_state['dm'].start()
    
def rerun():
    st.session_state['dm'] = None
    st.session_state['result']=None
    st.session_state["newvalues"]=None
    

if st.session_state["result"]:
    print("have result")
    #st.session_state["newvalues"]
    if "quit" not in st.session_state['result']:
        if st.session_state["newvalues"] is None:
            process_form(st.session_state['result']["form"],st.session_state['result'])
        if st.session_state["newvalues"]:
            #if len(st.session_state["newvalues"]["url"])>0:
                print("*********")
                #st.session_state["newvalues"]
                with st.spinner("Please wait... Bots at work"):
                    st.session_state["result"]=st.session_state['dm'].resume(st.session_state["newvalues"])
                st.session_state["newvalues"]=None
                st.rerun()
    if "quit" in st.session_state["result"]:
        st.subheader(st.session_state.result["title"])
        st.write(st.session_state.result["date"])
        st.markdown(st.session_state.result["body"])
        st.write("\n")
        st.write("summary:",st.session_state.result["summary"])
        
        with st.sidebar:
            st.button("Run with new document",key="rerun",on_click=rerun)
        
            


    


