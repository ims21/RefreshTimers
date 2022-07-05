#################################################################################
#
#    RefreshTimers plugin for OpenPLi-Enigma2
#    version:
#
#    by ims (c)2017-2022
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#################################################################################

from Plugins.Plugin import PluginDescriptor

def main(session,**kwargs):
	import ui
	session.open(ui.RefreshTimersSetup)

def sessionstart(reason, **kwargs):
	if reason == 0:
		import ui
		ui.RefreshTimers.startRefreshTimers(kwargs["session"])

def Plugins(**kwargs):
	name = "RefreshTimers"
	descr = _("update begin time for timer events")
	return [
		PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, icon = 'plugin.png', fnc=main),
		PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart, needsRestart = True),
	]
