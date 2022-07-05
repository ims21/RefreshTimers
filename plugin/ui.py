# for localized messages
from . import _, ngettext

#################################################################################
#
#    RefreshTimers plugin for OpenPLi Enigma2
#    version:
VERSION = "0.47"
#    by ims(ims21) (c)2017-2022
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

from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Label import Label

from enigma import eEPGCache, eTimer
from Components.config import config, getConfigListEntry, ConfigYesNo, ConfigSubsection, ConfigClock, ConfigSelection, ConfigText
from ServiceReference import ServiceReference
import datetime
import skin

installedEpgRefresh = False
try:
	from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh
	installedEpgRefresh = True
except:
	pass

config.plugins.RefreshTimers = ConfigSubsection()
config.plugins.RefreshTimers.enable = ConfigYesNo(default = False)
config.plugins.RefreshTimers.where = ConfigText(default = "/media/hdd")
config.plugins.RefreshTimers.time = ConfigClock(default = ((9*60) + 0) * 60)
config.plugins.RefreshTimers.log = ConfigYesNo(default = False)
config.plugins.RefreshTimers.pdconly = ConfigYesNo(default = True)
cfg = config.plugins.RefreshTimers

try:
	fC = "\c%08x" % int(skin.parseColor("foreground").argb())
except:
	fC = "\c00f0f0f0"
rC = "\c00ff4000"

