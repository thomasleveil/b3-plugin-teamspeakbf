from tests import *
prepare_fakeparser_for_tests()

import unittest
import b3

from b3.fake import fakeConsole
from b3.fake import joe
import time

from b3.config import XmlConfigParser
from teamspeakbf import TeamspeakbfPlugin

conf = XmlConfigParser()
conf.setXml("""
<configuration plugin="teamspeakbf">
	<settings name="teamspeakServer">
		<!-- IP or domain where your teamspeak server is hosted -->
		<set name="host">{ts_host}</set>
		<!-- query port of your teamspeak server (default: 10011) -->
		<set name="queryport">{ts_port}</set>
		<!-- Teamspeak virtual server ID -->
		<set name="id">{ts_id}</set>
		<!-- B3 login information. You need to create a ServerQuery Login for B3. video tutorial : http://bit.ly/a5qcjp -->
		<set name="login">{ts_login}</set>
		<set name="password">{ts_password}</set>
	</settings>
	<settings name="teamspeakChannels">
		<set name="B3">B3 autoswitched channel</set>
		<set name="team1">Team 1</set>
		<set name="team2">Team 2</set>
	</settings>
    <settings name="commands">
        <!-- set here levels needed to be allowed to use commands.
            You can define a command alias adding '-' and the alias after the command name.
            Levels:
            0 : everyone
            1 : registered users
            2 : regular users
            20 : moderators
            40 : admins
            60 : full admins
            80 : senior admins
            100 : super admins
        -->

        <!-- Allow admins to reconnect/disconnect B3 to the teamspeak server -->
        <set name="tsreconnect">100</set>
        <set name="tsdisconnect">100</set>

        <!-- give the player info about the current Teamspeak server and his status -->
        <set name="teamspeak-ts">1</set>

        <!-- !tsauto allow players to change their autoswitch preferences between one
        of 'off', 'team', 'squad' -->
        <set name="tsauto">1</set>
    </settings>
</configuration>
""".format(ts_host=config.get("teamspeak_server", "host"),
           ts_port=config.get("teamspeak_server", "port"),
           ts_id=config.get("teamspeak_server", "id"),
           ts_login=config.get("teamspeak_server", "login"),
           ts_password=config.get("teamspeak_server", "password")))

joe.ip = config.get("me", "ip")



