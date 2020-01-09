import os
import subprocess
import sys

from termcolor import cprint

COMPILED_SUCCESSFULLY = 0
IDENTICAL = 0


def get_number_of_test_cases():
    # must include current_dir because running it from the parser will raise no file
    with open(current_directory + '/test_cases', 'r') as number_of_tests_file:
        number_of_test_cases = int(number_of_tests_file.read())
    return number_of_test_cases


def get_current_directory():
    return os.path.dirname(os.path.realpath(__file__))


def compile_solution():
    # returned 0 = successful
    return os.system('make {}/main'.format(current_directory))


def run_solution_on_test(test_num):
    command = '{current_directory}/main < {current_directory}/in{test_num} > {current_directory}/my_out{test_num}'.format(
        current_directory=current_directory, test_num=test_num)

    subprocess.getstatusoutput(command)


def compare_outputs_of_test(test_num):
    # getstatusoutput returns a tuple, the first element is the exit status
    # if zero(no error), successful
    command = 'diff -s -q -Z {current_directory}/out{test_num} {current_directory}/my_out{test_num}'.format(
        current_directory=current_directory, test_num=test_num)

    status_output = subprocess.getstatusoutput(command)

    return status_output[0]


def show_output(test_num):
    with open('%s/my_out%s' % (current_directory, test_num), 'r') as fin:
        print('----OUTPUT----')
        print(fin.read(), end='')
        print('--------------')


def quit_tester():
    input('\nPress ENTER to exit...')
    sys.exit()


if __name__ == '__main__':
    current_directory = get_current_directory()
    test_cases = get_number_of_test_cases()

    # if no show output argument is provided
    should_show_output = sys.argv[1] if len(sys.argv) > 1 else False

    cprint('Compiling...', 'white', attrs=['dark'])

    if compile_solution() is COMPILED_SUCCESSFULLY:
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
        test_num = str(e)

        cprint('Test Case %d:' % (e+1), 'yellow', end='')

        run_solution_on_test(test_num)

        if compare_outputs_of_test(test_num) is IDENTICAL:
            cprint(' Passed', 'green')
        else:
            is_accepted = False
            cprint(' Wrong Answer', 'red')

        if should_show_output:
            show_output(test_num)

    print()

    if is_accepted:
        cprint("ACCEPTED", 'green', attrs=['reverse', 'bold'])
    else:
        cprint('Try Harder!', 'white', 'on_blue')

    cprint('\nPress ANY KEY to exit...', end='', color='white')

    input()
