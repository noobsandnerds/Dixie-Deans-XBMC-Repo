# TV Portal EPG Converter
# Copyright (C) 2016 Lee Randall (whufclee)
#

#  I M P O R T A N T :

#  You are free to use this code under the rules set out in the license below.
#  However under NO circumstances should you remove this license!

#  GPL:
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
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html

# Global imports
import xbmc, xbmcgui, os, xbmcaddon
import time, datetime, re, shutil, csv
import dixie, sfile
import calendar as cal
import xml.etree.ElementTree as ET

from sqlite3 import dbapi2 as sqlite
from time import mktime


# Global variables
AddonID     =  'script.tvportal'
ADDON       =  xbmcaddon.Addon(id=AddonID)
ADDONS      =  xbmc.translatePath('special://home/addons/')
USERDATA    =  xbmc.translatePath('special://profile/')
ADDON_DATA  =  xbmc.translatePath(os.path.join(USERDATA,'addon_data'))
dbpath      =  xbmc.translatePath(os.path.join(ADDON_DATA,AddonID,'program.db'))
xmlpath     =  ADDON.getSetting('xmlpath')
offset      =  ADDON.getSetting('offset')
dialog      =  xbmcgui.Dialog()
dp          =  xbmcgui.DialogProgress()
updateicon  =  os.path.join(ADDONS,AddonID,'resources','update.png')
chanxmlfile =  os.path.join(ADDON_DATA,AddonID,'chan.xml')
catsxmlfile =  os.path.join(ADDON_DATA,AddonID,'cats.xml')
xmlmaster   =  os.path.join(ADDONS,AddonID,'resources','chan.xml')
catsmaster  =  os.path.join(ADDONS,AddonID,'resources','cats.xml')
csvfile     =  os.path.join(ADDON_DATA,AddonID,'programs.csv')
path        =  dixie.GetChannelFolder()
chan        =  os.path.join(path, 'channels')
stop        =  0
chanchange  =  0
catschange  =  0
listpercent =  1
listcount   =  1

# Check if the xml is badly formatted and attempt to fix
def Fix_XML():
    if xmlpath != '':
        readfile   = open(xmlpath,'r')
        xmlfile    = readfile.read()
        readfile.close()

        if '?t' in xmlfile:
            print"### ?t found in xml file, replacing with 'and'"
            xmlfilenew = xmlfile.replace('?t', 'and')
            writefile  = open(xmlpath,'w+')
            writefile.write(xmlfilenew)
            witefile.close()
##########################################################################################
# Function to convert timestamp into proper integer that can be used for schedules
def Time_Convert(starttime):
# Split the time from the string that also contains the time difference
    starttime, diff  = starttime.split(' ')

    year             = starttime[:4]
    month            = starttime[4:6]
    day              = starttime[6:8]
    hour             = starttime[8:10]
    minute           = starttime[10:12]
    secs             = starttime[12:14]

# Convert the time diff factor into an integer we can work with
    diff             = int(diff[:-2])+int(offset)
    starttime        = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(secs))
    starttime        = starttime + datetime.timedelta(hours=diff)
    starttime        = time.mktime(starttime.timetuple())

    return int(starttime)
##########################################################################################
# Initialise the database calls
def DB_Open():
    global cur
    global con
    con = sqlite.connect(dbpath)
    cur = con.cursor()
##########################################################################################
# Check if item already exists in database
def updateDB(chan, s_date):
    entryexists = 0
    cur.execute('select channel, start_date from programs where channel LIKE "'+chan+'" and start_date="'+s_date+'";')
    try:
        row = cur.fetchone()
        if row:
            return True
    except:
        return False
