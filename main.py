import urllib.error
import os
from urllib.request import urlopen
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
import codeforces
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

editors_names = {
    'Atom': 'atom',
    'Brackets': 'brackets',
    'Sublime': 'subl',
    'Geany': 'geany',
    'Code::Blocks': 'codeblocks',
    'Clion': 'clion',
    'Gedit': 'gedit',
    'Visual Studio Code': 'code',
}


def group(lst, n):
    # return a list of list( of n items)
    return zip(*[lst[i::n] for i in range(n)])


c_code = '''#include<bits/stdc++.h>

using namespace std;

typedef vector<int> vi;
typedef map<string, int> mpsi;
typedef pair<int, int> pii;
typedef map<int, string> mpis;
typedef set<int> si;
typedef long long ll;
typedef unsigned long long ull;


int main (){
    // the following 2 lines are for fast input & output. For further info, please, visit: https://goo.gl/PoBEF1
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // come on, go SOLVE it..!!!
    // save your code, then use tester.py to check the test cases


    return 0;
}
'''

# raw string, so python parser doesn't alter the code or modify it

tester_code = r'''#!/usr/bin/python3
import os
import sys
from termcolor import cprint
import subprocess

dir_path = str(os.path.dirname(os.path.realpath(__file__)))
print(dir_path)

test_cases = int(open(dir_path + '/test_cases.txt', 'r').read())

input_file_names = ['in' + str(e) + '.txt' for e in range(test_cases)]
output_file_names = ['out' + str(e) + '.txt' for e in range(test_cases)]

os.system('clear')

cprint('Compiling...', 'white', attrs=['dark'])
dir_path = dir_path.replace(' ', r'\ ')

if os.system('g++ ' + dir_path + '/main.cpp -o ' + dir_path + '/a.out') == 0:  # returned 0 = successful
    os.system('clear')
    cprint('Compiled successfully...!\n', 'green', attrs=['bold'])
else:
    cprint('Compilation ERROR\n\n' + "Please, Check Your code", 'red', attrs=['bold'])
    cprint('\nPress ENTER to exit...', end='', color='white')
    input()
    sys.exit()
    # stop and close the program

ac = True

for e in range(test_cases):
    os.system(
        dir_path + '/a.out < ' + dir_path + '/' + input_file_names[e] + ' > ' + dir_path + '/my_' + output_file_names[
            e])

    cprint('Test Case {}:'.format(str(e + 1)), 'yellow')

    diff_command = subprocess.getstatusoutput(
        'diff -s -q -Z ' + dir_path + '/' + output_file_names[e] + ' ' + dir_path + '/my_' + output_file_names[e])
    # diff_command returns a tuple that contains 2 items(the exit status, command output)
    # if zero(no error), successful
    exit_status = diff_command[0]

    if not exit_status:
        cprint(' Passed', 'green')
    else:
        ac = False
        cprint(' Wrong Answer', 'red')

print()

if ac:
    cprint("ACCEPTED", 'green', attrs=['reverse', 'bold'])
else:
    cprint('Try Harder!', 'white', 'on_blue')

cprint('\nPress ANY KEY to exit...', end='', color='white')
input()

'''


def get_tags_contents(html_souped, tag_name, class_name=None):
    return [tag.contents for tag in html_souped.find_all(tag_name, class_name)]


