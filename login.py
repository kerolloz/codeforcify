import os
import tkinter as tk
from tkinter import ttk, messagebox

import codeforces_wrapper


class Login:
    username = ""
    password = ""
    api_key = ""
    api_secret = ""
    is_logged_in = False

    def __init__(self, shared_browser):
        self.root = tk.Tk()
        self.robo_browser = shared_browser
        self.root.title('CodeForces Login')
        self.root.resizable(False, False)
        style = ttk.Style()
        style.configure("TLabel", background="white", padding=3)
        style.configure("TLabelframe", background="white", padding=3)
        style.configure("TLabelframe.Label", background="white")
        style.configure("TEntry", padding=3)

        main_frame = ttk.LabelFrame(
            self.root, text="Login")

        current_file_path = os.path.dirname(os.path.realpath(__file__))
        codeforces_image = tk.PhotoImage(
            file=current_file_path + '/codeforces-logo.png')

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

        labels = ["Username", "Password", "API Key", "API Secret"]
        entries = [self.username_entry, self.password_entry, self.api_key_entry, self.api_secret_entry]

        for i in range(len(labels)):
            ttk.Label(main_frame, text=labels[i]).pack()
            entries[i].pack()
            entries[i].bind("<Return>", self.codeforces_login)

        self.login_button.pack(pady=30)

        self.username_entry.focus()

        by_kerolloz_bar = ttk.Label(
            main_frame, text="by: Kerolloz", relief=tk.SUNKEN)
        by_kerolloz_bar.pack(expand=1, fill="both")

        self.root.mainloop()

    def codeforces_login(self, _=None):
        self.login_button.config(text="Please wait..", state=tk.DISABLED)
        self.root.update()
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.api_key = self.api_key_entry.get()
        self.api_secret = self.api_secret_entry.get()
        if codeforces_wrapper.login(self.robo_browser, self.username, self.password):
            tk.messagebox.showinfo("Success", "Logged in successfully")
            self.is_logged_in = True
            self.root.destroy()  # destroy the login window
        else:
            self.login_button.config(text="Login", state=tk.NORMAL)
            tk.messagebox.showerror("Error", "Something went wrong")
