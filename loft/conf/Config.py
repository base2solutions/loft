#path to log files to tail
logFileNames = [
    "test/testlog1.log",
    "test/testlog2.log",
    "test/testlog3.log",
]

#State inspector TTL in seconds
ttl = 300

#LOFT logging level. Can be DEBUG, INFO, WARN
loftLogLevel = 'DEBUG'

#Path to loft PID file
loftPID = '/var/run/loft.pid'


#Implement the logic to be executed on msg delivery. Implementations should be defined in Outputs.py
def outputMethod(msg):
    import Outputs
    Outputs.postToStdOut(msg)
