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
