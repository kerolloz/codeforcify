import requests
import time
from termcolor import cprint

CF_SUBMITTED_SUCCESSFULLY = 1
CF_NOT_SUBMITTED_YET = 0
CF_FILE_NOT_FOUND = -1
CF_ALREADY_SUBMITTED = -2


def safe_get(dictionary, key):
    """This method tries to get the value of the key from the dictionary safely!"""
    if key in dictionary:
        return dictionary[key]
    return None


def get_latest_verdict(user):
    """This method uses codeforces API to get the last submission verdict submitted by the user"""

    r = requests.get('http://codeforces.com/api/user.status?'
                     + 'handle={}&from=1&count=1'.format(user))
    js = r.json()
    if 'status' not in js or js['status'] != 'OK':
        raise ConnectionError('Cannot connect to codeforces!')
    try:
        result = js['result'][0]
        id_ = result['id']
        # try to get the value of the verdict from the result json object
        verdict_ = safe_get(result, 'verdict')
        time_ = result['timeConsumedMillis']
        memory_ = result['memoryConsumedBytes'] / 1000
        passed_test_count_ = result['passedTestCount']
    except Exception as e:
        raise ConnectionError('Cannot get latest submission, error')
    return id_, verdict_, time_, memory_, passed_test_count_


def login(browser, username, password):
    """This method tries to login into codeforces account using RoboBrowser"""

    cprint("Opening login page", color='yellow')
    browser.open('http://codeforces.com/enter')
    enter_form = browser.get_form('enterForm')  # get login form object
    # set username in form to the username preset in utils.config
    enter_form['handleOrEmail'] = username
    enter_form['password'] = password  # same for password
    cprint("Logging in!", color='yellow')
    # submit the login form with the added info for user and password
    browser.submit_form(enter_form)

    try:
        checks = list(map(lambda x: x.getText()[1:].strip(),
                          browser.select('div.caption.titled')))
        if username not in checks:
            return False
    except Exception as e:
        return e

    cprint("[{}] logged in successfully!".format(username), color="green")
    return True


def submit_solution_to_problem(browser, solution_language, problem_id, filename):
    """"This method tries to submit codeforces solution to a problem using file"""

    cprint('Submitting [{1}] for problem [{0}] in [{2}]'.format(problem_id, filename, solution_language),
           color='green')

    browser.open('https://codeforces.com/contest/' +
                 problem_id[:-1] + '/problem/' + problem_id[-1])
    submit_form = browser.get_form(class_='submitForm')
    # set the problem id to the first command line argument

    while True:
        try:
            # set the solution language to the second argument
            submit_form['programTypeId'] = solution_language
            break  # if no error happens break, else retry
        except Exception as e:
            cprint('No such language [{}]!'.format(
                solution_language), color='red')
            cprint("Available languages are:", color='yellow')
            options = submit_form['programTypeId'].options
            labels = submit_form['programTypeId'].labels
            languages_dictionary = dict(zip(options, labels))
            for option, label in languages_dictionary.items():
                print(
                    "{number:2} -> {language}".format(number=option, language=label))
            solution_language = languages_dictionary[input(
                "Enter language number: ")]
            cprint('You chose [{}]'.format(solution_language), color='green')

    try:
        # set the source code file to the name provided in cl argument
        submit_form['sourceFile'] = filename
    except Exception as e:
        cprint('File {0} not found in current directory'.format(filename))
        return CF_FILE_NOT_FOUND

    browser.submit_form(submit_form)  # submit the source code file

    if browser.url[-3:] != '/my':
        cprint(
            'Failed submission, probably you have submit the same file before', color='red')
        return CF_ALREADY_SUBMITTED

    cprint("Okay submitted successfully!", color="green")
    return CF_SUBMITTED_SUCCESSFULLY


def get_last_verdict_status_for_user(last_submit_id, username):
    """This method returns the user last submission verdict"""
    last_status = None
    has_started = False
    while True:
        # keep trying to get last submission verdict
        id_, verdict_, time_, memory_, passed_test_count_ = get_latest_verdict(
            username)
        if id_ != last_submit_id and verdict_ != 'TESTING' and verdict_ is not None:
            # check if verdict is set to some value (Not TESTING)
            if verdict_ == 'OK':
                # OK = ACCEPTED
                last_status = 'ACCEPTED!\n' \
                              'OK - Passed {} tests\n' \
                              '{} MS | {} KB'.format(
                                  passed_test_count_, time_, memory_)
            else:
                # NOT ACCEPTED
                last_status = "{}!\n" \
                              "on test {}\n" \
                              "{} MS | {} KB".format(
                                  verdict_, passed_test_count_ + 1, time_, memory_)
            # Print submission details
            yield last_status
            break
        elif verdict_ == 'TESTING' and (not has_started):
            last_status = "\nTesting...\n"
            has_started = True
        time.sleep(0.5)
        yield last_status
        # hold on before making another request i.e.: (wait for a while till the judge finish testing)
