import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

import codeforces_wrapper


class Login:

    def __init__(self, shared_browser):
        self.user_data = None

        self.root = tk.Tk()
        self.robo_browser = shared_browser
        self.root.title('CodeForces Login')
        self.root.resizable(False, False)

        style = ttk.Style()
        style.configure("TLabel", background="white", padding=3)
        style.configure("TLabelframe", background="white", padding=3)
        style.configure("TLabelframe.Label", background="white")
        style.configure("TEntry", padding=3)

        main_frame = ttk.LabelFrame(self.root, text="Login")

        current_file_path = os.path.dirname(os.path.realpath(__file__))
        codeforces_image = tk.PhotoImage(file=current_file_path + '/codeforces-logo.png')

        image_label = ttk.Label(main_frame)
        image_label.config(image=codeforces_image)

        main_frame.pack()
        image_label.pack()

        self.username_entry = ttk.Entry(main_frame)
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.api_key_entry = ttk.Entry(main_frame)
        self.api_secret_entry = ttk.Entry(main_frame)
        self.login_button = ttk.Button(
            main_frame, text="Login", command=self.codeforces_login)

        self.labels = ["Username", "Password", "API Key", "API Secret"]
        self.entries = [self.username_entry, self.password_entry, self.api_key_entry, self.api_secret_entry]

        for i in range(len(self.labels)):
            ttk.Label(main_frame, text=self.labels[i]).pack()
            self.entries[i].pack()
            self.entries[i].bind("<Return>", self.codeforces_login)

        self.should_remember_me = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Remember Me", variable=self.should_remember_me).pack()

        self.login_button.pack(pady=30)

        self.username_entry.focus()

        by_kerolloz_bar = ttk.Label(
            main_frame, text="by: Kerolloz", relief=tk.SUNKEN)
        by_kerolloz_bar.pack(expand=1, fill="both")

        self.load_user_data_from_file()
        self.root.mainloop()

    def user_data_to_dictionary(self):
        d = {}
        for i in range(len(self.labels)):
            key = "_".join(self.labels[i].lower().split())  # to lower case && space to _
            d[key] = self.entries[i].get()
        return d

    def save_user_data_to_file(self):
        with open('.user_data.json', 'w') as f:
            json.dump(self.user_data, f)

    def load_user_data_from_file(self):
        if os.path.exists(".user_data.json"):
            try:
                with open('.user_data.json') as f:
                    self.user_data = json.load(f)
                    self.username_entry.insert(0, self.user_data['username'])
                    self.password_entry.insert(0, self.user_data['password'])
                    self.api_key_entry.insert(0, self.user_data['api_key'])
                    self.api_secret_entry.insert(0, self.user_data['api_secret'])
                    self.codeforces_login()
            except FileNotFoundError:
                print("No previous saved login user data")

    def codeforces_login(self, _=None):
        self.login_button.config(text="Please wait..", state=tk.DISABLED)
        self.root.update()
        self.user_data = self.user_data_to_dictionary()
        if self.should_remember_me.get():
            self.save_user_data_to_file()
        if codeforces_wrapper.login(self.robo_browser, self.user_data):
            tk.messagebox.showinfo("Success", "Logged in successfully")
            self.root.destroy()  # destroy the login window
        else:
            self.login_button.config(text="Login", state=tk.NORMAL)
            tk.messagebox.showerror("Error", "Something went wrong")
