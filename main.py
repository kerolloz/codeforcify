from robobrowser import RoboBrowser

import login
import parser

if __name__ == '__main__':
    shared_browser = RoboBrowser(parser='html.parser', timeout=10)
    login_gui = login.Login(shared_browser)
    user_data, is_logged_in = login_gui.user_data, login_gui.is_logged_in
    del login_gui  # free memory reserved by the login gui
    if is_logged_in:
        parser_gui = parser.Parser(shared_browser, user_data)