##########################################################################################
# Work out how many days worth of guides we have available
def Get_Dates(mode):
    DB_Open()
    emptydb  = 0
    datelist = []
    cur.execute("SELECT MIN(start_date) FROM programs;")
    mindate  = cur.fetchone()[0]

    mindate = datetime.datetime.fromtimestamp(mindate)
    year1   = str(mindate)[:4]
    month1  = str(mindate)[5:7]
    day1    = str(mindate)[8:10]


    cur.execute("SELECT MAX(start_date) FROM programs;")
    maxdate = cur.fetchone()[0]

    maxdate = datetime.datetime.fromtimestamp(maxdate)
    year2   = str(maxdate)[:4]
    month2  = str(maxdate)[5:7]
    day2    = str(maxdate)[8:10]

    d1      = datetime.date(int(year1), int(month1), int(day1))
    d2      = datetime.date(int(year2), int(month2), int(day2))
    diff    = d2 - d1
    print "### Successfully grabbed dates, now inserting into db"

# Grab the time now so we can update the db with timestamp
    nowtime     = cal.timegm(datetime.datetime.timetuple(datetime.datetime.now()))
    cleantime   = str(nowtime)

# Insert our dates into the db so the epg can scroll forward in time
    for i in range(diff.days + 1):
        newdate = (d1 + datetime.timedelta(i)).isoformat()
        if mode == 0:
            print"### Attempting to update records for: "+str(newdate)
            cur.execute('update updates set source=?, date=?, programs_updated=? where date LIKE "'+str(newdate)+'";', ['dixie.ALL CHANNELS',str(newdate),cleantime])
            con.commit()
            print"### Successfully updated rows"
        if mode == 1:
            print"### New database, lets create new entries"
            cur.execute("insert into updates (source, date, programs_updated) values (?, ?, ?)", ['dixie.ALL CHANNELS',str(newdate),cleantime] )
            con.commit()
            print"### Successfully inserted rows"
    cur.close()
    con.close()
##########################################################################################
### ADDON STARTS HERE ###

# Remove the channel folders so we can repopulate. All mappings will be lost unless set in the master chan.xml
if not os.path.exists(catsxmlfile):
    shutil.copyfile(catsmaster,catsxmlfile)
try:
    os.remove(os.path.join(ADDON_DATA, AddonID, 'settings.cfg'))
except:
    print"### No settings.cfg file to remove"
#if sfile.exists(chan):
#    xbmc.executebuiltin('Dialog.Show(busydialog)')
#    sfile.rmtree(chan)
#    xbmc.executebuiltin('Dialog.Close(busydialog)')

# Check database isn't locked and continue if possible
if os.path.exists(dbpath):
    try:
        os.rename(dbpath,dbpath+'1')
        os.rename(dbpath+'1',dbpath)
        print"### Database not in use, we can continue"
    except:
        print"### Database in use, Kodi needs a restart, if that doesn't work you'll need to restart your system."
        dialog.ok(ADDON.getLocalizedString(30813),ADDON.getLocalizedString(30814))
        stop = 1

if stop == 0:
    xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30807)+","+ADDON.getLocalizedString(30811)+",10000,"+updateicon+")")
    xbmc.executebuiltin("ActivateWindow(busydialog)")

# Grab the xml source, differenet sources require different methods of conversion
    with open(xmlpath) as myfile:
        head = str([next(myfile) for x in xrange(5)])
        xmlsource = str(re.compile('<tv source-info-name="(.+?)"').findall(head))
        xmlsource = str(xmlsource).replace('[','').replace(']','')
        print"XML TV SOURCE: "+xmlsource        

# Initialise the Elemettree params
    xbmc.executebuiltin('Dialog.Show(busydialog)')
# Initial parse of XML
    try:
        tree         =  ET.parse(xmlpath)
    except:
        print"### Badly formed XML file, trying to fix..."
        Fix_XML()
        tree         =  ET.parse(xmlpath)

# Get root item of tree
    root         =  tree.getroot()

# Grab all channels in XML
    try:
        channels   =  root.findall("./channel")
    except:
        print"### Badly formed XML file, trying to fix channels..."
        Fix_XML()
        channels = root.findall("./channel")        
    channelcount =  len(channels)

# Grab all programmes in XML
    try:
        programmes   =  root.findall("./programme")
    except:
        print"### Badly formed XML file, trying to fix programmes..."
        Fix_XML()
        programmes = root.findall("./programme")        

