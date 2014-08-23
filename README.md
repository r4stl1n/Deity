Deity
=====

Deity is a kippo plugin that identifies dictionary attacks against it then issues 
the same attack against the attacker. After it gains access it can execute additional
commands.

Kippo: Is a ssh honeypot

Install:

    Copy deity.py into kippo/dblog.
    Added the following lines to your

    ```
    [database_deity]
    logfile = deity.log
    timeoutTime = 5
    ```
