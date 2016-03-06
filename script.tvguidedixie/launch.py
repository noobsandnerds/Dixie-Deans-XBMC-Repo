#
#      Copyright (C) 2014 Sean Poyser and Richard Dean (write2dixie@gmail.com)
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
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc
import xbmcaddon
import xbmcgui
import urllib
import urllib2
from hashlib import md5
import socket
import os
import re
import shutil
import datetime
import download
import extract
import dixie
import getIni
import filmon
import sfile
import gui

import settings


ADDON       = dixie.ADDON
HOME        = dixie.HOME
TITLE       = dixie.TITLE
VERSION     = dixie.VERSION

skin        = dixie.SKIN
addonpath   = dixie.RESOURCES
datapath    = dixie.PROFILE
extras      = os.path.join(datapath,   'extras')
skinfolder  = os.path.join(extras,     'skins')
dest        = os.path.join(skinfolder, 'skins.zip')
default_ini = os.path.join(addonpath,  'addons.ini')
local_ini   = os.path.join(addonpath,  'local.ini')
current_ini = os.path.join(datapath,   'addons.ini')
database    = os.path.join(datapath,   'program.db')
channel_xml = os.path.join(addonpath,  'chan.xml')
image       = xbmcgui.ControlImage

FIRSTRUN = dixie.GetSetting('FIRSTRUN') == 'true'


def showChangelog(addonID=None):
    try:
        f     = open(ADDON.getAddonInfo('changelog'))
        text  = f.read()
        title = '%s - %s' % (xbmc.getLocalizedString(24054), ADDON.getAddonInfo('name'))

        showText(title, text)

    except:
        pass


def showText(heading, text):
    id = 10147

    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)

    win = xbmcgui.Window(id)

    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            # return
        except:
            pass


def CheckForChannels():
    dir    = dixie.GetChannelFolder()
    folder = os.path.join(dir, 'channels')
    files  = []
    try:    current, dirs, files = sfile.walk(folder)
    except: pass
    if len(files) == 0:
        dixie.SetSetting('updated.channels', -1) # force refresh of channels
    
    backup = os.path.join(dir, 'channels-backup')
    if not sfile.exists(backup):
        dixie.BackupChannels()


def CheckIniVersion():
    getIni.getIni()


def CheckFilmOn():
    getIni.ftvIni()


def CopyKeymap():
    return
    src = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'zOTT.xml')
    if os.path.exists(src):
        os.remove(src)

    src = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'super_favourites_menu.xml')

    if not os.path.exists(src):
        return

    dst = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), 'super_favourites_menu.xml')

    import shutil
    shutil.copyfile(src, dst)

    os.remove(src)

    xbmc.sleep(1000)
    xbmc.executebuiltin('Action(reloadkeymaps)')


def RemoveKeymap():
    return
    src = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), 'super_favourites_menu.xml')

    if not os.path.exists(src):
        return

    dst = os.path.join(xbmc.translatePath('special://userdata/keymaps'), 'super_favourites_menu.xml')

    import shutil
    shutil.copyfile(src, dst)

    os.remove(src)

    xbmc.sleep(1000)
    xbmc.executebuiltin('Action(reloadkeymaps)')


def main():
    try:
#        CheckPlugin()
        w = gui.TVGuide()
        CopyKeymap()
        w.doModal()
        RemoveKeymap()
        del w
        xbmcgui.Window(10000).clearProperty('OTT_RUNNING')
        xbmcgui.Window(10000).clearProperty('OTT_WINDOW')

    except Exception:
        raise


kodi = True
if xbmcgui.Window(10000).getProperty('OTT_KODI').lower() == 'false':
    kodi = False
xbmcgui.Window(10000).clearProperty('OTT_KODI')


#Reset Now/Next information
xbmcgui.Window(10000).setProperty('OTT_NOW_TITLE',  '')
xbmcgui.Window(10000).setProperty('OTT_NOW_TIME',   '')
xbmcgui.Window(10000).setProperty('OTT_NEXT_TITLE',  '')
xbmcgui.Window(10000).setProperty('OTT_NEXT_TIME',   '')


#Initialise the window ID that was used to launch OTT (needed for SF functionality)
xbmcgui.Window(10000).setProperty('OTT_LAUNCH_ID', str(xbmcgui.getCurrentWindowId()))


main()

filmon.logout()

