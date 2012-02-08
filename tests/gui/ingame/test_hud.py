# ###################################################
# Copyright (C) 2012 The Unknown Horizons Team
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

from tests.gui import gui_test


@gui_test(use_dev_map=True, timeout=60)
def test_hud(gui):
	"""
	Click on some buttons at the ingame menu.
	"""
	gui.trigger('mainhud', 'zoomOut/action/default')
	gui.trigger('mainhud', 'zoomIn/action/default')
	gui.trigger('mainhud', 'rotateRight/action/default')
	gui.trigger('mainhud', 'rotateLeft/action/default')

	gui.trigger('mainhud', 'logbook/action/default')
	gui.trigger('captains_log', 'okButton/action/default')

	gui.trigger('mainhud', 'build/action/default')
	gui.trigger('mainhud', 'diplomacyButton/action/default')
