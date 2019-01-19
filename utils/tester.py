import os
import sys
import subprocess
from termcolor import cprint


def get_number_of_text_cases():
    with open('test_cases.txt', 'r') as number_of_tests_file:
        number_of_test_cases = int(number_of_tests_file.read())
    return number_of_test_cases


def get_current_directory():
    return str(os.path.dirname(os.path.realpath(__file__)))


def compiled_cpp_successfully():
    # returned 0 = successful
    return os.system('g++ ' + current_directory + '/main.cpp -o ' + current_directory + '/a.out') == 0


def run_solution_on_test(test_index):
    os.system(
        current_directory + '/a.out < ' + current_directory + '/in' + test_index + '.txt > ' +
        current_directory + '/my_out' + test_index + '.txt'
    )


def compare_outputs_of_test(test_index):
    # getstatusoutput returns a tuple, the first element is the exit status
    # if zero(no error), successful
    compare_status = subprocess.getstatusoutput(
            'diff -s -q -Z ' + current_directory + '/out' + test_index + '.txt ' + current_directory +
            '/my_out' + test_index + '.txt'
           )[0]

    return compare_status == 0


if __name__ == '__main__':

    test_cases = get_number_of_text_cases()
    current_directory = get_current_directory()

    cprint('Compiling...', 'white', attrs=['dark'])

    if compiled_cpp_successfully():
        os.system('clear')
        cprint('Compiled successfully!\n', 'green', attrs=['bold'])
    else:
        cprint('Compilation ERROR\n\n' + "Please, Check Your code", 'red', attrs=['bold'])
        cprint('\nPress ENTER to exit...', end='', color='white')
        input()
        sys.exit()
        # stop and close the program

    is_accepted = True

    for e in range(test_cases):
        test_number = str(e)

        run_solution_on_test(test_number)

        cprint('Test Case {}:'.format(str(e + 1)), 'yellow')

        if compare_outputs_of_test(test_number):
            # 0 means Identical
            cprint(' Passed', 'green')
        else:
            is_accepted = False
            cprint(' Wrong Answer', 'red')

    print()

    if is_accepted:
        cprint("ACCEPTED", 'green', attrs=['reverse', 'bold'])
    else:
        cprint('Try Harder!', 'white', 'on_blue')

    cprint('\nPress ANY KEY to exit...', end='', color='white')

    input()
