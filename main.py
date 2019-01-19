from tkinter import Tk
from robobrowser import RoboBrowser
from utils import login, parser

if __name__ == '__main__':

    shared_gui = Tk()
    shared_browser = RoboBrowser(parser='html.parser')

    login_gui = login.Login(shared_gui, shared_browser)

    if login_gui.is_logged_in:
        parser_gui = parser.Parser(shared_gui, shared_browser, login_gui.get_username())
