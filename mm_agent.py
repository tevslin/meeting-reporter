from datetime import datetime
import json5 as json

from langgraph.graph import Graph

from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI

class WriterAgent:

    def writer(self, the_text:str,word_count=500):
        
        sample_json = """
            {
              "title": title of the article,
              "date": today's date,
              "body": The body of the article,
                "summary": "2 sentences summary of the article"
            }
            """

        prompt = [{
            "role": "system",
            "content": "You are a newspaper writer. Your sole purpose is to write a well-written article about the meeting described in the minutes "
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n."

                       f"{the_text}\n"
                       f""""Your task is to write an article for me about the meeting described above covering what seems most important.
                       The article should be approximately {word_count} words and should be divided into paragraphs
                       using newline characters.
                       You are reporting news. Do not editorialize."""
                       f"Please return nothing but a JSON in the following format:\n"
                       f"{sample_json}\n "

        }]

        lc_messages = convert_openai_messages(prompt)
        optional_params = {
            "response_format": {"type": "json_object"}
        }

        response = ChatOpenAI(model='gpt-4-0125-preview', max_retries=1, model_kwargs=optional_params).invoke(lc_messages).content
        print (response)
        return json.loads(response)

    def revise(self, article: dict):
        sample_revise_json = """
            {
                "body": The body of the article,,
                "message": "message to the critique"
            }
            """
        prompt = [{
            "role": "system",
            "content": "You are a newspaper editor. Your sole purpose is to edit a well-written article about a "
                       "topic based on given critique\n "
        }, {
            "role": "user",
            "content": f"{str(article)}\n"
                        f"Your task is to edit the article based on the critique given.\n "
                        f"Please return json format of the 'paragraphs' and a new 'message' field"
                        f"to the critique that explain your changes or why you didn't change anything.\n"
                        f"please return nothing but a JSON in the following format:\n"
                        f"{sample_revise_json}\n "

        }]

        lc_messages = convert_openai_messages(prompt)
        optional_params = {
            "response_format": {"type": "json_object"}
        }

        response = ChatOpenAI(model='gpt-4-0125-preview', max_retries=1, model_kwargs=optional_params).invoke(lc_messages).content
        response = json.loads(response)
        print(f"For article: {article['title']}")
        print(f"Writer Revision Message: {response['message']}\n")
        return response

    def run(self, article: dict):
        print("writer working...",article.keys())
        critique = article.get("critique")
        if critique is not None:
            article.update(self.revise(article))
        else:
            article.update(self.writer( article["source"],word_count=article['words']))
        return article


class CritiqueAgent:

    def critique(self, article: dict):
        prompt = [{
            "role": "system",
            "content": "You are a newspaper writing critique. Your sole purpose is to provide short feedback on a written "
                       "article so the writer will know what to fix.\n "
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n."
                       f"{str(article)}\n"
                       f"Your task is to provide a really short feedback on the article only if necessary.\n"
                       f"the article is a news story so should not include editrial comments."
                       f"if you think the article is good, please return only the word 'None' without the surrounding hash marks.\n"
                       f"do NOT return any text except the word 'None' without surrounding hash marks if no further work is needed onthe article."
                       f"if you noticed the field 'message' in the article, it means the writer has revised the article"
                       f"based on your previous critique. you can provide feedback on the revised article or just "
                       f"return only the word 'None' without surrounding hash mark if you think the article is good.\n"
                       f"Please return a string of your critique or the word 'None' without surrounding hash marks.\n"
        }]

        lc_messages = convert_openai_messages(prompt)
        response = ChatOpenAI(model='gpt-4', max_retries=1).invoke(lc_messages).content
        if response == 'None':
            return {'critique': None}
        else:
            print(f"For article: {article['title']}")
            print(f"Feedback: {response}\n")
            return {'critique': response, 'message': None}

    def run(self, article: dict):
        print("critiquer working...",article.keys())
        article.update(self.critique(article))
        article["form"]=1
        return article


