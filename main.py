from robobrowser import RoboBrowser

import login
import parser

if __name__ == '__main__':
    shared_browser = RoboBrowser(parser='html.parser', timeout=10)
    login_gui = login.Login(shared_browser)
    user_data = login_gui.user_data
    del login_gui  # free memory reserved by the login gui
    parser_gui = parser.Parser(shared_browser, user_data)
