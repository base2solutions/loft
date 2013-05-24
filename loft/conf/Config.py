#path to log files to tail. Must be absolute paths.
logFileNames = [
    "/path/to/testlog1.log",
    "/path/to/testlog2.log",
    "/path/to/testlog3.log",
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
    Outputs.writeToFile(msg)
