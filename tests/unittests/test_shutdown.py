from tests import *
prepare_fakeparser_for_tests()

import unittest
import b3

from b3.fake import fakeConsole
from b3.fake import superadmin
import time

from b3.config import XmlConfigParser
from teamspeakbf import TeamspeakbfPlugin, ServerQuery, TS3Error

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

superadmin.ip = config.get("me", "ip")


class Ts3Server(object):
    """Quick Ts3 client to control the Teamspeak server from out tests"""
    def __init__(self, host, port, server_id, login, password):
        self.tsconnection = ServerQuery(host, port)
        self.tsconnection.connect()
        self.tsconnection.command('login', {'client_login_name': login, 'client_login_password': password})
        self.tsconnection.command('use', {'sid': server_id})
        #self.tsconnection.telnet.set_debuglevel(99)

    def disconnect(self):
        self.tsconnection.disconnect()
        del self.tsconnection

    def get_serverinfo(self):
        return self.tsconnection.command('serverinfo')

    def get_channellist(self):
        return self.tsconnection.command('channellist')

    def get_channel_tree(self):
        channels = self.get_channellist()
        channels_index = {0: {'children': []}}
        for c in channels:
            channels_index[c['cid']] = {'data':c, 'children': []}
        for i, channel in channels_index.iteritems():
            if 'data' in channel:
                parent = channels_index[channel['data']['pid']]
                parent['children'].append(channel)
        return channels_index[0]

    @staticmethod
    def walk_channel_tree(func, channel, level=0):
        func(channel, level)
        for child in sorted(channel['children'], key=lambda x: x['data']['channel_order']):
            Ts3Server.walk_channel_tree(func, child, level + 1)

    def print_channel_tree(self):
        def print_channel(channel, level=0):
            if 'data' in channel:
                print "  "*level + "%s <%s>" % (channel['data']['channel_name'], channel['data']['cid'])
        Ts3Server.walk_channel_tree(print_channel, self.get_channel_tree())

    def del_channel(self, cid):
        try:
            self.tsconnection.command('channeldelete', {'cid': cid, 'force': 1})
        except TS3Error, err:
            print err

class Test_shutdown(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ## our own ts3 connection
        try:
            cls.ts3 = Ts3Server(config.get("teamspeak_server", "host"),
                        config.get("teamspeak_server", "port"),
                        config.get("teamspeak_server", "id"),
                        config.get("teamspeak_server", "login"),
                        config.get("teamspeak_server", "password"))
        except TS3Error, err:
            raise unittest.SkipTest("could not connect to Teamspeak server : %s" % err)

    def setUp(self):
        for channel in Test_shutdown.ts3.get_channellist():
            if channel['pid'] != 0:
                Test_shutdown.ts3.del_channel(channel['cid'])
        time.sleep(.5)
        Test_shutdown.ts3.print_channel_tree()

    def test_no_player(self):
        # count minimum channels
        initial_num_channels = len(Test_shutdown.ts3.get_channellist())

        ## create an instance of the plugin to test
        p = TeamspeakbfPlugin(fakeConsole, conf)
        p.onLoadConfig()
        p.onStartup()

        Test_shutdown.ts3.print_channel_tree()
        clist = Test_shutdown.ts3.get_channellist()
        afterinit_num_channels = len(clist)
        self.assertLess(initial_num_channels, afterinit_num_channels)

        superadmin.connects('superadmin')
        superadmin.says('!die')
        timeout = time.time() + 20
        while p.connected and time.time() < timeout:
            time.sleep(.5)
        if p.connected:
            self.fail("Could not disconnect from TeamSpeak server")

        time.sleep(.5)
        Test_shutdown.ts3.print_channel_tree()
        clist = Test_shutdown.ts3.get_channellist()
        afterdeath_num_channels = len(clist)
        self.assertGreaterEqual(initial_num_channels, afterdeath_num_channels)


    def test_with_player(self):
        # count minimum channels
        initial_num_channels = len(Test_shutdown.ts3.get_channellist())

        ## create an instance of the plugin to test
        p = TeamspeakbfPlugin(fakeConsole, conf)
        p.onLoadConfig()
        p.onStartup()

        superadmin.connects('superadmin')

        if not p.tsGetClient(superadmin):
            raise unittest.SkipTest("please connect to the test Teamspeak server first and make sure your ip is %s as set in config.ini" % config.get("me", "ip"))


        Test_shutdown.ts3.print_channel_tree()
        clist = Test_shutdown.ts3.get_channellist()
        afterinit_num_channels = len(clist)
        self.assertLess(initial_num_channels, afterinit_num_channels)

        superadmin.says('!ts join')
        time.sleep(.5)

        superadmin.says('!die')
        timeout = time.time() + 20
        while p.connected and time.time() < timeout:
            time.sleep(.5)
        if p.connected:
            self.fail("Could not disconnect from TeamSpeak server")

        time.sleep(.5)
        Test_shutdown.ts3.print_channel_tree()
        clist = Test_shutdown.ts3.get_channellist()
        afterdeath_num_channels = len(clist)
        self.assertGreaterEqual(initial_num_channels, afterdeath_num_channels)


        

if __name__ == '__main__':
    unittest.main()
