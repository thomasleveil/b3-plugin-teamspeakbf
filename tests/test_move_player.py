# -*- encoding: utf-8 -*-
import time
from tests import *
prepare_fakeparser_for_tests()


from b3.fake import fakeConsole, FakeClient
from teamspeakbf import TeamspeakbfPlugin
from b3.config import XmlConfigParser
from b3 import TEAM_BLUE, TEAM_RED, TEAM_SPEC, TEAM_UNKNOWN, TEAM_FREE


conf = XmlConfigParser()
conf.loadFromString("""
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
		<set name="tsreconnect">100</set>
		<set name="tsdisconnect">100</set>
        <set name="teamspeak-ts">0</set>
        <set name="tsauto-tsa">0</set>
	</settings>
</configuration>
""".format(ts_host=config.get("teamspeak_server", "host"),
           ts_port=config.get("teamspeak_server", "port"),
           ts_id=config.get("teamspeak_server", "id"),
           ts_login=config.get("teamspeak_server", "login"),
           ts_password=config.get("teamspeak_server", "password")))

p = TeamspeakbfPlugin(fakeConsole, conf)
p.onLoadConfig()
p.onStartup()

def instruct(instructions):
    print "\n\n> %s" % instructions
    raw_input("type ENTER when ready")


me = FakeClient(fakeConsole, name="me", guid="zaerazerazerzaer", groupBits=128, team=TEAM_UNKNOWN, ip=config.get("me", "ip"))

# force me to the managed channel
tsclient = p.tsGetClient(me)
while not tsclient:
    instruct("connect to the teamspeak server")
    tsclient = p.tsGetClient(me)

me.connects(0)

if not p.tsIsClientInB3Channel(tsclient):
    p.tsMoveTsclientToChannelId(tsclient, p.tsChannelIdB3)

time.sleep(.5)
me.says('!ts')

time.sleep(.5)
me.says('!ts disjoin')

time.sleep(.5)
me.says('!ts')

time.sleep(.5)
me.says('!ts join')

time.sleep(.5)
me.says('!tsauto team')

time.sleep(.5)
p.tsTellClient(tsclient['clid'], "Going to spec")
me.team = TEAM_SPEC

time.sleep(1)
p.tsTellClient(tsclient['clid'], "Going to blue team")
me.team = TEAM_BLUE

time.sleep(1)
p.tsTellClient(tsclient['clid'], "Going to red team")
me.team = TEAM_RED

time.sleep(1)
p.tsTellClient(tsclient['clid'], "Going in no team")
me.team = TEAM_FREE

time.sleep(1)
me.says('!tsauto off')
p.tsTellClient(tsclient['clid'], "Going to spec")
me.team = TEAM_SPEC
time.sleep(0.25)
p.tsTellClient(tsclient['clid'], "Going to blue team")
me.team = TEAM_BLUE
time.sleep(0.25)
p.tsTellClient(tsclient['clid'], "Going to red team")
me.team = TEAM_RED
time.sleep(0.25)
p.tsTellClient(tsclient['clid'], "Going in no team")
me.team = TEAM_FREE

time.sleep(.5)