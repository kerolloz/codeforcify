import json
import os
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from bs4 import BeautifulSoup

import codeforces_wrapper


class Parser:

    def __init__(self, logged_in_browser, user_data: dict):
        self.directory_name = ''
        self.problem_id = 0
        self.robo_browser = logged_in_browser
        self.problem_link = None
        self.username, _, self.api_key, self.api_secret = user_data

        self.current_file_path = os.path.dirname(os.path.realpath(__file__))

        # Load the editors from editors.json
        data_file_path = os.path.join(self.current_file_path, "editors.json")
        with open(data_file_path, "r", encoding="utf-8") as file:
            self.editor_run_command = json.load(file)

        # --- main GUI and styling ---
        self.root = tk.Tk()
        self.root.title('CodeForces Problem Parser')
        self.root.resizable(False, False)
        # self.root.iconbitmap('app_icon.ico')  # window icon

        style = ttk.Style()
        style.configure("TLabel", background="white", padding=3)
        style.configure("TLabelframe", background="white", padding=3)
        style.configure("TLabelframe.Label", background="white")
        style.configure("TEntry", padding=3)
        style.configure("TButton", background="white")

        # --- main Frame ---
        self.main_frame = ttk.LabelFrame(self.root, text="Parser")
        self.main_frame.pack()

        # --- CF image object ---

        codeforces_image = tk.PhotoImage(
            file=self.current_file_path + '/codeforces-logo.png')

        # --- CF image label ---
        image_label = ttk.Label(self.main_frame)
        image_label.config(image=codeforces_image)
        image_label.pack()

        # --- progress bar variable ---
        self.progress = tk.DoubleVar()
        self.progress.set(0.0)

        # --- problem link label ---
        ttk.Label(self.main_frame, text="Problem Link").pack()

        # ---  Problem link entry ---
        self.problem_link_entry = ttk.Entry(self.main_frame)
        self.problem_link_entry.pack(pady=5)

        self.problem_link_entry.bind("<Return>", lambda x: self.parse())
        self.problem_link_entry.focus()

        # --- editor label ---
        ttk.Label(self.main_frame, text="Editor").pack()

        # --- editors drop down menu ---

        self.editor_choice_name = tk.StringVar()

        self.editor_choice_name.set(list(self.editor_run_command.keys())[
                                        0])  # set the default option

        # --- Drop down editors menu 
        ttk.OptionMenu(self.main_frame, self.editor_choice_name, *self.editor_run_command).pack(pady=5)

        # --- progressbar ---
        self.progressbar = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate',
                                           maximum=100, variable=self.progress)
        self.progressbar.pack(expand=1, fill="both", pady=5)

        # --- parse button ---
        self.parse_button = ttk.Button(self.main_frame, text="Parse",
                                       command=self.parse)
        self.parse_button.pack(pady=5)

        # --- Test button ---
        self.test_button = ttk.Button(self.main_frame, text="Test",
                                      command=self.tester)
        self.test_button.pack(pady=5)

        # --- show output checkbox ---
        self.should_show_output = tk.BooleanVar()
        self.show_output_checkbox = ttk.Checkbutton(self.main_frame, text="Show Output",
                                                    variable=self.should_show_output)
        self.show_output_checkbox.pack(pady=5)

        # --- Submit button ---
        self.submit_button = ttk.Button(self.main_frame, text="Submit",
                                        command=self.submit)
        self.submit_button.pack(pady=5)

        # --- Remove files button ---
        self.remove_files_button = ttk.Button(self.main_frame, text="Remove Files",
                                              command=self.remove_parsed_problem_files)
        self.remove_files_button.pack(pady=5)

        # --- status bar ---

        self.status_bar = ttk.Label(self.main_frame, text="\nStatus: Ok\n", )
        self.status_bar.pack(pady=5)

        # --- by kerolloz ---
        ttk.Label(
            self.main_frame, text="by: Kerolloz", relief=tk.SUNKEN).pack(expand=1, fill="both")

        self.root.mainloop()

    def start_testing(self):
        """This function starts the command line tester"""
        self.start_progressbar()
        should_show_output = "TRUE" if self.should_show_output.get() else ""
        command = 'python3 %s/%s/tester.py %s' % (os.getcwd(), self.directory_name,
                                                  should_show_output)
        subprocess.getstatusoutput("x-terminal-emulator -e '%s'" % command)

        self.reset_progressbar()

    def tester(self):
        """this function gets called when the Test ttk.Button is clicked"""

        if self.directory_name == '':
            tk.messagebox.showerror(
                'Problem error', "You haven't parsed any problems yet")
            return

        self.start_progressbar()
        threading.Thread(target=self.start_testing).start()
        self.reset_progressbar()

    def parse(self):
        """This function gets called when the Parse ttk.Button is clicked or
        Enter is pressed in the problem link entry"""

        main_thread = threading.Thread(target=self._parse)
        # start the threads to work simultaneously
        self.start_progressbar()
        main_thread.start()

    def start_progressbar(self):
        self.set_state_for_all_buttons(tk.DISABLED)
        # create a thread for the progressbar, thread for the main program "parser"
        progress_speed = 8  # progressbar running speed
        progressbar_thread = threading.Thread(
            target=self.progressbar.start(progress_speed), args=())
        progressbar_thread.start()

    def reset_progressbar(self):
        self.progress.set(0.0)
        self.progressbar.stop()
        self.set_state_for_all_buttons(tk.NORMAL)

    def _parse(self):
        self.problem_link = self.problem_link_entry.get()

        if not codeforces_wrapper.is_a_valid_problem_link(self.problem_link):
            self.reset_progressbar()
            messagebox.showerror('Invalid link', 'This is NOT a valid codeforces problem link!')
            return

        try:
            self.robo_browser.open(self.problem_link, timeout=10)
            self.set_status_bar_to("\nStatus: Opening problem link..\n")

        except Exception:
            self.reset_progressbar()
            messagebox.showerror('Connection TimeOut', 'Check your internet connection or the problem link')
            return

        self.set_status_bar_to("\nStatus: Preparing problem's files..\n")

        problem_number = re.findall(r"\d+", self.problem_link)[-1]  # get last match
        # the last letters form the link
        self.directory_name = str(problem_number) + self.problem_link[-1:]
        self.directory_name = self.directory_name.replace('/', '')
        self.problem_id = self.directory_name
        # remove slash '/' form the directory name to avoid confusion
        os.chdir(self.current_file_path)
        # change directory to the parse.py file dir
        # so when creating the problem folder it gets created in parse.py dir
        os.makedirs(self.directory_name, exist_ok=True)  # create a new folder

        shutil.copy('utils/tester.py', self.directory_name)
        shutil.copy('utils/template.cpp', self.directory_name)

        os.chdir(self.directory_name)  # go to the problem folder

        self.set_status_bar_to("\nStatus: Extracting test cases..\n")

        my_html = str(self.robo_browser.select('pre')).replace(
            '<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n')
        html_souped = BeautifulSoup(my_html, features="html.parser")

        input_output_list = get_tags_contents(html_souped, 'pre')
        # using BeautifulSoup, return strings between "pre" tags
        # "pre" is the tag that contains test cases, whether input or output

        input_output_group = group(input_output_list, 2)
        test_cases = list(input_output_group)

        index = 0
        for test in test_cases:
            with open('in' + str(index), 'w') as in_file:
                input_content = ''.join(test[0]).strip()
                in_file.write(input_content)
            with open('out' + str(index), 'w') as out_file:
                output = ''.join(test[1]).strip()
                out_file.write(output)
            index += 1

        with open('test_cases', 'w') as f:
            f.write(str(index))

        os.chdir('..')  # go to the previous directory "parse.py" directory

        self.reset_progressbar()

        self.set_status_bar_to("\nStatus: Opening your editor\n")
        messagebox.showinfo(
            'CF Parser', 'Problem has been parsed Successfully!')

        self.set_status_bar_to("\nStatus: Ok\n")

        # open the code using the chosen editor
        os.system(
            self.editor_run_command[self.editor_choice_name.get()] + ' ' + self.directory_name + '/main.cpp')

    def set_state_for_all_buttons(self, state):
        self.submit_button.config(state=state)
        self.test_button.config(state=state)
        self.parse_button.config(state=state)
        self.remove_files_button.config(state=state)

    def remove_parsed_problem_files(self):
        if self.directory_name:
            os.system("rm -r " + self.directory_name)
            self.set_status_bar_to("Status: Problem Files\nHave Been Deleted\nSuccessfully!")
        else:
            messagebox.showerror("Error", "You haven't parsed any problems yet!")

    def submit(self):
        self.set_state_for_all_buttons(tk.DISABLED)
        return_value = codeforces_wrapper.CF_NOT_SUBMITTED_YET
        last_submit_id = None
        if self.problem_id:
            self.set_status_bar_to("\nStatus: getting last submission id\n")
            # returns a tuple (first element is the last submission id)
            last_submit_id = codeforces_wrapper.get_latest_verdict(self.api_key, self.api_secret, self.username).id

            status = 'Submitting [{1}]\nfor problem [{0}]\nin [{2}]' \
                .format(self.problem_id,
                        self.directory_name + '/main.cpp',
                        "GNU G++17 7.3.0")
            self.set_status_bar_to(status)

            return_value = codeforces_wrapper.submit_solution_to_problem(self.robo_browser,
                                                                         'GNU G++17 7.3.0',
                                                                         self.problem_link,
                                                                         self.directory_name + '/main.cpp')
        if return_value == codeforces_wrapper.CF_ALREADY_SUBMITTED:
            messagebox.showerror("Error", "File is already submitted before")

        elif return_value == codeforces_wrapper.CF_FILE_NOT_FOUND:
            messagebox.showerror("Error", "File is not found")

        elif return_value == codeforces_wrapper.CF_NOT_REGISTERED:
            messagebox.showerror("Error", "You cannot submit, maybe you are not registered!")

        elif return_value == codeforces_wrapper.CF_SUBMITTED_SUCCESSFULLY:
            status = "Okay submitted successfully!\nPlease Wait while Judging...\n"
            self.set_status_bar_to(status)
            verdict = None
            for verdict in codeforces_wrapper.get_last_verdict_status_for_user(last_submit_id, self.username,
                                                                               self.api_key, self.api_secret):
                self.set_status_bar_to(verdict)

            messagebox.showinfo("Verdict", verdict)

        self.set_status_bar_to("\nStatus: Ok\n")
        self.set_state_for_all_buttons(tk.NORMAL)

    def set_status_bar_to(self, status):
        self.status_bar['text'] = status
        self.root.update()


# Helpful functions
def group(lst, n):
    """returns a list of list( of n items)"""
    return zip(*[lst[i::n] for i in range(n)])


def get_tags_contents(souped_html, tag_name, class_name=None):
    """This function returns all the tags contents in a souped html"""
    return [tag.contents for tag in souped_html.find_all(tag_name, class_name)]
