import os
import codeforces_wrapper

from tkinter import *
from tkinter import messagebox


class Login:

    def __init__(self, shared_tk, shared_browser):
        self.root = shared_tk
        self.main_frame = LabelFrame(
            self.root, height=500, width=500, text="Login", font="Serif")

        self.username_entry = Entry(self.main_frame)
        self.password_entry = Entry(self.main_frame, show="*")
        self.api_key_entry = Entry(self.main_frame)
        self.api_secret_entry = Entry(self.main_frame)

        self.login_button = Button(self.main_frame, text="Login", command=self.codeforces_login)

        self.is_logged_in = False
        self.robo_browser = shared_browser

        self.draw_gui()

    def draw_gui(self):
        self.root.title('CodeForces Login')
        self.root.geometry('306x235+200+200')
        self.root.resizable(False, False)

        # --- main Frame ---
        self.main_frame.grid(row=0, column=0)
        self.main_frame.config(background='white', fg='black')

        # --- CF image object ---
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        codeforces_image = PhotoImage(
            file=current_file_path + '/codeforces-logo.png')

        # --- CF image label ---
        image_label = Label(self.main_frame)
        image_label.config(image=codeforces_image)
        image_label.grid(row=0, columnspan=3, rowspan=2, sticky='nsew')
        image_label.config(background='white')
        row_counter = 2

        # --- username label ---
        username_label = Label(self.main_frame, text="Username: ",
                               font="Serif 10 bold")
        username_label.grid(row=row_counter, column=0, rowspan=2, sticky='sw')
        username_label.config(background='white', fg='black')

        # ---  Problem link entry ---
        self.username_entry.grid(
            row=row_counter, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.username_entry.config(background='white', fg='black')
        self.username_entry.bind("<Return>", self.codeforces_login)
        self.username_entry.focus()
        row_counter += 2

        # --- password label ---
        password_label = Label(
            self.main_frame, text="Password: ", font="Serif 10 bold")
        password_label.grid(row=row_counter, column=0, rowspan=2, sticky='sw')
        password_label.config(background='white', fg='black')

        # --- password entry ---
        self.password_entry.grid(
            row=row_counter, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.password_entry.config(background='white', fg='black')
        self.password_entry.bind("<Return>", self.codeforces_login)
        row_counter += 2

        # --- api key label ---
        api_key_label = Label(
            self.main_frame, text="API Key: ", font="Serif 10 bold")
        api_key_label.grid(row=row_counter, column=0, rowspan=2, sticky='sw')
        api_key_label.config(background='white', fg='black')

        # --- api key entry ---

        self.api_key_entry.grid(
            row=row_counter, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.api_key_entry.config(background='white', fg='black')
        row_counter += 2

        # --- api secret label ---

        api_secret_label = Label(
            self.main_frame, text="API Secret: ", font="Serif 10 bold")
        api_secret_label.grid(row=row_counter, column=0, rowspan=2, sticky='sw')
        api_secret_label.config(background='white', fg='black')

        # --- api secret entry ---
        self.api_secret_entry.grid(
            row=row_counter, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.api_secret_entry.config(background='white', fg='black')
        self.api_secret_entry.bind("<Return>", self.codeforces_login)
        row_counter += 2

        # --- login button ---
        self.login_button.grid(row=row_counter, column=1, columnspan=2)
        row_counter += 1

        # --- by kerolloz ---
        by_kerolloz_bar = Label(self.main_frame, text="by: Kerolloz", font="Serif 10 bold italic", bd=1, relief=SUNKEN,
                                anchor=W)
        by_kerolloz_bar.grid(row=row_counter, column=0,
                             columnspan=3, sticky=("N", "S", "W", "E"))
        by_kerolloz_bar.config(background='white', fg='black')

        self.root.mainloop()

    def codeforces_login(self, event=None):
        self.login_button.config(text="Please wait..", state=DISABLED)
        self.root.update()

        if codeforces_wrapper.login(self.robo_browser, str(self.username_entry.get()), str(self.password_entry.get())):
            messagebox.showinfo("Success", "Logged in successfully")
            self.is_logged_in = True
            self.root.quit()  # closes the login window
        else:
            self.login_button.config(text="Login", state=NORMAL)
            messagebox.showerror("Error", "Something went wrong")

    def get_username(self):
        return str(self.username_entry.get())

    def get_api_key(self):
        return str(self.api_key_entry.get())

    def get_api_secret(self):
        return str(self.api_secret_entry.get())
