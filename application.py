import os

from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from functions import channels, Channel, messages, Message, history
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
#initiate session
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app)

Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    #initialise a session if the user already has a displayname on local storage
    if request.method == "GET":
        return render_template("name.html")
    else:
        session.clear()
        session['name'] = request.form.get('displayname')
        if session['name']:
            return render_template("index.html", user=session['name'], channels=channels)
        return render_template("error.html", message="Failed to initialize session server-side")

@app.route("/name", methods=["GET"])
def name():
    return render_template("name.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    """Creates a channel"""
    if request.method == "POST":
        channelname = request.form.get("channel")
        channel_info = Channel(channelname, session['name'])
        # add into the list of channels
        channel_info.add()

        return render_template("index.html", channels=channels, user=session['name'])

    return render_template("create.html", name=session['name'])

@app.route("/chatroom")
def chatroom():
    channelname = request.args.get("channelname")
    createdby = request.args.get("createdby")
    created = request.args.get("created")

    # check if channel requested exists
    for count in range(len(channels)):
        c = channels[count]
        if c['channelname'] == channelname and c['createdby'] == createdby:
            break
        elif count == len(channels) - 1:
            return render_template("error.html", message="There is no such channel")


    #fetch history of messages in channel
    messages = history(channelname, created)

    # start a session based on the channelname and the created of the channels
    session['channelname'] = channelname
    session['created'] = created


    return render_template("chatroom.html", chatname=channelname, createdby=createdby, created=created, history=messages)

@app.route("/leave")
def leave():
    """leaves chatroom"""
    # end sessions
    session.pop("channelname", None)
    session.pop("created", None)

    return redirect("/")

@socketio.on("leave")
def leaveroom(data):
    room = session['channelname']
    # stop subscribing to messages
    leave_room(room)
    # leave room notification
    emit("post", session["name"] +" has left the chat", room=room)


@socketio.on("submit chat")
def submitchat(data):
    """send message to the room"""
    # log message
    chat = data['chat']
    room = data['room']
    message = Message(chat, session['name'], session['channelname'], session['created'])

    message_data = message.add()
    emit('post', message_data, room=room)

@socketio.on("join")
def join(data):
    """joins user to room so that messages are received"""
    channel = data['channel']
    user = data['user']
    join_room(channel)
    emit('join', user + " has entered the room", room=channel)


# allow for app to be initialised by running this script
if __name__ == '__main__':
    socketio.run(app)
