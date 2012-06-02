TeamSpeakBf plugin for Big Brother Bot (www.bigbrotherbot.net)
==============================================================



Description
-----------

This plugin will change BFBC2 / BF3 players that are found on your teamspeak 3
server to the relevant team/squad channel.


Requirements
------------

You must have a Teamspeak 3 server.


Player commands
---------------

!teamspeak
  give info about the Teamspeak server (ip:port) and instruction on how to use this plugin

!ts
  alias for !teamspeak

!ts join
  moves you to the B3 managed channel on TS

!ts disjoin
  moves you back out of the B3 managed channel on TS

!tsauto off
  disable auto channel changes

!tsauto team
  make B3 automatically change you to your team channel when you change teams in game

!tsauto squad
  make B3 automatically change you to your squad channel when you change squad or team in game

!tsa
  alias for !tsauto


Admin commands
--------------

!tsreconnect
  force B3 to reconnect to the TeamSpeak server

!tsdisconnect
  disconnect B3 from the TeamSpeak server


Changelog
---------

1.0 - 2010/04/13
  * first release. should do its job. waiting for feedbacks to stabilize code

1.1 - 2010/04/14
  * add command !tsauto [off|team|squad] to give player the choice of disabling
  * auto channel switching or to activate it only for teams or squads

2.0 - 2011/12/08
  * rename plugin from teamspeakbfbc2 to teamspeakbf
  * add support for BF3
  * can recognize players on Teamspeak based on their IP address instead of relying only on name
  * handles BF3 Squad Death Match game mode
  
2.1 - 2011/12/14
  * fix crash when trying to delete TS channels having users
  * ServerQuery is now more reactive when receiving a error as response

2.2 - 2011/12/16
  * fixes issue #1 : 'player aren't moved at round start' (requires b3 >= 1.8.0dev15)

2.3 - 2011/12/18
  * default switch target (squad or team) can be specified in the config file (thanks to 82ndab-Bravo17)

2.3.1 - 2011/12/18
  * default switch target can also be 'off'

2.4 - 2012/05/01
  * Allow main B3 Auto channel to be permanent to preserve TS tree
  * Allow creation of only Team channels to cut down on number of channels
  * Allow B3 Team channel flip/flop each round to keep in sync with BF3 Team flip/flop and cut down on channel switching
  * Allow Codec and Voice Quality to be set in the xml



Installation
------------

To install the plugin follow the steps below:

1. copy teamspeakbf.py into ``b3/extplugins``
2. copy ``plugin_teamspeakbf.xml`` into your main B3 conf folder
3. set up your TeamSpeak server to enable ServerQuery
4. add the IP address of the machine running B3 to your TeamSpeak server ``query_ip_whitelist.txt`` file
5. edit ``plugin_teamspeakbf.xml`` with your teamspeak server information
6. update your main b3 config file with::

    <plugin name="teamspeakbf" config="@conf/plugin_teamspeakbf.xml"/>


Support
-------

see the B3 forums : http://forum.bigbrotherbot.net/plugins-by-courgette/teamspeak-battlefield/