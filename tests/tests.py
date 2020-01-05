import os
import codeforces_wrapper
import unittest
import parser
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
from uuid import uuid4


class ParserTests(unittest.TestCase):

    def test_get_contents(self):
        souped_html = BeautifulSoup(
            "<pre>test1</pre>"
            "<pre>test2</pre>", 'html.parser'
        )
        self.assertEqual(parser.get_tags_contents(
            souped_html, 'pre'), [['test1'], ['test2']])


class CodeForcesTests(unittest.TestCase):
    logged_in_browser = RoboBrowser(parser='html.parser')

    def test_safe_get(self):
        _dict = {
            'existing_key': 1
        }
        self.assertEqual(codeforces_wrapper.safe_get(_dict, 'existing_key'), 1)
        self.assertIsNone(codeforces_wrapper.safe_get(
            _dict, 'non_existing_key'))

    def test_get_latest_verdict(self):
        self.assertTrue(codeforces_wrapper.get_latest_verdict(
            None, None, "tourist"))
        with self.assertRaises(ValueError):
            codeforces_wrapper.get_latest_verdict(None, None, '_')

    def test_login(self):
        self.assertTrue(codeforces_wrapper.login(
            self.logged_in_browser, 'test-parser', 'parser'))
        # create a new logged out browser
        browser = RoboBrowser(parser='html.parser')
        self.assertFalse(codeforces_wrapper.login(browser, '_', '_'))

    def test_submit_solution_to_problem(self):
        self.setUp()

        submission_status = codeforces_wrapper.submit_solution_to_problem(self.logged_in_browser,
                                                                          'GNU G++17 7.3.0', 'https://codeforces.com/problemset/problem/4/A',
                                                                          'main.cpp')
        self.assertEqual(submission_status,
                         codeforces_wrapper.CF_SUBMITTED_SUCCESSFULLY)

        submission_status = codeforces_wrapper.submit_solution_to_problem(self.logged_in_browser,
                                                                          'GNU G++17 7.3.0', 'https://codeforces.com/problemset/problem/4/A',
                                                                          'main.cpp')
        self.assertEqual(submission_status,
                         codeforces_wrapper.CF_ALREADY_SUBMITTED)

    def test_get_latest_verdict_is_accepted(self):
        latest_submission = codeforces_wrapper.get_latest_verdict(
            None, None, 'test-parser')
        # returns id_, verdict_, time_, memory_, passed_test_count_
        while latest_submission.verdict.value == "TESTING":
            latest_submission = codeforces_wrapper.get_latest_verdict(
                None, None, 'test-parser')
        self.assertEqual(
            latest_submission.verdict.value, "OK"
        )

    def setUp(self):
        accepted_code = r"""
                #include <bits/stdc++.h>
                using namespace std;
                int main () {
                    int n;
                    cin >> n;
                    if(n % 2 == 0 && n != 2) cout << "YES" << endl;
                    else cout << "NO" << endl;
                }
                //""" + uuid4().hex + uuid4().int
        with open('main.cpp', 'w') as ac_code:
            ac_code.write(accepted_code)

    def tearDown(self):
        os.remove('main.cpp')
