# -*- encoding: utf-8 -*-
from tests import *
prepare_fakeparser_for_tests()


from b3.fake import fakeConsole, superadmin
from teamspeakbf import TeamspeakbfPlugin
from b3.config import XmlConfigParser


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
