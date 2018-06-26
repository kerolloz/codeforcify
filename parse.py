#!/usr/bin/python3
import os
import urllib.error
from urllib.request import urlopen
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading

editors_list = ['atom', 'brackets', 'subl', 'geany', 'codeblocks']


def group(lst, n):
    return zip(*[lst[i::n] for i in range(n)])


c_code = '''#include<bits/stdc++.h>

using namespace std;

typedef vector<int> vi;
typedef map<string, int> mpsi;
typedef pair<int, int> pii;
typedef map<int, string> mpis;
typedef set<int> si;
typedef long long int ll;


int main (){
    // the following 2 lines are for fast input & output. For further info, please, visit: https://goo.gl/PoBEF1
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // come on, go SOLVE it..!!!
    // save your code, then use tester.exe to check the test cases


    return 0;
}
'''


class Gui:
    def __init__(self):
        # --- variable for path adding restriction in case of parsing more than one problem
        # to avoid adding editors' paths again
        self.first_problem = True

        # --- main GUI and size ---
        self.root = Tk()
        self.root.title('CodeForces Problem Parser')
        self.root.geometry('310x340+200+200')
        self.root.resizable(False, False)
        # self.root.iconbitmap('app_icon.ico')  # window icon

        # --- main Frame ---
        self.main_frame = LabelFrame(self.root, height=400, width=400, text="Parser", font="Serif")
        self.main_frame.grid(row=0, column=0)
        self.main_frame.config(background='white')

        # --- CF image object ---
        codeforces_image = PhotoImage(file='codeforces-logo.png')

        # --- CF image label ---
        image_label = Label(self.main_frame)
        image_label.config(image=codeforces_image)
        image_label.grid(row=0, columnspan=2, rowspan=2, sticky='nsew')
        image_label.config(background='white')

        # --- progress bar variable ---
        self.progress = DoubleVar()
        self.progress.set(0.0)

        # --- chosen editor variable ---
        self.editor_choice = IntVar()
        self.editor_choice.set(0)

        # --- problem link label ---
        label1 = Label(self.main_frame, text="Problem Link: ", font="Serif 10 bold")
        label1.grid(row=2, column=0, rowspan=2, sticky='sw')
        label1.config(background='white')

        # ---  Problem link entry ---
        self.problem_link_entry = Entry(self.main_frame)
        self.problem_link_entry.grid(row=2, column=1, columnspan=2, sticky=("N", "S", "W", "E"))
        self.problem_link_entry.config(background='white')

        # --- editor label ---
        label2 = Label(self.main_frame, text="Editor: ", font="Serif 10 bold")
        label2.grid(row=4, column=0, rowspan=2, sticky='sw')
        label2.config(background='white')

        # --- editors_list' radio buttons ---
        Radiobutton(self.main_frame, text="Atom", font="Serif", variable=self.editor_choice, value=0).grid(row=5,
                                                                                                           column=1,
                                                                                                           sticky=W)
        Radiobutton(self.main_frame, text="Brackets", font="Serif", variable=self.editor_choice, value=1).grid(row=6,
                                                                                                               column=1,
                                                                                                               sticky=W)
        Radiobutton(self.main_frame, text="Sublime", font="Serif", variable=self.editor_choice, value=2).grid(row=7,
                                                                                                              column=1,
                                                                                                              sticky=W)
        Radiobutton(self.main_frame, text="Geany", font="Serif", variable=self.editor_choice, value=3).grid(row=8,
                                                                                                            column=1,
                                                                                                            sticky=W)
        Radiobutton(self.main_frame, text="Code::Blocks", font="Serif", variable=self.editor_choice, value=4).grid(
            row=9, column=1, sticky=W)

        # --- progressbar ---
        self.progressbar = ttk.Progressbar(self.main_frame, orient=HORIZONTAL, length=200, mode='indeterminate',
                                           maximum=100, variable=self.progress)
        self.progressbar.grid(row=10, column=0, columnspan=2, sticky=("N", "S", "W", "E"))

        # --- parse button ---
        Button(self.main_frame, text="Parse", font="Serif 14 bold", command=self.parse_start).grid(row=11, column=0,
                                                                                                   columnspan=2)

        # --- status bar ---
        status_bar = Label(self.main_frame, text="by: Kerolloz", font="Serif 10 bold italic", bd=1, relief=SUNKEN,
                           anchor=W)
        status_bar.grid(row=13, column=0, columnspan=2, sticky=("N", "S", "W", "E"))
        status_bar.config(background='white')

        self.root.mainloop()

    def parse_start(self):
        """this function gets called when the Parse Button is clicked"""
        # create a thread for the progressbar, thread for the main program "parser"
        progress_speed = 8  # progressbar running speed
        progressbar_thread = threading.Thread(target=self.progressbar.start(progress_speed), args=())
        main_thread = threading.Thread(target=self.start, args=())
        # start the threads to work simultaneously
        progressbar_thread.start()
        main_thread.start()

    def progressbar_reset(self):
        self.progress.set(0.0)
        self.progressbar.stop()

    def start(self):
        link = str(self.problem_link_entry.get())

        try:
            request = urlopen(link)  # try reading the provided link, and if errors occur, stop
        except (ValueError, urllib.error.HTTPError):
            self.progressbar_reset()
            messagebox.showerror("Invalid Link", "Please, provide a valid CodeForces problem link !")
            return
        except urllib.error.URLError:
            self.progressbar_reset()
            messagebox.showerror("Error", "Connection Error!\nPlease, check the problem link or your internet "
                                          "connection.")
            return

        directory_name = link[-5:-2] + link[-1:]  # the last letters form the link
        directory_name = directory_name.replace('/', '')  # remove slash '/' form the directory name to avoid confusion

        os.system('mkdir ' + directory_name)  # create a new folder
        os.system('cp test.py ' + directory_name + '/')  # copy tester.exe into the problem folder
        os.chdir(directory_name)  # go to the problem folder

        with open('main.cpp', 'w') as code:
            code.write(c_code)

        html = request.read().decode()  # decode the bytes string to normal string, same as str(request.read())

        input_output_list = re.findall('<pre>(.*?)</pre>', html)
        # using regular expressions, return strings between "pre" opening and closing tags in the html code
        # "pre" is the tag that contains test cases, whether input or output

        input_output_group = group(input_output_list, 2)
        test_cases = list(input_output_group)

        index = 0
        for test in test_cases:
            with open('in' + str(index) + '.txt', 'w') as in_file:
                in_file.write(test[0].replace('<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n'))
            with open('out' + str(index) + '.txt', 'w') as out_file:
                out_file.write(test[1].replace('<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n'))
            index += 1

        with open('test_cases.txt', 'w') as f:
            f.write(str(index))

        os.chdir('..')  # go to the previous directory

        self.progressbar_reset()

        messagebox.showinfo('CF Parser', 'Problem has been parsed Successfully!')

        editor_number = self.editor_choice.get()

        # open the code using the chosen editor
        os.system(editors_list[editor_number] + ' ' + directory_name + '/main.cpp')


if __name__ == '__main__':
    # when the program starts
    main_application = Gui()
