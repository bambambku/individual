from __future__ import print_function
import time
import json
from forms import RegistrationForm, LoginForm, BmiForm
from flask import Flask, render_template, request, redirect, g, url_for, redirect, session, flash
from flask_session import Session
from flask_mqtt import Mqtt
import ssl
import sqlite3
from user import *
from datetime import datetime
from db import *
import bcrypt
import sys
from loging import *
from flask import current_app
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)

app.config['SECRET_KEY'] = 'be07a2373dc6594eb7cfb2a2'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config['MQTT_BROKER_URL'] = "88d6cfe158be4e04bed7f19cd1b68d7d.s1.eu.hivemq.cloud"  # URL for HiveMQ cluster
app.config['MQTT_USERNAME'] = "wyderek"  # From the credentials created in HiveMQ
app.config['MQTT_PASSWORD'] = "SHUMichaelF1"  # From the credentials created in HiveMQ
app.config[
    'MQTT_CLIENT_ID'] = "88d6cfe158be4e04bed7f19cd1b68d7d"  # Must be unique for any client that connects to the cluster
app.config['MQTT_BROKER_PORT'] = 8883  # MQTT port for encrypted traffic
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_TLS_INSECURE'] = False
app.config['MQTT_TLS_CA_CERTS'] = 'isrgrootx1.pem'  # CA for HiveMQ, read: https://letsencrypt.org/about/
app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLSv1_2
app.config['MQTT_TLS_CIPHERS'] = None

# MQTT functionaliteis
mqtt = Mqtt(app)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc), flush=True)
    mqtt.subscribe("home/test")  # We are subscribing to the 'home/test' topic which we made up here
    mqtt.subscribe("home/caught")


def handle_users(fname, lname, tag):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO Users(Fname, Lname, Tag, Date, Time) VALUES (?,?,?,?)",
                   [fname, lname, tag, datetime.now().date(), datetime.now().strftime('%H:%M')])
        db.commit()

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    if str(message.topic) == "home/caught":
        data = message.payload
        datadict = json.loads(data)
        fname = datadict[0]
        lname = datadict[1]
        tag = datadict[2]
        handle_users(fname, lname, tag)


@app.route('/caught')
def caught():
    db = get_db()
    data = db.execute('SELECT Fname, Lname, Tag, Date, Time FROM Users').fetchall()
    db.commit()
    print(data, flush=True)
    return render_template('caught.html', data=data)