class RefreshTimersSetup(Screen, ConfigListScreen):
	skin = """
	<screen name="RefreshTimersSetup" position="center,center" size="560,180" title="RefreshTimers Setup" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red"    position="0,0"   size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_green"  position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue"   position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="config" position="10,45" size="540,125" zPosition="1" scrollbarMode="showOnDemand" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = [ ]
		self.onChangedEntry = [ ]
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"red": self.keyCancel,
				"green": self.keySave,
				"ok": self.keySave,
				"blue": self.manually,
			}, -2)

		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("Manually"))

		choices=getLocationChoices()
		if choices:
			currentwhere = cfg.where.value
			defaultchoice = choices[0][0] 
			for k,v in choices:
				if k == currentwhere:
					defaultchoice = k
					break
		else:
			defaultchoice = ""
			choices = [("", _("Nowhere"))]
		cfg.where = ConfigSelection(default=defaultchoice, choices=choices)

		self.onLayoutFinish.append(self.layoutFinished)

		self.enable = _("Enable Refresh Timer")
		self.listMenu()

	def listMenu(self):
		self.list = [ getConfigListEntry( self.enable, cfg.enable) ]
		if cfg.enable.value:
			self.list.append(getConfigListEntry(_("Refresh time period (mm:ss)"), cfg.time))
			self.list.append(getConfigListEntry(_("Services with PDC only"), cfg.pdconly))
			self.list.append(getConfigListEntry(_("Save log"), cfg.log))
			if cfg.log.value:
				self.list.append(getConfigListEntry(4*" " + _("Location"), cfg.where))
		self["config"].list = self.list
		self["config"].setList(self.list)

	def changedEntry(self):
		self.listMenu()

	def layoutFinished(self):
		self.setTitle(_("RefreshTimers Setup v%s") % VERSION)

	def manually(self):
		self.session.open(RefreshTimersScreen)

	def keySave(self):
		if cfg.enable.value:
			RefreshTimers.RefreshTimers.start(15000, True)
		else:
			if RefreshTimers.RefreshTimers.isActive():
				RefreshTimers.RefreshTimers.stop()
		for x in self["config"].list:
			x[1].save()
		self.close(True)

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
def time_now(fulldate=False):
	now = datetime.datetime.now()
	if fulldate:
		return now.strftime("%d-%m-%Y %H:%M:%S") + 2*" "
	return now.strftime("%H:%M:%S") + 2*" "

def getChangedTxt(delta, service_name, name):
	time=""
	hours = delta//3600
	rest = delta%3600
	minuts = rest//60
	secs = rest%60

	if hours:
		time="(%dh %dm %ds)" % (hours, minuts, secs)
	else:
		time="(%dm %ds)" % (minuts, secs)
	return "{0:26s} {1:60s} {2:>10s}\n" .format(service_name[:26].decode("utf-8","ignore"), name[:60].decode("utf-8","ignore"), time)
	

margin_before = config.recording.margin_before.value * 60
margin_after = config.recording.margin_after.value * 60

def saveLog(msg):
	if cfg.log.value:
		try:
			log = file(cfg.where.value + '/' + 'timer_correction.log', 'a');log.write(msg);log.close()
		except:
			print "[RefreshTimers] log failed"

def Make_Correction(session):
		if installedEpgRefresh and epgrefresh.isRunning():
			msg = _("Not possible - EPGRefresh is running.")
			if cfg.log.value:
				saveLog(time_now() + msg + '\n')
			return msg
		changed_start = 0
		changed_end = 0
		msg = _("Nothing was changed")
		changed_txt = ""
		epgcache = eEPGCache.getInstance()
		for timer_event in session.nav.RecordTimer.timer_list:
			if timer_event.eit:
				service_ref = timer_event.service_ref and timer_event.service_ref.ref
				event = epgcache.lookupEventId(service_ref, timer_event.eit)
				if event:
					if cfg.pdconly.value and not event.getPdcPil():
						continue
					if timer_event.begin != event.getBeginTime() - margin_before:
						changed_txt += getChangedTxt(abs(event.getBeginTime() - margin_before - timer_event.begin), ServiceReference(service_ref).getServiceName(), timer_event.name)
						if not timer_event.isRunning(): # do not change start time when timer is recorded (instant recording 'infinitely' then cancel timer due it)
							timer_event.begin = event.getBeginTime() - margin_before
							changed_start += 1
						timer_event.end = event.getBeginTime() + event.getDuration() + margin_after
						session.nav.RecordTimer.timeChanged(timer_event)
						changed_end += 1
		if changed_start or changed_end:
			msg = ngettext("Refreshed %d timer events start time", "Refreshed %d timer events start times", changed_start) % changed_start
			msg += ngettext(" and %s end time", " and %s end times", changed_end) % changed_end
			if cfg.log.value:
				saveLog(time_now(True) + msg + '\n' + changed_txt)
		return msg

def Make_Test(session):
		if installedEpgRefresh and epgrefresh.isRunning():
			return _("Not possible - EPGRefresh is running.")
		changed = 0
		msg = _("No changes needed...")
		timers_txt = ""
		epgcache = eEPGCache.getInstance()
		for timer_event in session.nav.RecordTimer.timer_list:
			if timer_event.eit:
				service_ref = timer_event.service_ref and timer_event.service_ref.ref
				event = epgcache.lookupEventId(service_ref, timer_event.eit)
				if event:
					if timer_event.begin != event.getBeginTime() - margin_before:
						delta = (event.getBeginTime() - margin_before - timer_event.begin)
						minuts = delta//60
						secs = delta%60
						changed += 1
						timers_txt += ("%s*%s " % (rC,fC) if timer_event.isRunning() else "") + timer_event.name[:80] + " " + "[%s:%02d]\n" % (minuts, secs)
		if changed:
			msg = ngettext("Need refresh %s timer event:", "Need refresh %s timer events:", changed) % changed
			msg += "\n\n"
			msg += "%s" % timers_txt
		return msg

FRIENDLY = {
	"/media/hdd": _("Harddisk"),
	"/media/usb": _("USB"),
	}

def getLocationChoices():
	result = []
	for line in open('/proc/mounts', 'r'):
		items = line.split()
		if items[1].startswith('/media'):
			desc = FRIENDLY.get(items[1], items[1])
			if items[0].startswith('//'):
				desc += ' (*)'
			result.append((items[1], desc))
		elif items[1] == '/' and items[0].startswith('/dev/'):
			# Box that has a rootfs mounted from a device
			desc = _("root")
			# On a 7025, that'd be the harddisk or CF
			if items[0].startswith('/dev/hdc'):
				desc = _("CF")
			elif items[0].startswith('/dev/hda'):
				desk = _("Harddisk")
			result.append((items[1], desc))
	return result

class RefreshTimersScreen(Screen):
	skin = """
	<screen name="RefreshTimersScreen" position="center,center" size="560,420" title="RefreshTimers - Manually">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red"    position="0,0"   size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_green"  position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue"   position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="text" position="10,50" size="540,360" zPosition="1" font="Regular;22" halign="left"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _("RefreshTimers - Manually")

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.quit,
				#"green": self.correction,
				"red": self.quit,
				"blue": self.correction,
				"yellow": self.test,
			}, -2)

		self["key_green"] = Label()
		self["key_red"] = Label(_("Cancel"))
		self["key_yellow"] = Label(_("Test"))
		self["key_blue"] = Label(_("Correction"))

		self['text'] = Label()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title + "  " + VERSION)

	def correction(self):
		self['text'].setText("")
		msg = Make_Correction(self.session)
		self['text'].setText(msg)

	def test(self):
		self['text'].setText("")
		msg = Make_Test(self.session)
		self['text'].setText(msg)

	def quit(self):
		self.close()

class RefreshTimersMain():
	def __init__(self):
		self.RefreshTimers = eTimer()
		self.RefreshTimers.timeout.get().append(self.refreshTimerEvents)

	def startRefreshTimers(self, session):
		self.session = session
		if cfg.enable.value:
			self.RefreshTimers.start(10000, True) # wait 10s on start enigma2

	def countDelay(self):
		clock = cfg.time.value
		return (clock[0] * 60 + clock[1]) * 1000

	def refreshTimerEvents(self):
		Make_Correction(self.session)
		delay = self.countDelay()
		self.RefreshTimers.start(delay, True)

RefreshTimers = RefreshTimersMain()