class Parser:
    directory_name = ''
    problem_id = 0

    def __init__(self, shared_tk, shared_browser, username):
        # --- variable for path adding restriction in case of parsing more than one problem
        # to avoid adding editors' paths again
        self.robo_browser = shared_browser
        self.first_problem = True
        self.username = username

        # --- main GUI and size ---
        self.root = shared_tk
        self.root.title('CodeForces Problem Parser')
        self.root.geometry('305x300+200+200')
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

        # --- editor label ---
        label2 = Label(self.main_frame, text="Editor: ", font="Serif 10 bold")
        label2.grid(row=4, column=0, rowspan=2, sticky='sw')
        label2.config(background='white', fg='black')

        # --- editors drop down menu ---
        row_counter = 5

        self.editor_choice_name = StringVar()

        self.editor_choice_name.set(list(editors_names.keys())[
            0])  # set the default option

        drop_down_editors_menu = OptionMenu(
            self.main_frame, self.editor_choice_name, *editors_names)
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
                                   background='white', fg='black', command=self.parse_start)
        self.parse_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- Test button ---
        self.test_button = Button(self.main_frame, text="Test", font="Serif 14 bold",
                                  background='white', fg='black', command=self.tester)
        self.test_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- Submit button ---
        self.submit_button = Button(self.main_frame, text="Submit", font="Serif 14 bold",
                                    background='white', fg='black', command=self.codeforces_submit)
        self.submit_button.grid(row=row_counter, column=0, columnspan=2)
        row_counter += 1

        # --- status bar ---
        status_bar = Label(self.main_frame, text="by: Kerolloz", font="Serif 10 bold italic", bd=1, relief=SUNKEN,
                           anchor=W)
        status_bar.grid(row=row_counter, column=0,
                        columnspan=2, sticky=("N", "S", "W", "E"))
        status_bar.config(background='white', fg='black')
        row_counter += 1

        self.root.mainloop()

    def tester(self):
        """this function gets called when the Test Button is clicked"""

        if self.directory_name == '':
            messagebox.showerror(
                'Problem error', "You haven't parsed any problems yet")
            return

        command = 'python3 ' + os.getcwd() + '/' + self.directory_name + '/tester.py'
        command_run = "xterm -e 'bash -c \"" + command + "\"'"
        os.system(command_run)

    def parse_start(self):
        """this function gets called when the Parse Button is clicked"""

        main_thread = threading.Thread(target=self.start, args=())
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

    def start(self):
        link = str(self.problem_link_entry.get())

        try:
            # try reading the provided link, and if errors occur, stop
            request = urlopen(link)
        except (ValueError, urllib.error.HTTPError):
            self.reset_progressbar()
            messagebox.showerror(
                "Invalid Link", "Please, provide a valid CodeForces problem link !")
            return
        except urllib.error.URLError:
            self.reset_progressbar()
            messagebox.showerror("Error", "Connection Error!\nPlease, check the problem link or your internet "
                                          "connection.")
            return

        problem_number = re.findall("\d+", link)[0]  # get first match
        # the last letters form the link
        self.directory_name = str(problem_number) + link[-1:]
        self.directory_name = self.directory_name.replace('/', '')
        self.problem_id = self.directory_name
        # remove slash '/' form the directory name to avoid confusion
        os.chdir(str(os.path.dirname(os.path.realpath(__file__))))
        # change directory to the parse.py file dir
        # so when creating the problem folder it gets created in parse.py dir
        os.system('mkdir ' + self.directory_name)  # create a new folder
        os.chdir(self.directory_name)  # go to the problem folder

        with open('tester.py', 'w') as tester:
            tester.write(tester_code)

        with open('main.cpp', 'w') as code:
            code.write(c_code)

        # decode the bytes string to normal string, same as str(request.read())
        my_html = request.read().decode().replace(
            '<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n')
        html_souped = BeautifulSoup(my_html, 'lxml')

        input_output_list = get_tags_contents(html_souped, 'pre')
        # using regular expressions, return strings between "pre" opening and closing tags in the html code
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

        # open the code using the chosen editor
        os.system(
            editors_names[self.editor_choice_name.get()] + ' ' + self.directory_name + '/main.cpp')

    def set_state_for_all_buttons(self, state):
        self.submit_button.config(state=state)
        self.test_button.config(state=state)
        self.parse_button.config(state=state)

    def codeforces_submit(self):
        self.start_progressbar()
        # returns a tuple (first element is the last submission id)
        return_value = codeforces.CF_NOT_SUBMITTED_YET
        if self.problem_id:
            last_submit_id = codeforces.get_latest_verdict(self.username)[0]
            messagebox.showinfo('Status', 'Submitting [{1}]\nfor problem [{0}]\nin [{2}]'
                                .format(self.problem_id,
                                        self.directory_name + '/main.cpp',
                                        "GNU G++17 7.3.0"))
            return_value = codeforces.submit_problem(self.robo_browser,
                                                     'GNU G++17 7.3.0',
                                                     self.problem_id,
                                                     self.directory_name + '/main.cpp')
        if return_value == codeforces.CF_ALREADY_SUBMITTED:
            messagebox.showerror("Error", "File is already submitted before")
        elif return_value == codeforces.CF_FILE_NOT_FOUND:
            messagebox.showerror("Error", "File is not found")
        elif return_value == codeforces.CF_SUBMITTED_SUCCESSFULLY:
            messagebox.showinfo(
                "Success", "Okay submitted successfully!\nPlease Wait while Judging...")
            for verdict in codeforces.print_last_verdict_status_for_user(last_submit_id, self.username):
                messagebox.showinfo("Status", verdict)
        self.reset_progressbar()


class Login:

    def __init__(self, shared_tk):
        self.root = shared_tk
        self.main_frame = LabelFrame(
            self.root, height=500, width=500, text="Login", font="Serif")
        self.username_entry = Entry(self.main_frame)
        self.password_entry = Entry(self.main_frame, show="*")

        self.is_logged_in = False
        self.robo_browser = RoboBrowser(parser='html.parser')

        self.draw_gui()

    def draw_gui(self):
        self.root.title('CodeForces Login')
        self.root.geometry('306x167+200+200')
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
        image_label.grid(row=0, columnspan=2, rowspan=2, sticky='nsew')
        image_label.config(background='white')

        # --- username label ---
        username_label = Label(self.main_frame, text="Username: ",
                               font="Serif 10 bold")
        username_label.grid(row=2, column=0, rowspan=2, sticky='sw')
        username_label.config(background='white', fg='black')

        # ---  Problem link entry ---
        self.username_entry.grid(
            row=2, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.username_entry.config(background='white', fg='black')

        # --- password label ---
        password_label = Label(
            self.main_frame, text="Password: ", font="Serif 10 bold")
        password_label.grid(row=4, column=0, rowspan=2, sticky='sw')
        password_label.config(background='white', fg='black')

        # --- password entry ---
        self.password_entry.grid(
            row=4, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.password_entry.config(background='white', fg='black')

        # --- login button ---
        Button(self.main_frame, text="Login", command=self.codeforces_login).grid(
            row=6, column=1, columnspan=1)

        self.root.mainloop()

    def codeforces_login(self):
        if codeforces.login(self.robo_browser, str(self.username_entry.get()), str(self.password_entry.get())):
            messagebox.showinfo("Success", "Logged in successfully")
            self.is_logged_in = True
            Parser(shared_gui, self.robo_browser,
                   str(self.username_entry.get()))
        else:
            messagebox.showerror("Error", "Something went wrong")


if __name__ == '__main__':
    shared_gui = Tk()
    login_gui = Login(shared_gui)
