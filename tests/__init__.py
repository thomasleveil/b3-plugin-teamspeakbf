# -*- encoding: utf-8 -*-
import ConfigParser, os, sys
from b3.fake import fakeConsole

script_dir = os.path.dirname(os.path.abspath(__file__))

global config
config = ConfigParser.ConfigParser()


try:
    with open(os.path.join(script_dir, "config.ini")) as fh:
        config.readfp(fh)
except IOError, err:
    if err.errno == 2:
        print "\n\nYou must rename \"%s\" to \"%s\" to run the tests" % (os.path.join(script_dir, "config.ini.example"), os.path.join(script_dir, "config.ini"))
        sys.exit(1)
    else:
        raise

def prepare_fakeparser_for_tests():
    fakeConsole.Events.createEvent('EVT_CLIENT_SQUAD_CHANGE', 'Client Squad Change')
    fakeConsole.gameName = 'bf3'
    fakeConsole.game.sv_hostname = 'FakeGameServer'