# Get total amount of programmes
    listingcount =  len(programmes)
    xbmc.executebuiltin('Dialog.Close(busydialog)')

# If the database already exists givet the option of doing a fresh import or add to existing
    mode = 0
    try:
        cur.close()
        con.close()
    except:
        print "Database not open, we can continue"
    if os.path.exists(dbpath):
        mode = dialog.yesno('Fresh Listings OR Update?','[COLOR=dodgerblue]'+str(listingcount)+"[/COLOR] programmes in [COLOR=dodgerblue]"+str(channelcount)+"[/COLOR] channels found.",'Do you want to do a clean update of the listings or are you just adding more channels from another xml?',yeslabel='Fresh Listings',nolabel='Adding Channels')
        if mode == 1:
            try:
                os.remove(dbpath)
                print "### Successfully deleted database"
            except:
                print "### FAILED: Database in use, Kodi needs a restart. If that doesn't work you'll need to restart your system."
                dialog.ok(ADDON.getLocalizedString(30813),ADDON.getLocalizedString(30814))
                stop = 1
            try:
                os.remove(chanxmlfile)
            except:
                print"### No chans.xml file to delete, lets continue"
            shutil.copyfile(xmlmaster,chanxmlfile)
#            try:
#                shutil.rmtree(os.path.join(ADDON_DATA,AddonID,'channels'))
#            except:
#                print"No channels folder to delete"
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    if (mode == 1) or (not os.path.exists(dbpath)):
# Set mode as 1 if the db didn't exist as we need this later
        mode = 1

# Create the main database
        DB_Open()
        versionvalues = [1,4,0]
        try:
            cur.execute('create table programs(channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, image_large TEXT, image_small TEXT, source TEXT, subTitle TEXT);')
            con.commit()
            cur.execute('create table updates(id INTEGER, source TEXT, date TEXT, programs_updated TIMESTAMP, PRIMARY KEY(id));')
            con.commit()
            cur.execute('create table version(major INTEGER, minor INTEGER, patch INTEGER);')
            con.commit()
            cur.execute("insert into version (major, minor, patch) values (?, ?, ?);", versionvalues)
            con.commit()

        except:
            print"### Valid program.db file exists"

        cur.close()
        con.close()

# If database is not locked lets continue
    if stop == 0:

# Read main chan.xml into memory so we can add any new channels
        if not os.path.exists(chanxmlfile):
            shutil.copyfile(xmlmaster,chanxmlfile)
        chanxml     =  open(chanxmlfile,'r')
        content     = chanxml.read()
        chanxml.close()

        writefile   = open(chanxmlfile,'w+')
        replacefile = content.replace('</tv>','')
        writefile.write(replacefile)
        writefile.close()
        writefile   = open(chanxmlfile,'a')

# Read cats.xml into memory so we can add any new channels
        catsxml     = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'r')
        content2    = catsxml.read()
        catsxml.close()

        writefile2  = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'w+')
        replacefile = content2.replace('</Document>','')
        writefile2.write(replacefile)
        writefile2.close()
        writefile2  = open(os.path.join(ADDON_DATA,AddonID,'cats.xml'),'a')

# Set a temporary list matching channel id with real name
        print "Creating List of channels"
        tempchans    = []
        print"### Channels Found: "+str(channelcount)
        xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30816)+str(channelcount)+","+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
        for channel in channels:
            channelid   = channel.get("id")
            displayname = channel.findall('display-name')
            if len(displayname) > 3 and displayname[3]!='Independent' and not 'Affiliate' in displayname[3] and displayname[3]!='Satellite' and displayname[3]!='Sports Satellite' :
                displayname = displayname[3].text.encode('ascii', 'ignore').replace('&','&amp;').replace("'",'').replace(",",'').replace(".",'')
            else:
                displayname = displayname[0].text.encode('ascii', 'ignore').replace('&','&amp;').replace("'",'').replace(",",'').replace(".",'')

            if displayname in tempchans:
                displayname  = 'donotadd'

            if not displayname in tempchans:
                tempchans.append([channelid,displayname])
