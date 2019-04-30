from tkinter import *
from utils import *
import webbrowser

window = Tk()
window.title("UIC Search Engine")
window.geometry('800x800')

welcome = Label(window, text="Welcome to UIC Search Engine, Please enter your query below!")
welcome.pack()

txt = Entry(window, width=60)
txt.pack()

inverted_index = get_data_from_pickle("inverted_index")
idf_scores = get_data_from_pickle("idf_scores")
scores = get_data_from_pickle("scores")
mappings = extract_mapping('mapping.txt')


def callback(event):
    webbrowser.open_new(event.widget.cget('text'))


def clear():
    children = window.winfo_children()
    for child in children:
        if str(type(child)) == "<class 'tkinter.Frame'>":
            child.destroy()
    frame = Frame(window)
    return frame


def clicked():
    frame = clear()
    query = txt.get()
    parsed_query = preprocess_queries(query)
    query_scores = calculate_tfidf_queries(parsed_query, idf_scores)
    results = rank_results(parsed_query, inverted_index, scores, query_scores)
    links = get_links_from_ranked_pages(results, mappings)
    if len(links) == 0:
        link = Label(frame, text="No results found!")
        link.pack()
    else:
        lim = 10
        if len(links) < 10:
            lim = len(links)
        for i in range(lim):
            link = Label(frame, text=(links[i]), fg='blue', cursor='hand2')
            link.pack()
            link.bind("<Button-1>", callback)
    frame.pack()


def expand_search():
    frame = clear()
    query = txt.get()
    expanded_query = expand_query(query)
    parsed_query = preprocess_queries(expanded_query)
    query_scores = calculate_tfidf_queries(parsed_query, idf_scores)
    results = rank_results(parsed_query, inverted_index, scores, query_scores)
    links = get_links_from_ranked_pages(results, mappings)
    if len(links) == 0:
        link = Label(frame, text="No results found!")
        link.pack()
    else:
        lim = 10
        if len(links) < 10:
            lim = len(links)
        for i in range(lim):
            link = Label(frame, text=(links[i]), fg='blue', cursor='hand2')
            link.pack()
            link.bind("<Button-1>", callback)
    frame.pack()

btn = Button(window, text='Search', command=clicked)
btn.pack()

btn = Button(window, text="Search expanded", command=expand_search)
btn.pack()

window.mainloop()
