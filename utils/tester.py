import os
import sys
import subprocess
from termcolor import cprint


def get_number_of_test_cases_for(current_dir):
    # must include current_dir because running it from the parser will raise no file
    with open(current_dir + '/test_cases.txt', 'r') as number_of_tests_file:
        number_of_test_cases = int(number_of_tests_file.read())
    return number_of_test_cases


def get_current_directory():
    return str(os.path.dirname(os.path.realpath(__file__)))


def compiled_cpp_successfully():
    # returned 0 = successful
    return os.system('g++ ' + current_directory + '/main.cpp -o ' + current_directory + '/a.out') == 0


def run_solution_on_test(test_index):
    subprocess.getstatusoutput(
        current_directory + '/a.out < ' + current_directory + '/in' + test_index + '.txt > ' +
        current_directory + '/my_out' + test_index + '.txt'
    )


def compare_outputs_of_test(test_index):
    # getstatusoutput returns a tuple, the first element is the exit status
    # if zero(no error), successful
    status_output = subprocess.getstatusoutput(
        'diff -s -q -Z ' + current_directory + '/out' + test_index + '.txt ' + current_directory +
        '/my_out' + test_index + '.txt'
    )

    return status_output[0] == 0  # 0 means Identical


def show_output(test_number):
    with open(current_directory + '/my_out' + test_number + '.txt', 'r') as fin:
        print('----OUTPUT----')
        print(fin.read(), end='')
        print('--------------')


def quit_tester():
    cprint('\nPress ENTER to exit...', end='', color='white')
    input()
    sys.exit()


if __name__ == '__main__':
    current_directory = get_current_directory()
    test_cases = get_number_of_test_cases_for(current_directory)

    # if no show output argument is provided
    should_show_output = sys.argv[1] if len(sys.argv) > 1 else False

    cprint('Compiling...', 'white', attrs=['dark'])

    if compiled_cpp_successfully():
        os.system('clear')
        cprint('Compiled successfully!\n', 'green', attrs=['bold'])
    else:
        cprint('Compilation ERROR\n\n' +
               "Please, Check Your code", 'red', attrs=['bold'])
        quit_tester()
        # stop and close the program

    if test_cases == 0:
        cprint("No available test cases!", color="red")
        quit_tester()

    is_accepted = True

    for e in range(test_cases):
        test_number = str(e)

        cprint('Test Case {}:'.format(str(e + 1)), 'yellow', end='')

        run_solution_on_test(test_number)

        if compare_outputs_of_test(test_number):
            cprint(' Passed', 'green')
        else:
            is_accepted = False
            cprint(' Wrong Answer', 'red')

        if should_show_output:
            show_output(test_number)

    print()

    if is_accepted:
        cprint("ACCEPTED", 'green', attrs=['reverse', 'bold'])
    else:
        cprint('Try Harder!', 'white', 'on_blue')

    cprint('\nPress ANY KEY to exit...', end='', color='white')

    input()
