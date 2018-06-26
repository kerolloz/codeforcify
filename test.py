#!/usr/bin/python3
import os
import sys
from termcolor import cprint
import subprocess


test_cases = int(open('test_cases.txt', 'r').read())

input_file_names = ['in' + str(e) + '.txt' for e in range(test_cases)]
output_file_names = ['out' + str(e) + '.txt' for e in range(test_cases)]

os.system('clear')

cprint('Compiling...', 'white', attrs=['dark'])

if os.system('g++ main.cpp') == 0:  # returned 0 = successful
    os.system('clear')
    cprint('Compiled successfully...!\n', 'green', attrs=['bold'])
else:
    cprint('Compilation ERROR\n\n' + "Please, Check Your code", 'red',  attrs=['bold'])
    cprint('\nPress ENTER to exit...', end='', color='white')
    input()
    sys.exit()
    # stop and close the program

ac = True

for e in range(test_cases):
    os.system('./a.out < ' + input_file_names[e] + ' > my_' + output_file_names[e])

    cprint('Test Case {}:'.format(str(e + 1)), 'yellow')

    diff_command = subprocess.getstatusoutput('diff -s -q -Z ' + output_file_names[e] + ' my_' + output_file_names[e])
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
