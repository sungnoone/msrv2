#-*- coding:utf-8 -*-

import sys, os
from flask import Flask
from flask_cors import *
from pymongo import *
import json
import bson.json_util

import smtplib, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.image import MIMEImage
import random

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv2.log"

TEST_DB_IP = "192.168.1.230"
TEST_DB_PORT = 27017
TEST_DB_NAME = "test2"
TEST_DB_COLLECTION_NAME = "post1"

DB_IP = "192.168.1.230"
DB_PORT = 27017
# DB -- Order
DB_ORDER = "orders"
COLLECTION_ORDER_OUTPUT = "order_output"
#DB -- Books
DB_BOOK_NAME = "books"
COLLECTION_BOOK_STOCK = "book_in_stock"
#DB -- App Users
DB_APP = "apps"
COLLETION_APP_USERS = "app_users"





#=============================== Book & Order =========================================

@app.route('/msrv2/')
@cross_origin()
def hello_world():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write('>>>...MODULE:hello_world()'+'\r\n')
    return 'Hello World wenjen!'
    #return LOG_FILE_FULL_PATH


# Testing mongodb
@app.route('/msrv2/connect1/')
@cross_origin()
def test_connect_mongodb():
    try:
        client = MongoClient(TEST_DB_IP, TEST_DB_PORT)
        db = client[TEST_DB_NAME]
        collection = db[TEST_DB_COLLECTION_NAME]
        client.close()
        return "Mongodb test connection successful! -- "
    except Exception as e:
        return str(e)


# Order -- Query all
@app.route('/msrv2/order/order_query_all/')
@cross_origin()
def order_query_all():
    try:
        client = MongoClient(DB_IP, DB_PORT)
        db = client[TEST_DB_NAME]
        collection = db[COLLECTION_ORDER_OUTPUT]
        #Query all data
        s = ""
        for post in collection.find():
            s += str(post) + "</br>"
        client.close()
        return str(s)
    except Exception as e:
        return str(e)


# Order -- Insert multi
@app.route("/msrv2/order/order_insert_multi/", methods=["POST"])
@cross_origin()
def order_insert_multi():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:order_insert_multi()\r\n")

    try:
        request_data = request.json
        log.write("request data content: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "Remote return fail!"

    try:
        client = MongoClient(DB_IP, DB_PORT)
        db = client[DB_ORDER]
        collection = db[COLLECTION_ORDER_OUTPUT]
        post_id = collection.insert(request_data)
        client.close()
    except Exception as e:
        log.close()
        return str(e)
    log.close()

    return str("OK -- "+ str(post_id))


# Book -- Insert multi
@app.route("/msrv2/book/book_insert_multi/", methods=["POST"])
@cross_origin()
def book_insert_multi():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:book_insert_multi()\r\n")

    try:
        request_data = request.json
        log.write("request data content: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "Remote return fail!"

    try:
        client = MongoClient(DB_IP, DB_PORT)
        db = client[DB_BOOK_NAME]
        collection = db[COLLECTION_BOOK_STOCK]
        post_id = collection.insert(request_data)
        client.close()
    except Exception as e:
        log.close()
        return str(e)
    log.close()

    return str("OK -- "+ str(post_id))


#=================================== App security service =====================================

# App validation request
@app.route("/msrv2/security/app_validation_request/", methods=["POST"])
@cross_origin()
def app_validation_request():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:app_validation_request()\r\n")

    request_data = request.json
    log.write("request data content: "+str(request_data)+"\r\n")

    sn = random.randrange(1000,9999)

    # 發送信件
    msg = MIMEMultipart()
    from_address = "service1@snoone.net"
    to_address = "wenjen@hanlin.com.tw"
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = Header("App中心密語發送","utf-8")
    body = MIMEText("請在App中輸入下列數字：\r\n"+ str(sn)+ "\r\n"+ str(request_data), "plain", "utf-8")
    msg.attach(body)

    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login("service1@snoone.net", "hl20140909")
        #server.set_debuglevel(1)
        server.sendmail(from_address, to_address, msg.as_string())
        server.close()
        log.write("密語信件發送完成\r\n")
    except Exception as e:
        log.write("密語發送失敗: "+str(e)+"\r\n")
        return "密語發送失敗，稍後再試"

    log.close()
    return "OK"


# changing security id request
@app.route("/msrv2/security/id_change_request/", methods=["GET", "POST"])
@cross_origin()
def id_change_request():
    from_address = "service1@snoone.net"
    to_address = "wenjen@hanlin.com.tw"
    subject = "App Security changed"
    #msg = ("From: %s\r\nTo: %s\r\nSubject:%s\r\n Hello , This is a testing!!" % (from_address, to_address, "App安全性變更通知"))
    #msg = "Subject: testing\r\nHello , This is a testing!!"
    header = 'From: %s\n' % from_address
    header += 'To: %s\n' % ','.join(to_address)
    header += 'Subject: %s\n\n' % subject
    msg = header+ "Hello"

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login("service1@snoone.net", "hl20140909")
    #server.set_debuglevel(1)
    server.sendmail(from_address, to_address, msg)
    server.quit()

    return "OK"





#========================================================================

if __name__ == '__main__':
    #app.run(port=8088) #production environment
    app.run(host="192.168.1.229", port=8088)