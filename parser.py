import json
import shutil
import os
import threading
import codeforces

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from bs4 import BeautifulSoup


class Parser:
    directory_name = ''
    problem_id = 0

    def __init__(self, shared_tk, logged_in_browser, username):
        # --- variable for path adding restriction in case of parsing more than one problem
        # to avoid adding editors' paths again
        self.robo_browser = logged_in_browser
        self.first_problem = True
        self.username = username
        self.problem_link = None

        # Load the editors from editors.json
        data_file_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "editors.json")
        with open(data_file_path, "r", encoding="utf-8") as file:
            self.editor_run_command = json.load(file)

        # --- main GUI and size ---
        self.root = shared_tk
        self.root.title('CodeForces Problem Parser')
        self.root.resizable(False, False)
        # self.root.iconbitmap('app_icon.ico')  # window icon

        # --- main Frame ---
        self.main_frame = LabelFrame(
            self.root, height=400, width=400, text="Parser", font="Serif")
        self.main_frame.grid(row=0, column=0)
        self.main_frame.config(background='white', fg='black')

        # --- CF image object ---
        current_file_path = os.path.dirname(os.path.realpath(__file__))
        codeforces_image = PhotoImage(
            file=current_file_path + '/codeforces-logo.png')

        # --- CF image label ---
        image_label = Label(self.main_frame)
        image_label.config(image=codeforces_image)
        image_label.grid(row=0, columnspan=2, rowspan=2, sticky='nsew')
        image_label.config(background='white')

        # --- progress bar variable ---
        self.progress = DoubleVar()
        self.progress.set(0.0)

        # --- problem link label ---
        label1 = Label(self.main_frame, text="Problem Link: ",
                       font="Serif 10 bold")
        label1.grid(row=2, column=0, rowspan=2, sticky='sw')
        label1.config(background='white', fg='black')

        # ---  Problem link entry ---
        self.problem_link_entry = Entry(self.main_frame)
        self.problem_link_entry.grid(
            row=2, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.problem_link_entry.config(background='white', fg='black')
        self.problem_link_entry.focus()

        # --- editor label ---
        label2 = Label(self.main_frame, text="Editor: ", font="Serif 10 bold")
        label2.grid(row=4, column=0, rowspan=2, sticky='sw')
        label2.config(background='white', fg='black')

        # --- editors drop down menu ---
        row_counter = 5

        self.editor_choice_name = StringVar()

        self.editor_choice_name.set(list(self.editor_run_command.keys())[
                                        0])  # set the default option

        drop_down_editors_menu = OptionMenu(
            self.main_frame, self.editor_choice_name, *self.editor_run_command)
        drop_down_editors_menu.grid(row=row_counter, column=1, rowspan=2)

        row_counter += 2

        # --- progressbar ---
        self.progressbar = ttk.Progressbar(self.main_frame, orient=HORIZONTAL, length=200, mode='indeterminate',
                                           maximum=100, variable=self.progress)
        self.progressbar.grid(row=row_counter, column=0,
                              columnspan=2, sticky=("N", "S", "W", "E"))
        row_counter += 1

        # --- parse button ---
        self.parse_button = Button(self.main_frame, text="Parse", font="Serif 14 bold",
                                   background='white', fg='black', command=self.parser)
        self.parse_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- Test button ---
        self.test_button = Button(self.main_frame, text="Test", font="Serif 14 bold",
                                  background='white', fg='black', command=self.tester)
        self.test_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- show output checkbox ---
        self.should_show_output = BooleanVar()
        self.show_output_checkbox = Checkbutton(self.main_frame, text="Show Output", variable=self.should_show_output)
        self.show_output_checkbox.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- Submit button ---
        self.submit_button = Button(self.main_frame, text="Submit", font="Serif 14 bold",
                                    background='white', fg='black', command=self.codeforces_submit)
        self.submit_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- Remove files button ---
        self.remove_files_button = Button(self.main_frame, text="Remove Files", font="Serif 14 bold",
                                          background='white', fg='black', command=self.remove_parsed_problem_files)
        self.remove_files_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 5

        # --- status bar ---

        self.status_bar = Label(self.main_frame, text="\nStatus: Ok\n", font="Serif 10 bold")
        self.status_bar.grid(row=row_counter, column=0, columnspan=2, sticky=("N", "S", "W", "E"))
        self.status_bar.config(background='white', fg='black')
        row_counter += 5

        # --- by kerolloz ---

        by_kerolloz_bar = Label(self.main_frame, text="by: Kerolloz", font="Serif 10 bold italic", bd=1, relief=SUNKEN,
                                anchor=W)
        by_kerolloz_bar.grid(row=row_counter, column=0,
                             columnspan=2, sticky=("N", "S", "W", "E"))
        by_kerolloz_bar.config(background='white', fg='black')
        row_counter += 1

        self.root.geometry('{width}x{height}+{x}+{y}'.format(width=305, height=20+(row_counter*17), x=200, y=200))

        self.root.mainloop()

    def start_testing(self):
        """This function starts the command line tester"""
        self.start_progressbar()
        command = 'python3 {0}/{1}/tester.py {2}'.format(os.getcwd(), self.directory_name,
                                                         str(self.should_show_output.get()))
        command_run = "x-terminal-emulator -e 'bash -c \"" + command + "\"'"
        os.system(command_run)
        self.reset_progressbar()

    def tester(self):
        """this function gets called when the Test Button is clicked"""

        if self.directory_name == '':
            messagebox.showerror(
                'Problem error', "You haven't parsed any problems yet")
            return

        self.start_progressbar()
        threading.Thread(target=self.start_testing).start()
        self.reset_progressbar()

    def parser(self):
        """this function gets called when the Parse Button is clicked"""

        main_thread = threading.Thread(target=self.start_parsing, args=())
        # start the threads to work simultaneously
        self.start_progressbar()
        main_thread.start()

    def start_progressbar(self):
        self.set_state_for_all_buttons(DISABLED)
        # create a thread for the progressbar, thread for the main program "parser"
        progress_speed = 8  # progressbar running speed
        progressbar_thread = threading.Thread(
            target=self.progressbar.start(progress_speed), args=())
        progressbar_thread.start()

    def reset_progressbar(self):
        self.progress.set(0.0)
        self.progressbar.stop()
        self.set_state_for_all_buttons(NORMAL)

    def start_parsing(self):
        self.problem_link = str(self.problem_link_entry.get())

        if not codeforces.is_a_valid_problem_link(self.problem_link):
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
        os.chdir(str(os.path.dirname(os.path.realpath(__file__))))
        # change directory to the parse.py file dir
        # so when creating the problem folder it gets created in parse.py dir
        os.system("mkdir " + self.directory_name)  # create a new folder

        shutil.copyfile('utils/tester.py', self.directory_name + '/tester.py')
        shutil.copyfile('utils/template.cpp', self.directory_name + '/main.cpp')

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
            with open('in' + str(index) + '.txt', 'w') as in_file:
                input_content = ''.join(test[0]).strip()
                in_file.write(input_content)
            with open('out' + str(index) + '.txt', 'w') as out_file:
                output = ''.join(test[1]).strip()
                out_file.write(output)
            index += 1

        with open('test_cases.txt', 'w') as f:
            f.write(str(index))

        os.chdir('..')  # go to the previous directory "parse.py" directory

        self.reset_progressbar()

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
            self.set_status_bar_to("Status: Problem Files\nare Deleted\nSuccessfully!")
        else:
            messagebox.showerror("Error", "You haven't parsed any problems yet!")

    def codeforces_submit(self):
        self.set_state_for_all_buttons(DISABLED)
        return_value = codeforces.CF_NOT_SUBMITTED_YET
        last_submit_id = None
        if self.problem_id:
            self.set_status_bar_to("\nStatus: getting last submission id\n")
            # returns a tuple (first element is the last submission id)
            last_submit_id = codeforces.get_latest_verdict(self.username)[0]

            status = 'Submitting [{1}]\nfor problem [{0}]\nin [{2}]' \
                .format(self.problem_id,
                        self.directory_name + '/main.cpp',
                        "GNU G++17 7.3.0")
            self.set_status_bar_to(status)

            return_value = codeforces.submit_solution_to_problem(self.robo_browser,
                                                                 'GNU G++17 7.3.0',
                                                                 self.problem_link,
                                                                 self.directory_name + '/main.cpp')
        if return_value == codeforces.CF_ALREADY_SUBMITTED:
            messagebox.showerror("Error", "File is already submitted before")

        elif return_value == codeforces.CF_FILE_NOT_FOUND:
            messagebox.showerror("Error", "File is not found")

        elif return_value == codeforces.CF_NOT_REGISTERED:
            messagebox.showerror("Error", "You cannot submit, maybe you are not registered!")

        elif return_value == codeforces.CF_SUBMITTED_SUCCESSFULLY:
            status = "Okay submitted successfully!\nPlease Wait while Judging...\n"
            self.set_status_bar_to(status)
            for verdict in codeforces.get_last_verdict_status_for_user(last_submit_id, self.username):
                self.set_status_bar_to(verdict)

            messagebox.showinfo("Verdict", verdict)

        self.set_status_bar_to("\nStatus: Ok\n")
        self.set_state_for_all_buttons(NORMAL)

    def set_status_bar_to(self, status):
        self.status_bar['text'] = status
        self.root.update()


# Helpful functions
def group(lst, n):
    """returns a list of list( of n items)"""
    return zip(*[lst[i::n] for i in range(n)])


def get_tags_contents(html_souped, tag_name, class_name=None):
    """This function returns all the tags contents in a souped html"""
    return [tag.contents for tag in html_souped.find_all(tag_name, class_name)]
