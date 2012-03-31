# ###################################################
# Copyright (C) 2012 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.

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

import horizons.main

from fife import fife
from horizons.world.status import StatusIcon
from horizons.constants import LAYERS

from horizons.util.messaging.message import AddStatusIcon, RemoveStatusIcon, WorldObjectDeleted, HoverInstancesChanged

class StatusIconManager(object):
	"""Manager class that manages all status icons. It listenes to AddStatusIcon
	and RemoveStatusIcon messages on the main message bus"""

	def __init__(self, session):
		self.session = session
		# {instance: [list of icons]}
		self.icons = {}
		# Renderer used to render the icons
		self.renderer = self.session.view.renderer['GenericRenderer']

		self.tooltip_instances = set() # no weakset:
		# we need to remove the tooltip always anyway, and along with it the entry here

		self.session.message_bus.subscribe_globally(AddStatusIcon, self.on_add_icon_message)
		self.session.message_bus.subscribe_globally(HoverInstancesChanged, self.on_hover_instances_changed)
		self.session.message_bus.subscribe_globally(RemoveStatusIcon, self.on_remove_icon_message)
		self.session.message_bus.subscribe_globally(WorldObjectDeleted, self.on_worldobject_deleted_message)

	def on_add_icon_message(self, message):
		"""This is called by the message bus with AddStatusIcon messages"""
		assert isinstance(message, AddStatusIcon)
		icon_instance = message.icon.instance
		if not icon_instance in self.icons:
			self.icons[icon_instance] = []
		assert not message.icon in self.icons[icon_instance]
		self.icons[icon_instance].append(message.icon)
		# Sort, make sure highest icon is at top
		self.icons[icon_instance] = sorted(self.icons[icon_instance], key=StatusIcon.get_sorting_key(), reverse=True)
		# Now render the most important one
		self.__render_status(icon_instance, self.icons[icon_instance][0])

	def on_worldobject_deleted_message(self, message):
		assert isinstance(message, WorldObjectDeleted)
		# remove icon
		if message.worldobject in self.icons:
			self.renderer.removeAll(self.get_status_string(message.worldobject))
			del self.icons[message.worldobject]
		# remove icon tooltip
		if message.worldobject in self.tooltip_instances:
			new_instances = set(i for i in self.tooltip_instances if \
			                    i is not message.worldobject)
			self.on_hover_instances_changed( HoverInstancesChanged(self, new_instances) )

	def on_remove_icon_message(self, message):
		"""Called by the MessageBus with RemoveStatusIcon messages."""
		assert isinstance(message, RemoveStatusIcon)
		icon_instance = message.instance
		if icon_instance in self.icons:
			for registered_icon in self.icons[icon_instance][:]:
				if message.icon_class is registered_icon.__class__:
					self.icons[icon_instance].remove(registered_icon)
					if len(self.icons[icon_instance]) == 0:
						# No icon left for this building, remove it
						self.renderer.removeAll(self.get_status_string(icon_instance))
						del self.icons[icon_instance]
					else:
						# Render next icon
						self.__render_status(icon_instance, self.icons[icon_instance][0])
					return

	def __render_status(self, instance, status):
		status_string = self.get_status_string(instance)

		# Clean icons
		self.renderer.removeAll(status_string)

		# pixel-offset on screen (will be constant across zoom-levels)
		rel = fife.Point(0, -30)

		layer = self.session.view.layers[LAYERS.OBJECTS]

		pos = instance.position

		# trial and error has brought me to this (it's supposed to hit the center)
		loc = fife.Location(layer)
		loc.setExactLayerCoordinates(
		  fife.ExactModelCoordinate(
		    pos.origin.x + float(pos.width) / 4,
		    pos.origin.y + float(pos.height) / 4,
		  )
		)

		node = fife.RendererNode(loc, rel)

		try: # to load an animation
			anim = horizons.main.fife.animationloader.loadResource(status.icon)
			self.renderer.addAnimation(status_string, node, anim)
		except ValueError:
			img = horizons.main.fife.imagemanager.load(status.icon)
			self.renderer.addImage(status_string, node, img)

	def get_status_string(self, instance):
		"""Returns render name for status icons of this instance"""
		status_string = "status_"+ str(id(instance))
		return status_string

	def on_hover_instances_changed(self, msg):
		"""Check if we need to display a tooltip"""
		instances = msg.instances
		dropouts = self.tooltip_instances.difference(instances)
		additions = instances.difference(self.tooltip_instances)

		# only those that have icons
		additions = (i for i in additions if i in self.icons)
		# and belong to the player
		additions = (i for i in additions if \
		             hasattr(i, "owner" ) and \
		             hasattr(i.owner, "is_local_player") and \
		             i.owner.is_local_player)

		# apply changes
		for instance in dropouts:
			self.tooltip_instances.remove(instance)
			# remove tooltip
			# TODO
			print 'remove tooltip of ', instance
		for instance in additions:
			self.tooltip_instances.add(instance)
			icons_of_instance = self.icons[instance]

			icon = max(icons_of_instance, key=StatusIcon.get_sorting_key())

			# show tooltip
			# TODO
			print 'new icon for', instance, ":", icon.helptext



