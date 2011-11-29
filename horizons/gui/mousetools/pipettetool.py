# ###################################################
# Copyright (C) 2011 The Unknown Horizons Team
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

from fife import fife

import horizons.main

from horizons.entities import Entities
from horizons.gui.mousetools import SelectionTool, BuildingTool,  NavigationTool


class PipetteTool(NavigationTool):
	"""Tool to select buildings in order to build another building of
	the type of the selected building"""
	HIGHLIGHT_COLOR = (0, 200, 90)

	def __init__(self, session):
		super(PipetteTool, self).__init__(session)
		self.session.gui.on_escape = self.on_escape
		self.renderer = session.view.renderer['InstanceRenderer']
		horizons.main.fife.set_cursor('pipette')

	def end(self):
		super(PipetteTool, self).end()

	def on_escape(self):
		self._remove_coloring()
		horizons.main.fife.set_cursor('default')
		self.session.cursor = SelectionTool(self.session)

	def mouseMoved(self,  evt):
		self.update_coloring(evt)

	def mousePressed(self,  evt):
		if evt.getButton() == fife.MouseEvent.LEFT:
			obj = self._get_object(evt)
			if obj:
				# clean up before end, it could interfere with other colorings
				self._remove_coloring()
				self.session.cursor = BuildingTool(self.session, \
				                                   Entities.buildings[obj.id])
			evt.consume()
		elif evt.getButton() == fife.MouseEvent.RIGHT:
			self.on_escape()
			evt.consume()
		else:
			super(PipetteTool,  self).mouseClicked(evt)

	def _get_object(self, evt):
		for obj in self.get_hover_instances(evt):
			if obj.id in Entities.buildings:
				return obj
		return None

	def update_coloring(self, evt):
		obj = self._get_object(evt)
		if obj:
			self._remove_coloring()
			self._add_coloring(obj)

	def _add_coloring(self,  obj):
		self.renderer.addColored(obj.fife_instance, *self.__class__.HIGHLIGHT_COLOR)

	def _remove_coloring(self):
		self.renderer.removeAllColored()