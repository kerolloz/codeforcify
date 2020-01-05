from robobrowser import RoboBrowser

import login
import parser

if __name__ == '__main__':

    shared_browser = RoboBrowser(parser='html.parser', timeout=10)

    login_gui = login.Login(shared_browser)

    if login_gui.is_logged_in:
        parser_gui = parser.Parser(
            shared_browser,
            login_gui.username,
            login_gui.api_key,
            login_gui.api_secret)
