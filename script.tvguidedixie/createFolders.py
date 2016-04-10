#
#      Copyright (C) 2016 noobsandnerds.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Kodi; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmcgui
import xbmcaddon
import os
import dixie
import sfile

AddonID        =  'script.tvportal'
ADDON          =  xbmcaddon.Addon(id=AddonID)
SF_CHANNELS    =  ADDON.getSetting('SF_CHANNELS')
OTT_CHANNELS   =  os.path.join(dixie.GetChannelFolder(), 'channels')
dialog         =  xbmcgui.Dialog()

if SF_CHANNELS.startswith('special://'):
	SF_CHANNELS = xbmc.translatePath(SF_CHANNELS)
	
try:
    current, dirs, files = sfile.walk(OTT_CHANNELS)
except Exception, e:
    dixie.log('Failed to run script: %s' % str(e))
    
for file in files:
    if not os.path.exists(os.path.join(SF_CHANNELS,file)):
        try:
            print os.path.join(SF_CHANNELS,file)
            os.makedirs(os.path.join(SF_CHANNELS,file))
        except:
            dixie.log('### Failed to create folder for: %s' % str(file))

dialog.ok(ADDON.getLocalizedString(30809),ADDON.getLocalizedString(30810))