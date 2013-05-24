# Implement methods for posting to an arbitrary location here. This code can do almost anything desired so long as
# the input is a string.


#Example implementation of outputting to a RESTful interface.
def postJson(msg):
    import requests
    import json
    import time
    import logging

    logger = logging.getLogger(__name__)
    endpoint = "http://endpoint.url"
    retransmissions = 10

    jsonMsg = {'body': {'log': str.strip(msg)}, 'metadata': {'app-id': 'LOFT',
               'message-type': 'log'},
               'destination': {'exchange': 'test'}}
    try:
        result = requests.post(endpoint, data=json.dumps(jsonMsg))

        while result.status_code != 200 and retransmissions > 0:
            logger.error("Invalid response: " + str(result.status_code) + " for message " + jsonMsg + " to " + endpoint + "  Retransmission attempts remaining: " + str(retransmissions) + "...")
            #wait 2 seconds and attempt to repost
            time.sleep(2)
            result = requests.post(endpoint, data=json.dumps(jsonMsg))

            retransmissions -= 1

        if retransmissions == 0:
            logger.error("Unable to send. Dropping message " + jsonMsg)

    except:
        #if we hit this there was some kind of server error that prevented a result object
        logger.error("Post to producer failed. Dropping message " + jsonMsg)


#Implementation for outputting to stdout
def postToStdOut(msg):
    print msg


#Implementation for outputting to a file
def writeToFile(msg):
    fo = open(r'/path/to/file.txt', 'a')
    fo.write(msg + "\n")
    fo.close()