class InputAgent:
       
    def run(self,article:dict):
        from mytools import extract_text_from_path_or_url
        
        print ("input agent running...")
        print(article.keys())
        if "url" in article:
            the_text=extract_text_from_path_or_url(article["url"])
            
        else:
            if "raw" in article: #if already read
                the_text=extract_text_from_path_or_url(article["file_name"],content=article['raw'])
                del article["raw"]
            else:
                the_text=extract_text_from_path_or_url(article['file_name'])
        article["source"]=the_text
        return article
            
class OutputAgent:
    def run(self,article:dict):
        print(f"Title: {article['title']}\nSummary: {article['summary']}\nBody:{article['body']}")
        return article
      
class HumanReviewAgent:
    def run(self,article:dict):
        print("human review agent running",article.keys())
        if article["button"]=='OK':
            if not article["critique"]:
                article["critique"]=None
                article["quit"]="yes"
        else:
            assert False,"Canceled by editor"
        #print("from user:",article["body"],"\n","from dialog:",result["text1"])
        return article
    
class StartAgent:
    name='start'
    def run(self,dummy):
        print("start agent working")
        return {"form":0,"name":self.name}
          
            
        
class StateMachine:
    def __init__(self,api_key=None):
        import os
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3
        
        def from_conn_stringx(cls, conn_string: str,) -> "SqliteSaver":
            return SqliteSaver(conn=sqlite3.connect(conn_string, check_same_thread=False))
        SqliteSaver.from_conn_stringx=classmethod(from_conn_stringx)

        if api_key:
            os.environ['OPENAI_API_KEY']=api_key
        else:
            from dotenv import load_dotenv
            load_dotenv()
        self.memory = SqliteSaver.from_conn_stringx(":memory:")

        start_agent=StartAgent()
        input_agent=InputAgent()
        writer_agent = WriterAgent()
        critique_agent = CritiqueAgent()
        output_agent=OutputAgent()
        human_review=HumanReviewAgent()

        workflow = Graph()

        workflow.add_node(start_agent.name,start_agent.run)
        workflow.add_node("input",input_agent.run)
        workflow.add_node("write", writer_agent.run)
        workflow.add_node("critique", critique_agent.run)
        workflow.add_node("output",output_agent.run)
        workflow.add_node("human_review",human_review.run)
 
        #workflow.add_edge(start_agent.name,"input")
        workflow.add_edge("input","write")

        workflow.add_edge('write', 'critique')
        workflow.add_edge('critique','human_review')
        workflow.add_edge(start_agent.name,"input")
        workflow.add_conditional_edges(start_key='human_review',
                                       condition=lambda x: "accept" if x['critique'] is None else "revise",
                                       conditional_edge_mapping={"accept": "output", "revise": "write"})
                                       
        
        # set up start and end nodes
        workflow.set_entry_point(start_agent.name)
        workflow.set_finish_point("output")
        
        self.thread={"configurable": {"thread_id": "2"}}
        self.chain=workflow.compile(checkpointer=self.memory,interrupt_after=[start_agent.name,"critique"])
    def start(self):
        result=self.chain.invoke("",self.thread)
        #print("*",self.chain.get_state(self.thread),"*")
        #print("r",result)
        if result is None:
            values=self.chain.get_state(self.thread).values
            last_state=next(iter(values))
            return values[last_state]
        return result
        
    def resume(self,new_values:dict):
        values=self.chain.get_state(self.thread).values
        #last_state=self.chain.get_state(self.thread).next[0].split(':')[0]
        last_state=next(iter(values))
        #print(self.chain.get_state(self.thread))
        values[last_state].update(new_values)
        self.chain.update_state(self.thread,values[last_state])
        result=self.chain.invoke(None,self.thread,output_keys=last_state)
        #print("r",result)
        if result is None:
            values=self.chain.get_state(self.thread).values
            last_state=next(iter(values))
            return self.chain.get_state(self.thread).values[last_state]
        return result       
      

if __name__ == '__main__': #test code
    
    from mm_tkinter import process_form

       
    sm=StateMachine()
    result =sm.start()
    while "quit" not in result:
        new_values=process_form(result["form"],result)
        result=sm.resume (new_values)
    