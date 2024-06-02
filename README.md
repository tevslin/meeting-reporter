# meeting_reporter
Code, samples, and a working streamlit app for demonstrating:
1. multiagent and human collaboration
2. the use of langgraph to coordinate the interaction
3. the mating of the langgraph and streamlit state machines (non-trivial)

The agents are prompted to create a newsstory in collaboration with a human(you)from a meeting transcript or minutes which you either provide a URL to or upload. The input agent uploads or downloads the document as appropriate and extracts text from it; the writer agent drafts; the critique agent critiques; you can edit either the draft or the critique. the cycle continues until you are satisfied with a draft at which point it ia giiven to the output agent to display.

This concept could easily be extended to different types of news stories as well as different sources ands could include fact checking, RAG from an archive etc.

I started with meetings because there are many more public meetings than there are reporters to cover them.

## overview

[langgraph](https://github.com/langchain-ai/langgraph)is a library for building stateful, multi-actor applications with LLMs, built on top of (and intended to be used with) LangChain. It is low-code but not no-code.

The depository is set up so that an application can be uploaded to the Streamlit cloud. That has been done and the application is [here](https://meeting-reporter.streamlit.app/). The .gitignore and requirements.txt are specific to streamlit cloud.

mm_agent.py in this repository contains the main logic and all of the langchain speciifc code for the application. If you run it as a main program in your own Python environment, it will use tkinter rather than streamlit for UI.

mm_st.py is the main program of the streamlit version and contains all the streamlit specific logic

mytools.py are a few miscellaneous uilities of mine.

mm_tkinter.py contains  the tkinter specific code. It is not used in the streamliit version.


## usage

### as a streamlit app:
Click the URL https://meeting-reporter.streamlit.app/. You will need an OPENAI api key in the paid tier. The free api key will not work because the agents use GPT4.

### as a basis for deploying your own Streamlit app.
1. clone the repository.
2. make any changes you want to make.
3. be sure to update .gitignore and requirements.txt as needed.
4. deploy from Streamlit (you need an acount, of course).

### in a Python environment

1. download the mm_agent, mytools, and mm_tkinter modules 
2. Set up a .env file with an entry for OPENAI_API_KEY set equal to your paid OpenAI key or otherwise set an environmental variable with that name
3. Run mm_agent.py.

### as a custom GPT (no api key or paid subscription required)
click the URL https://chatgpt.com/g/g-roNR24Ty6-collaborative-meeting-reporter.

## ideas for enhancement
1. Select a prompt depending on the content of the source
2. Incorporate fact checking via browsing
3. Include a process for improving the prompts based on frequent critiqes
4. add sources and stories to a database (a morgue in news terms)
5. use RAG to consult the morgue and get background
6. embed in a larger collaborative newsroom process
7. acccept audio files for input
8. incorporate graphics

pull requests welcome

## privacy
No code here explititly collects any information of any kind. However, some usage stastics are available from both github and Streamlit.

## disclaimer
This all comes with no warranty of any kind nor any promise to fix problems or maintain compatabity with the code it uses. However, bug reports, issues, and enhancement pull requests are welcome.




