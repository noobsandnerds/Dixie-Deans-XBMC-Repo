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
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc, xbmcaddon, xbmcgui, os, re, urllib, urllib2
import time, dixie, shutil
import extract, download, login

from sqlite3 import dbapi2 as sqlite

AddonID          =  'script.tvportal'
ADDON            =  xbmcaddon.Addon(id=AddonID)
USERDATA         =  xbmc.translatePath(os.path.join('special://home/userdata',''))
ADDON_DATA       =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
ADDONS           =  xbmc.translatePath('special://home/addons')
chanxml          =  os.path.join(ADDON_DATA,AddonID,'chan.xml')
xmlmaster        =  os.path.join(ADDONS,AddonID,'resources','chan.xml')
catsxml          =  os.path.join(ADDON_DATA,AddonID,'cats.xml')
catsmaster       =  os.path.join(ADDONS,AddonID,'resources','cats.xml')
firstrun         =  os.path.join(ADDON_DATA,AddonID,'firstrun.txt')
updateicon       =  os.path.join(ADDONS,AddonID,'resources','update.png')
cookies          =  os.path.join(ADDON_DATA,AddonID,'cookies')       
dialog           =  xbmcgui.Dialog()
dbpath           =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'program.db'))

#if __name__ == '__main__':
login.o0o()
if not os.path.exists(os.path.join(ADDON_DATA,AddonID)):
    dixie.log("New addon_data folder created")
    os.makedirs(os.path.join(ADDON_DATA,AddonID))
else:
    dixie.log("addon_data already exists")

if not os.path.exists(cookies):
    os.makedirs(cookies)

#if not os.path.exists(chanxml):
#    dixie.log("Copying chan.xml to addon_data")
#    shutil.copyfile(xmlmaster, chanxml)
#else:
#    dixie.log("Chan.xml file exists in addon_data")

#if not os.path.exists(catsxml):
#    dixie.log("Copying cats.xml to addon_data")
#    shutil.copyfile(catsmaster, catsxml)
#else:
#    dixie.log("Cats.xml file exists in addon_data")

if not os.path.exists(firstrun):
    dixie.log("First Run, show OTTV message")
    dialog.ok(ADDON.getLocalizedString(30805),ADDON.getLocalizedString(30806))
    writefile=open(firstrun,'w+')
    writefile.close()
if os.path.exists(dbpath):
    dixie.log("Database exists, checking it's not already in use")
    try:
        os.rename(dbpath,dbpath+'1')
        os.rename(dbpath+'1',dbpath)
        dixie.log("Database not in use, we can continue")
        login.Oooo0O0oo00oO()
    except:
        dixie.log("Database in use, Kodi needs a restart, if that doesn't work you'll need to restart your system.")
        choice = dialog.yesno(ADDON.getLocalizedString(30821),ADDON.getLocalizedString(30822))
        if choice == 1:
            login.Oooo0O0oo00oO()
else:
    dixie.log("No database exists, opening verification")
    login.Oooo0O0oo00oO()