class TestTeamspeakbf(unittest.TestCase):

    tsclient = None
    tsDefaultChannel = None

    @classmethod
    def setUpClass(cls):
        global p, joe, conf

        ## create an instance of the plugin to test
        p = TeamspeakbfPlugin(fakeConsole, conf)
        p.onLoadConfig()
        p.onStartup()
        joe.connects('Joe')

        timeout = time.time() + 10
        while not p.tsconnection and time.time() < timeout:
            time.sleep(.1)
        if not p.tsconnection:
            raise AssertionError("Could not connect to TeamSpeak server")

        if not p.tsGetClient(joe):
            raise unittest.SkipTest("please connect to the test Teamspeak server first and make sure your ip is %s as set in config.ini" % config.get("me", "ip"))

        channellist = p.tsSendCommand('channellist')
        cls.tsDefaultChannel= p.tsGetChannelIdByName(u'Default Channel', channellist)
        if not cls.tsDefaultChannel:
            raise unittest.SkipTest("Could not get default teamspeak channel")


    def setUp(self):
        global p
        self.p = p
        joe.team = b3.TEAM_UNKNOWN
        joe.squad = -1

        p.tsMoveTsclientToChannelId(p.tsGetClient(joe), self.tsDefaultChannel)


    def test_cmd_ts(self):
        joe.clearMessageHistory()
        joe.says('!ts')
        self.assertNotEqual(0, len(joe.message_history))

    def test_cmd_ts_join(self):

        joe.clearMessageHistory()
        joe.says('!ts join')
        self.assertNotEqual(0, len(joe.message_history))
        time.sleep(.1)
        self.assertEqual(True, self.p.tsIsClientInB3Channel(self.p.tsGetClient(joe)))

        joe.clearMessageHistory()
        joe.says('!ts disjoin')
        self.assertNotEqual(0, len(joe.message_history))
        time.sleep(.1)
        self.assertEqual(False, self.p.tsIsClientInB3Channel(self.p.tsGetClient(joe)))

    def test_cmd_tsauto(self):
        joe.says('!ts join')
        joe.clearMessageHistory()
        joe.says('!tsauto')
        self.assertNotEqual(0, len(joe.message_history))

        joe.clearMessageHistory()
        joe.says('!tsauto off')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertEqual('You will not be automatically switched on teamspeak', joe.getMessageHistoryLike('You will'))

        joe.clearMessageHistory()
        joe.says('!tsauto team')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertEqual('You will be automatically switched on your team channel', joe.getMessageHistoryLike('You will'))

        joe.clearMessageHistory()
        joe.says('!tsauto squad')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertEqual('You will be automatically switched on your squad channel', joe.getMessageHistoryLike('You will'))

        joe.clearMessageHistory()
        joe.says('!tsauto on')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertNotEqual(None, joe.getMessageHistoryLike('Invalid parameter'))

        joe.clearMessageHistory()
        joe.says('!tsauto qsdfqsd f')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertNotEqual(None, joe.getMessageHistoryLike('Invalid parameter'))

        joe.clearMessageHistory()
        joe.says('!tsauto    ')
        self.assertNotEqual(0, len(joe.message_history))
        self.assertNotEqual(None, joe.getMessageHistoryLike('Invalid parameter'))

    def test_teamMisc(self):
        joe.says('!ts join')
        joe.team = b3.TEAM_SPEC
        joe.setvar(self.p, 'switchtarget', 'team')
        fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_SQUAD_CHANGE, (joe.team, joe.squad), joe))
        time.sleep(.1)
        tsclient = self.p.tsGetClient(joe)
        self.assertNotEqual(tsclient, None)
        self.assertEqual(tsclient['cid'], self.p.tsChannelIdB3)

    def test_team1(self):
        joe.says('!ts join')
        joe.team = b3.TEAM_BLUE
        joe.squad = 0
        joe.setvar(self.p, 'switchtarget', 'team')
        fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_SQUAD_CHANGE, (joe.team, joe.squad), joe))
        time.sleep(.1)
        tsclient = self.p.tsGetClient(joe)
        self.assertNotEqual(tsclient, None)
        self.assertEqual(tsclient['cid'], self.p.tsChannelIdTeam1)

    def test_team2(self):
        joe.says('!ts join')
        joe.team = b3.TEAM_RED
        joe.squad = 0
        joe.setvar(self.p, 'switchtarget', 'team')
        fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_SQUAD_CHANGE, (joe.team, joe.squad), joe))
        time.sleep(.1)
        tsclient = self.p.tsGetClient(joe)
        self.assertNotEqual(tsclient, None)
        self.assertNotEqual(tsclient, None)
        self.assertEqual(tsclient['cid'], self.p.tsChannelIdTeam2)

    def test_squadsTeam1(self):
        joe.says('!ts join')
        joe.team = b3.TEAM_BLUE
        joe.setvar(self.p, 'switchtarget', 'squad')
        for i in range(1, 9):
            joe.squad = i
            fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_SQUAD_CHANGE, (joe.team, joe.squad), joe))
            time.sleep(.1)
            tsclient = self.p.tsGetClient(joe)
            self.assertNotEqual(tsclient, None)
            self.assertEqual(tsclient['cid'], self.p.tsChannelIdSquadsTeam1[i])

    def test_squadsTeam2(self):
        joe.says('!ts join')
        joe.team = b3.TEAM_RED
        joe.setvar(self.p, 'switchtarget', 'squad')
        for i in range(1, 9):
            joe.squad = i
            fakeConsole.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_SQUAD_CHANGE, (joe.team, joe.squad), joe))
            time.sleep(.1)
            tsclient = self.p.tsGetClient(joe)
            self.assertNotEqual(tsclient, None)
            self.assertEqual(tsclient['cid'], self.p.tsChannelIdSquadsTeam2[i])

def donothing(*whatever):
    pass
fakeConsole.error = donothing
fakeConsole.debug = donothing
fakeConsole.bot = donothing
fakeConsole.verbose = donothing
fakeConsole.verbose2 = donothing
fakeConsole.console = donothing
fakeConsole.warning = donothing
fakeConsole.info = donothing
fakeConsole.exception = donothing
fakeConsole.critical = donothing

if __name__ == '__main__':
    unittest.main()
