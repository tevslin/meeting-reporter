
    
def article_options():
    import tkinter as tk
    
    result={}
    
    def on_ok():
        nonlocal result
        result = {
            'button': 'OK',
            'origin': source_var.get(),
            'words': slider_var.get()
        }
        #print(result)
        root.destroy()
        return result
    
    def on_cancel():
        nonlocal result
        result={
            'button':'Cancel'
        }
        #print({'button': 'Cancel'})
        root.destroy()
        return result
    
    root = tk.Tk()
    root.title("Article Options")
    
    # Slider for "words in article"
    tk.Label(root, text="Words in article:").pack()
    slider_var = tk.IntVar(value=500)
    words_slider = tk.Scale(root, from_=100, to=2000, orient='horizontal', variable=slider_var)
    words_slider.pack()
    
    # Label and Radio buttons for source document
    tk.Label(root, text="Retrieve source document from:").pack()
    source_var = tk.StringVar(value="internet")
    tk.Radiobutton(root, text="The internet", variable=source_var, value="internet").pack()
    tk.Radiobutton(root, text="My computer", variable=source_var, value="computer").pack()
    
    # OK and Cancel buttons
    tk.Button(root, text="OK", command=on_ok).pack(side=tk.RIGHT)
    tk.Button(root, text="Cancel", command=on_cancel).pack(side=tk.RIGHT)
    
    root.mainloop()
    return result
    

def process_form(form:int,article):
    from tkinter import filedialog
    
    if form==0:
        answer = article_options()
        assert answer['button']=='OK', "Canceled by editor"
        del answer['button']
        if answer['origin']=="internet":
            next_answer=request_url()
            assert len(next_answer)>0,"Canceled by editor"
            answer['url']=next_answer
        else:
             file_name = filedialog.askopenfilename(title="Select source file", 
                                                    filetypes=[("PDF files", "*.pdf"),
                                                          ("Word documents", "*.docx"),
                                                          ("HTML files", "*.html"),
                                                          ("Text files", "*.txt")]
                                                    )
             assert len(file_name)>0,"Canceled by editor"
             answer["file_name"]=file_name
             
    elif form==1:
        answer= open_review_dialog(
        header=article["title"],
        initial_contents=[article["body"],article["critique"]],
        link_text="Click here to open source document in browser.",
        link_url=article.get("url"),
    )
    return answer
   
def request_url(top_label_text="Please enter a URL", 
                bottom_label_text=""):
    import tkinter as tk
    
    # Function to enable OK button based on text length
    def check_text_length(event=None):
        content = text_box.get("1.0", "end-1c")
        if len(content) >= 10:
            ok_button.config(state="normal")
        else:
            ok_button.config(state="disabled")

    # Function to handle OK button click
    def on_ok():
        # Using nonlocal to modify the outer scope variable
        nonlocal user_input
        user_input = text_box.get("1.0", "end-1c")
        dialog.destroy()

    # Function to handle Cancel button click
    def on_cancel():
        # Using nonlocal to modify the outer scope variable
        nonlocal user_input
        user_input = None
        dialog.destroy()
        


    # Function to handle right-click event
    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root, 0)

    # Function to paste text from clipboard
    def paste_from_clipboard():
        try:
            text = dialog.clipboard_get()
        except dialog.TclError:
            return
        text_box.insert(tk.INSERT, text)
        check_text_length()

    user_input = None  # Initialize return value within the function scope

    dialog = tk.Tk()
    dialog.title("URL Requester")

    tk.Label(dialog, text=top_label_text).pack(padx=10, pady=(10,0))

    text_box = tk.Text(dialog, height=2, width=50)
    text_box.pack(padx=10, pady=10)
    text_box.bind("<KeyRelease>", check_text_length)

    context_menu = tk.Menu(dialog, tearoff=0)
    context_menu.add_command(label="Paste", command=paste_from_clipboard)
    text_box.bind("<Button-3>", show_context_menu)

    tk.Label(dialog, text=bottom_label_text).pack(padx=10, pady=(0,10))

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=10, pady=(0,10), anchor='e')
    
    ok_button = tk.Button(button_frame, text="OK", command=on_ok, state="disabled")
    ok_button.pack(side="right", padx=(5,0))

    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side="right")

    # Start the event loop and wait for the dialog to close
    dialog.mainloop()

    return user_input


def open_review_dialog(header="Editorial Review)", 
                initial_contents=["",""],
                titles=["article","critique"], 
                link_text=None, 
                link_url=None, 
                #radio_labels=[],
                instruction_text="You can edit either the article or the critique.\n Clear the critique to use the article as displayed. ",
):
    import tkinter as tk
    from tkinter import scrolledtext
    import webbrowser
    
    def open_url():
        if link_url:
            webbrowser.open(link_url)

    def close_dialog(action='Cancel'):
        # Collect text area contents before closing
        results['body'] = text_boxes[0].get('1.0', tk.END).strip()
        results['critique'] = text_boxes[1].get('1.0', tk.END).strip() if len(text_boxes) > 1 else ''
        #results['radio'] = radio_var.get()
        results['button'] = action
        root.quit()

    root = tk.Tk()
    root.title(header)

    # Ensure the window width is at least 7 inches or fits the screen
    screen_width = root.winfo_screenwidth()
    window_width = min(screen_width, 7 * 96)  # 7 inches to pixels
    root.geometry(f"{window_width}x600")
    root.resizable(False, False)

    # Text Boxes and Labels
    text_boxes = []
    for i, (content, title) in enumerate(zip(initial_contents, titles), start=1):
        tk.Label(root, text=title).pack(fill=tk.X)
        text_box = scrolledtext.ScrolledText(root, height=15 if i == 1 else 5)
        text_box.pack(fill=tk.X, padx=10, pady=5)
        if not content:
            content=""
        text_box.insert(tk.END, content)
        text_boxes.append(text_box)
        
    if instruction_text:
        instruction_widget=tk.Label(root,text=instruction_text)
        instruction_widget.pack(fill=tk.X,padx=10,pady=10)


    # Optional Clickable Link
    if link_text and link_url:
        link_label = tk.Label(root, text=link_text, fg="blue", cursor="hand2")
        link_label.pack()
        link_label.bind("<Button-1>", lambda e: open_url())

    # OK and Cancel buttons
    tk.Button(root, text="OK", command=lambda: close_dialog('OK')).pack(side=tk.RIGHT, padx=5)
    tk.Button(root, text="Cancel", command=lambda: close_dialog('Cancel')).pack(side=tk.RIGHT)

    # A dictionary to store results
    results = {'body': '', 'critique': '',  'button': 'Cancel'}

    root.mainloop()

    # Ensure the root window is destroyed after closing the dialog and data collection
    root.destroy()

    return results

if __name__ == '__main__': #test code

    result = open_review_dialog(
        initial_contents=["Initial content for the first box", "Initial content for the second box"],
        titles=["Title 1", "Title 2"],
        link_text="Click here for more information",
        link_url="http://www.example.com",
        #radio_labels=["Option 1", "Option 2", "Option 3","Option 4"]
    )
    print (result)

    result=process_form(0,None)
    print (result)
   

    

