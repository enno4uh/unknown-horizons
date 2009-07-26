# ###################################################
# Copyright (C) 2009 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import fife
import horizons.main

from cursortool import CursorTool
from horizons.util.point import Point

class NavigationTool(CursorTool):
	"""The Selectiontool is used to select instances on the game screen.
	@param game: the main game Instance
	"""
	def __init__(self):
		super(NavigationTool, self).__init__()
		self.lastScroll = [0, 0]
		self.lastmoved = fife.ExactModelCoordinate()
		self.middle_scroll_active = False

		#ugly but works o_O
		class CmdListener(fife.ICommandListener): pass
		self.cmdlist = CmdListener()
		horizons.main.fife.eventmanager.addCommandListener(self.cmdlist)
		self.cmdlist.onCommand = self.onCommand

	def end(self):
		horizons.main.fife.eventmanager.removeCommandListener(self.cmdlist)
		horizons.main.session.view.autoscroll(-self.lastScroll[0], -self.lastScroll[1])
		super(NavigationTool, self).end()

	def mousePressed(self, evt):
		#print horizons.main.session.view.cam.toMapCoordinates(fife.ScreenPoint(evt.getX(), evt.getY()), False).x, horizons.main.session.view.cam.toMapCoordinates(fife.ScreenPoint(evt.getX(), evt.getY()), False).y
		if (evt.getButton() == fife.MouseEvent.MIDDLE):
			horizons.main.session.view.autoscroll(-self.lastScroll[0], -self.lastScroll[1])
			self.lastScroll = [evt.getX(), evt.getY()]
			self.middle_scroll_active = True

	def mouseReleased(self, evt):
		if (evt.getButton() == fife.MouseEvent.MIDDLE):
			self.lastScroll = [0, 0]
			CursorTool.mouseMoved(self, evt)
			self.middle_scroll_active = False

	def mouseDragged(self, evt):
		if (evt.getButton() == fife.MouseEvent.MIDDLE):
			horizons.main.session.view.scroll(self.lastScroll[0] - evt.getX(), self.lastScroll[1] - evt.getY())
			self.lastScroll = [evt.getX(), evt.getY()]
		else:
			# Else the event will mistakenly be delegated if the left mouse button is hit while
			# scrolling using the middle mouse button
			if not self.middle_scroll_active:
				NavigationTool.mouseMoved(self, evt)

	def mouseMoved(self, evt):
		mousepoint = fife.ScreenPoint(evt.getX(), evt.getY())

		# Status menu update
		current = horizons.main.session.view.cam.toMapCoordinates(mousepoint, False)
		if abs((current.x-self.lastmoved.x)**2+(current.y-self.lastmoved.y)**2) >= 4**2:
			self.lastmoved = current
			island = horizons.main.session.world.get_island(int(round(current.x)), int(round(current.y)))
			if island:
				settlement = island.get_settlement(Point(int(round(current.x)), int(round(current.y))))
				if settlement:
					horizons.main.session.ingame_gui.resourceinfo_set(settlement)
				else:
					horizons.main.session.ingame_gui.resourceinfo_set(None)
			else:
				horizons.main.session.ingame_gui.resourceinfo_set(None)
		# Mouse scrolling
		old = self.lastScroll
		new = [0, 0]
		if mousepoint.x < 5:
			new[0] -= 5 - mousepoint.x
		elif mousepoint.x >= (horizons.main.session.view.cam.getViewPort().right()-5):
			new[0] += 6 + mousepoint.x - horizons.main.session.view.cam.getViewPort().right()
		if mousepoint.y < 5:
			new[1] -= 5 - mousepoint.y
		elif mousepoint.y >= (horizons.main.session.view.cam.getViewPort().bottom()-5):
			new[1] += 6 + mousepoint.y - horizons.main.session.view.cam.getViewPort().bottom()
		new = [new[0] * 10, new[1] * 10]
		if new[0] != old[0] or new[1] != old[1]:
			horizons.main.session.view.autoscroll(new[0]-old[0], new[1]-old[1])
			self.lastScroll = new

	def mouseWheelMovedUp(self, evt):
		horizons.main.session.view.zoom_in()
		evt.consume()

	def mouseWheelMovedDown(self, evt):
		horizons.main.session.view.zoom_out()
		evt.consume()

	def onCommand(self, command):
		if command.getCommandType() == fife.CMD_APP_ICONIFIED or command.getCommandType() == fife.CMD_INPUT_FOCUS_LOST:
			old = self.lastScroll
			horizons.main.session.view.autoscroll(-old[0], -old[1])
			self.lastScroll = [0, 0]
