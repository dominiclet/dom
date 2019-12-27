from datetime import datetime

# intialize an empty list (which will be used as container for dictionaries)
channels = []
messages = []

class Channel:
    def __init__(self, channelname, createdby):
        self.channelname = channelname
        self.createdby = createdby
        self.created = datetime.now()

    # add to list of dictionaries to display at Homepage
    def add(self):
        dict = {
        "channelname" : self.channelname,
        "createdby" : self.createdby,
        "created" : self.created,
        }
        channels.append(dict)


class Message:
    def __init__(self, message, messageby, channelname, created):
        self.message = message
        self.messageby = messageby
        self.channelname = channelname
        self.created = created

    # makes dictionary, appends to list, then return dictionary
    def add(self):
        dict = {
        'message' : self.message,
        'messageby' : self.messageby,
        'channelname' : self.channelname,
        'created' : self.created
        }
        messages.append(dict)

        return dict

# returns a list of message history in that channel
def history(channelname, created):
    messagehistory = []
    for message in messages:
        if message['channelname'] == channelname and message['created'] == created:
            dict = {
            'message' : message['message'],
            'messageby' : message['messageby']
            }
            messagehistory.append(dict)

    return messagehistory
