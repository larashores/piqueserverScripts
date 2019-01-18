'''
#-------------------------------------------------------------------------------
# Name:        userlogger
# Purpose:     Logs when players are on and off the server. Can find what
#              players were on the server during a specific time interval by
#              using /findusers timeinterval1 timeinterval2 day month year
#              Each time interval should be in the form hour:minute:second
#              If the intervals are the same it finds the users logged on at
#              that point in time. If day, month, or year is left out it will
#              use the current day, month, or year at the time the command is
#              used. Logs are saved on disconnect to the file specified at the
#              beginning of this script.
#
#              WARNING: YOU MUST CTRL-C EXIT THE SERVER FOR THE LOG TO SAVE. IT
#              WILL NOT SAVE IF YOU JUST EXIT THE WINDOW
#
# Author:      Gamemaster77
#-------------------------------------------------------------------------------
'''
from commands import add, admin, alias, get_player
from pyspades.constants import *
import commands
from twisted.internet import reactor
from commands import name
import os
import time
import pickle

log = r'\logs\playtime\log.dat'

@admin
def writelog(connection):
    connection.send_chat('Saving log...')
    connection.protocol.write_log()
    return 'Done Saving'
add(writelog)

def calculateseconds(connection,hour,minute,seconds):
    totalseconds=(int(hour)*3600)+(int(minute)*60)+(int(seconds))
    return totalseconds

@admin
def findusers(connection, time1, time2, day=None, month=None, year=None):
    playerlog = connection.protocol.playerlog
    seconds = getseconds()
    curyear, curmonth, curday = getdate()
    if year==None:
        year = curyear
    if month==None:
        month = curmonth
    if day==None:
        day = curday
    day = int(day)
    month = int(month)
    year = int(year)
    if not attemptlog(connection,year,month,day):
        return 'No logs for that day'
    if time1.find(':') and time2.find(':'):
        split1=time1.split(':')
        split2=time2.split(':')
        time1 = calculateseconds(connection,int(split1[0]),int(split1[1]),int(split1[2]))
        time2 = calculateseconds(connection,int(split2[0]),int(split2[1]),int(split2[2]))
        if time2<time1:
            raise TypeError()
    else:
        raise TypeError()
    players = []
    #print playerlog[year][month][day]
    for name,ip,rights,times in playerlog[year][month][day]:
        start = times['logon']
        end =times['disconnect']
        if time1<start:
            if time2>start:
                ininterval=True
            else:
                ininterval=False
        else:
            if time1<end:
                ininterval=True
            else:
                ininterval=False
        if ininterval:
            string ='('+name+ ' => ' + ip+')'
            if not string in players:
                players.append(string)
    if players:
        message = ' , '.join(players)
        message += ' were logged on'
    else:
        message = 'No one logged on at that time'
    return message
add(findusers)

def collectplayers(connection):
    players=[]
    for player in connection.protocol.players.values():
        types = []
        types_ = player.user_types
        if types_:
            for usertype in player.user_types:
                types.append(usertype)
        info = (player.name,player.address[0],types)
        players.append(info)
    return players

def attemptlog(connection,year,month,day):
    playerlog = connection.protocol.playerlog
    try:
        playerlog[year][month][day]
        return True
    except KeyError:
        try:
            playerlog[year][month]
            playerlog[year][month][day] = []
        except KeyError:
            try:
                playerlog[year]
                playerlog[year][month] = {}
                playerlog[year][month][day] = []
            except KeyError:
                playerlog[year] = {}
                playerlog[year][month] = {}
                playerlog[year][month][day] = []
        if (year, month, day) == getdate():
            players = collectplayers(connection)
            for player in players:
                if player[0] == connection.name:
                    continue
                playerlog[year][month][day].append(player+({'logon':0,'login':-1,'disconnect': 86500},))
            return True

def getdate():
    curtime = time.localtime()
    year = curtime[0]
    month = curtime[1]
    day = curtime[2]
    return (year,month,day)

def getseconds():
    curtime = time.localtime()
    seconds = (curtime[3]*3600)+(curtime[4]*60)+curtime[5]
    return seconds

def apply_script(protocol, connection, config):
    logname = os.getcwd()+log
    if os.path.exists(logname):
        print('Loading playerlog')
        logfile = open(logname, 'rb')
        player_log=pickle.load(logfile)
        logfile.close()
    else:
        print('Creating new playerlog')
        player_log = {}
    class userLogConnection(connection):
        def on_login(self, name):
            seconds = getseconds()
            year, month, day = getdate()
            attemptlog(self,year,month,day)
            self.protocol.playerlog[year][month][day].append((name,self.address[0],[],{'logon':seconds,'login':-1,'disconnect': 86500}))
            return connection.on_login(self, name)

        def on_disconnect(self):
            seconds = getseconds()
            year, month, day = getdate()
            attemptlog(self,year, month, day)
            run = 0
            for name,ip,rights,times in self.protocol.playerlog[year][month][day]:
                if (self.name == name) and (self.address[0] == ip):
                    disconnecttime = int(self.protocol.playerlog[year][month][day][run][3]['disconnect'])
                    if disconnecttime == 86500:
                       self.protocol.playerlog[year][month][day][run][3]['disconnect'] = seconds
                run += 1
            return connection.on_disconnect(self)

    class loggerProtocol(protocol):
        playerlog = player_log
        def __init__(self, *args, **kargs):
            protocol.__init__(self, *args, **kargs)
            reactor.addSystemEventTrigger('before', 'shutdown', self.write_log)
        def create_file(self, filename):
            path = os.path.split(filename)[0]
            if os.path.exists(path):
                pass
            else:
                os.makedirs(path)
            fileobj = open(filename, 'wb')
            fileobj.close()
        def endgame(self):
            players = self.players.values().copy()
            for player in players:
                player.on_disconnect()
        def write_log(self):
            self.endgame()
            logname = os.getcwd()+log
            self.create_file(logname)
            logfile = open(logname, 'wb')
            pickle.dump(self.playerlog, logfile)
            logfile.close()

    return loggerProtocol, userLogConnection