# Add channel to chan.xml file
                if not '<channel id="'+str(displayname)+'">' in content:
                    writefile.write('  <channel id="'+displayname+'">\n    <display-name lang="en">'+displayname+'</display-name>\n  </channel>\n')
# Add channel to cats.xml file
                if not '<channel>'+str(displayname)+'</channel>' in content2:
                    writefile2.write(' <cats>\n    <category>Uncategorised</category>\n    <channel>'+displayname+'</channel>\n </cats>\n')
            else:
                print"### Duplicate channel - skipping "+str(displayname)


        writefile.write('</tv>')
        writefile.close()
        writefile2.write('</Document>')
        writefile2.close()

# Loop through and grab each channel listing and add to array
        xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30815)+","+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
        currentlist  = []
        print"### Total Listings to scan in: "+str(listingcount)
        xbmc.executebuiltin("XBMC.Notification("+ADDON.getLocalizedString(30816)+"[COLOR=dodgerblue]"+str(listingcount)+"[/COLOR],"+ADDON.getLocalizedString(30812)+",10000,"+updateicon+")")
        writetofile = open(csvfile,'w+')
        dp.create('Converting XML','','Please wait...','')
        writetofile.write('channel,title,start_date,end_date,description,image_large,image_small,source,subTitle')
        for programme in programmes:
#            try:
                icon = 'special://home/addons/'+AddonID+'/resources/dummy.png'
                starttime  = programme.get("start")
                starttime2 = Time_Convert(starttime)
                endtime    = programme.get("stop")
                endtime2   = Time_Convert(endtime)
                channel    = programme.get("channel").encode('ascii', 'ignore')
                try:
                    title  = programme.find('title').text.encode('ascii', 'ignore')
                except:
                    title = "No information available"
                try:
                    subtitle = programme.find('sub-title').text.encode('ascii', 'ignore')
                except:
                    subtitle = ''
                desc = programme.findtext('desc', default='No programme information available').encode('ascii', 'ignore')
                for icon in programme.iter('icon'):
                    icon = str(icon.attrib).replace("{'src': '",'').replace("'}",'')

# Convert the channel id to real channel name
                for matching in tempchans:
                    if matching[0] == channel:
                        cleanchan = str(matching[1])

# Check if this already exists in the database
                if str(cleanchan)!='donotadd':
                    writetofile.write('\n"'+str(cleanchan)+'","'+str(title)+'",'+str(starttime2)+','+str(endtime2)+',"'+str(desc)+'",,'+str(icon)+',dixie.ALL CHANNELS,'+subtitle+',')

                listcount += 1
                if listcount == int(listingcount/100):
#                    print"### "+str(listpercent)+" percent of TV guide exported to csv"
                    listcount = 0
                    dp.update(listpercent,'','','')
                    listpercent = listpercent+1

#            except:
#                try:
#                    print"### FAILED to pull details for item: "+str(title)+": "+str(subtitle)
#                except:
#                    print"### FAILED to import #"+str(listcount)
#                listcount += 1

        writetofile.close()

# Import the newly created csv file
        with open(csvfile,'rb') as fin:
            dr = csv.DictReader(fin) # comma is default delimiter
            to_db = [(i['channel'], i['title'],i['start_date'], i['end_date'], i['description'],i['image_large'], i['image_small'], i['source'], i['subTitle']) for i in dr]

        DB_Open()
        cur.executemany("INSERT INTO programs (channel,title,start_date,end_date,description,image_large,image_small,source,subTitle) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        con.commit()
        cur.execute("DELETE FROM programs WHERE RowID NOT IN (SELECT MIN(RowID) FROM programs GROUP BY channel,start_date,end_date);")
        con.commit()            
        cur.close()
        con.close()

# Insert relevant records into the updates table, if we don't do this we can't move forward in time in the EPG
        Get_Dates(mode)

        openepg = dialog.yesno(ADDON.getLocalizedString(30819),ADDON.getLocalizedString(30820))
        if openepg:
            xbmc.executebuiltin('RunAddon('+AddonID+")'")