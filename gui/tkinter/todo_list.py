from tkinter import *
import tkinter as tk


class ToDoItem:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class ToDoListApp:
    def __init__(self, root):
        root.title("To Do List")
        frame = Frame(root, borderwidth=2, relief="sunken")
        frame.grid(column=1, row=1, sticky=(N, E, S, W))
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        # To Do Items list
      
        list_label = Label(frame, text="To Do Items")
        list_label.grid(column=1, row=1, sticky=(S, W))
      
        self.to_do_items = [
            ToDoItem("Workout", "Push ups, pull ups, squats"),
            ToDoItem("House work", "Clean kitchen, sweep floors, do laundry"),
            ToDoItem("Groceries", "Buy bread, milk, eggs"),
        ]
      
        self.to_do_names = StringVar(value=list(map(lambda x: x.name, self.to_do_items)))
        items_list = Listbox(frame, listvariable=self.to_do_names)
        items_list.bind("<<ListboxSelect>>", lambda s: self.select_item(items_list.curselection()))
        items_list.grid(column=1, row=2, sticky=(E, W), rowspan=5)
        self.selected_description = StringVar()
        selected_description_label = Label(frame, textvariable=self.selected_description, wraplength=200)
        selected_description_label.grid(column=1, row=7, sticky=(E, W))
      
        # New Item
        new_item_label = Label(frame, text="New Item")
        new_item_label.grid(column=2, row=1, sticky=(S, W))
      
        name_label = Label(frame, text="Item name")
        name_label.grid(column=2, row=2, sticky=(S, W))
        self.name = StringVar()
      
        name_entry = Entry(frame, textvariable=self.name)
        name_entry.grid(column=2, row=3, sticky=(N, E, W))
      
        description_label = Label(frame, text="Item description")
        description_label.grid(column=2, row=4, sticky=(S, W))
        self.description = StringVar()
      
        description_entry = Entry(frame, textvariable=self.description)
        description_entry.grid(column=2, row=5, sticky=(N, E, W))
      
        save_button = Button(frame, text="Save", command=self.save_item)
        save_button.grid(column=2, row=6, sticky=(E))
      
        for child in frame.winfo_children():
            child.grid_configure(padx=10, pady=5)

  
    def save_item(self):
        name = self.name.get()
        description = self.description.get()
        new_item = ToDoItem(name, description)
        self.to_do_items.append(new_item)
        self.to_do_names.set(list(map(lambda x: x.name, self.to_do_items)))

  
    def select_item(self, index):
        selected_item = self.to_do_items[index[0]]
        self.selected_description.set(selected_item.description)


root = Tk()
ToDoListApp(root)
root.mainloop()
