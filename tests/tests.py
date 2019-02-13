import os
import codeforces
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
        self.assertEqual(parser.get_tags_contents(souped_html, 'pre'), [['test1'], ['test2']])


class CodeForcesTests(unittest.TestCase):
    logged_in_browser = RoboBrowser(parser='html.parser')

    def test_safe_get(self):
        _dict = {
            'existing_key': 1
        }
        self.assertEqual(codeforces.safe_get(_dict, 'existing_key'), 1)
        self.assertIsNone(codeforces.safe_get(_dict, 'non_existing_key'))

    def test_get_latest_verdict(self):
        self.assertTrue(codeforces.get_latest_verdict("tourist"))
        with self.assertRaises(ConnectionError):
            codeforces.get_latest_verdict('_')

    def test_login(self):
        self.assertTrue(codeforces.login(self.logged_in_browser, 'test-parser', 'parser'))
        browser = RoboBrowser(parser='html.parser')  # create a new logged out browser
        self.assertFalse(codeforces.login(browser, '_', '_'))

    def test_submit_solution_to_problem(self):
        self.setUp()

        submission_status = codeforces.submit_solution_to_problem(self.logged_in_browser,
                                                                  'GNU G++17 7.3.0', 'https://codeforces.com/problemset/problem/4/A',
                                                                  'main.cpp')
        self.assertEqual(submission_status, codeforces.CF_SUBMITTED_SUCCESSFULLY)

        submission_status = codeforces.submit_solution_to_problem(self.logged_in_browser,
                                                                  'GNU G++17 7.3.0', 'https://codeforces.com/problemset/problem/4/A',
                                                                  'main.cpp')
        self.assertEqual(submission_status, codeforces.CF_ALREADY_SUBMITTED)

    def test_get_latest_verdict_is_accepted(self):
        latest_verdict = codeforces.get_latest_verdict('test-parser')
        # returns id_, verdict_, time_, memory_, passed_test_count_
        self.assertEqual(
            latest_verdict[1], "OK"
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
                //""" + uuid4().hex
        with open('main.cpp', 'w') as ac_code:
            ac_code.write(accepted_code)

    def tearDown(self):
        os.remove('main.cpp')

