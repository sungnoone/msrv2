#-*- coding:utf-8 -*-

import sys, os
from flask import Flask, jsonify, Response
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

import datetime

import conf

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

APP_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE_FULL_PATH = APP_PATH+"/msrv2.log"
LOG_SUB_FUNCTION_PATH = APP_PATH+"/function.log"
LOG_SEND_MAIL = APP_PATH+"/sendmail.log"
LOG_CHECK_USER = APP_PATH+"/checkuser.log"
LOG_DB_OPERATE = APP_PATH+"/db.log"


#=============================== test service =========================================

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
        client = MongoClient(conf.TEST_DB_IP, conf.TEST_DB_PORT)
        db = client[conf.TEST_DB_NAME]
        collection = db[conf.TEST_DB_COLLECTION_NAME]
        client.close()
        return "Mongodb test connection successful! -- "
    except Exception as e:
        return str(e)


@app.route('/msrv2/test/fileupload/' , methods=["POST"])
@cross_origin()
def test_fileupload():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write('>>>...MODULE:test_fileupload()'+'\r\n')
    #request_data = len(request.files)
    log.write(str(len(request.files))+'\r\n')
    log.close()
    return 'file upload!'


#=============================== Book & Order =========================================


# Order -- Query all
@app.route('/msrv2/order/order_query_all/')
@cross_origin()
def order_query_all():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:order_query_all()"+str(datetime.datetime.now())+"\r\n")
    try:
        #Query all data
        find_result = record_query(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, {})
        s = ""
        for post in find_result:
            s += str(post) + "</br>"
        log.close()
        return str(s)
    except Exception as e:
        log.write("Query db error! " + str(e) + "\r\n")
        log.close()
        return str("01x001")


# Order -- query by barcode
@app.route("/msrv2/order/order_query_by_barcode/", methods=["POST"])
@cross_origin()
def order_query_by_barcode():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:order_query_by_barcode()"+str(datetime.datetime.now())+"\r\n")

    try:
        request_data = request.json
        log.write("request data: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x004"

    order_find_result = record_query(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, request_data)

    if order_find_result == False:
        log.write("query fail.\r\n")
        log.close()
        return "02x005"

    if order_find_result.count() == 0:
        log.write("沒有訂單記錄.\r\n")
        log.close()
        return "02x006"

    log.write("order find result: "+str(order_find_result)+"\r\n")

    order_json = {}
    for idx, idoc in enumerate(order_find_result):
        idoc_json = bson.json_util.dumps(idoc, ensure_ascii=False)
        order_json.update({idx:idoc_json})
        log.write("%s /r/n" % order_json)
    log.close()
    return bson.json_util.dumps(order_json, ensure_ascii=False)


# Order -- Insert(new)
@app.route("/msrv2/order/order_insert/", methods=["POST"])
@cross_origin()
def order_insert():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:order_insert()"+str(datetime.datetime.now())+"\r\n")

    try:
        request_data = request.json
        log.write("request data content: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x004"

    #get barcode
    order_shipping_barcode = ""
    order_shipping_subscriber = ""
    order_shipping_address = ""
    for key, value in request_data.items():
        if key == conf.ORDER_SHIPPING_BARCODE:
            order_shipping_barcode = value
        elif key == conf.ORDER_SHIPPING_SUBSCRIBER:
            order_shipping_subscriber = value
        elif key == conf.ORDER_SHIPPING_ADDRESS:
            order_shipping_address = value

    #if exist then update it, if not exist then add
    order_find_result = record_query(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, {conf.ORDER_SHIPPING_BARCODE:order_shipping_barcode})
    if order_find_result.count() == 0:
        insert_result = record_save(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, request_data)
        if insert_result == False:
            log.write("insert fail: " + str(insert_result) + "\r\n")
            log.close()
            return "02x005"
        else:
            log.write("insert OK: " + str(insert_result) + "\r\n")
            log.close()
            return "02x000"
    else:
        update_json = {conf.ORDER_SHIPPING_SUBSCRIBER:order_shipping_subscriber , conf.ORDER_SHIPPING_ADDRESS:order_shipping_address}
        update_result = record_update(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, {conf.ORDER_SHIPPING_BARCODE:order_shipping_barcode}, update_json)
        if update_result == False:
            log.write("update fail: " + str(update_result) + "\r\n")
            log.close()
            return "02x005"
        else:
            log.write("update OK: " + str(update_result) + "\r\n")
            log.close()
            return "02x000"


# Orders -- Insert book into order
@app.route('/msrv2/book/book_insert_into_order/', methods=["POST"])
@cross_origin()
def book_insert_into_order():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write('>>>...MODULE:book_insert_into_order()'+str(datetime.datetime.now())+'\r\n')

    book_barcode = ""
    order_barcode = ""
    try:
        #sending data from client , mut be json format
        #book barcode and order barcode
        request_data = request.json
        log.write("request data content: "+str(request_data)+"\r\n")
        for key, value in request_data.items():
            if key == conf.BOOK_IN_STOCK_FIELD_BARCODE:
                book_barcode = value
            elif key == conf.ORDER_SHIPPING_BARCODE:
                order_barcode = value
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "02x004"

    #must have book barcode and order barcode
    if (book_barcode == "") or (order_barcode == ""):
        log.write("To be lack of book barcode or  order barcode"+"\r\n")
        return "02x004"

    #find book
    books_find_result = record_query(conf.DB_BOOKS, conf.COLLECTION_BOOK_STOCK, {conf.BOOK_IN_STOCK_FIELD_BARCODE:book_barcode})
    #find order
    orders_find_result = record_query(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, {conf.ORDER_SHIPPING_BARCODE:order_barcode})

    if books_find_result == False:
        log.write("query book fail.\r\n")
        log.close
        return "01x001"
    elif orders_find_result == False:
        log.write("query order fail.\r\n")
        log.close
        return "02x004"

    if books_find_result.count() == 0:
        log.write("沒有書本記錄.\r\n")
        log.close
        return "01x006"
    elif orders_find_result.count() == 0:
        log.write("沒有訂單記錄.\r\n")
        log.close
        return "02x006"

    #log.write(str(orders_find_result[0][conf.ORDER_SHIPPING_BARCODE])+"\r\n")
    s = []
    for post in orders_find_result:
        for key, value in post.items():
            if key == conf.ORDER_SHIPPING_CONTENT:
                #get original books
                s.extend(value)

    for post in books_find_result:
        for key, value in post.items():
            if key == conf.BOOK_IN_STOCK_FIELD_BARCODE:
                compare_value = value
                log.write("compare value: "+str(compare_value)+"\r\n")
                #compare if any same barcode book exist in original order content
                compare_result = array_compare_value(compare_value, s)
                if compare_result == False:
                    s.append(value)

    log.write(str(s)+"\r\n")
    #update order
    order_update_result = record_update(conf.DB_ORDERS, conf.COLLECTION_ORDER_SHIPPING, {conf.ORDER_SHIPPING_BARCODE:order_barcode}, {conf.ORDER_SHIPPING_CONTENT:s})
    if order_update_result == False:
        log.write("update order fail.\r\n")
        log.close()
        return "02x005"
    else:
        log.write(str(order_update_result)+"\r\n")
        log.close()
        return "02x000"


# Book -- Insert
@app.route("/msrv2/book/book_insert/", methods=["POST"])
@cross_origin()
def book_insert_multi():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:book_insert_multi()"+str(datetime.datetime.now())+"\r\n")

    try:
        request_data = request.json
        log.write("request data content: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "01x004"

    # write into db
    try:
        insert_result = record_save(conf.DB_BOOKS, conf.COLLECTION_BOOK_STOCK, request_data)
        log.write("insert OK: " + str(insert_result) + "\r\n")
        log.close()
        return "01x000"
    except Exception as e:
        log.write("insert fail: " + str(e) + "\r\n")
        log.close()
        return "01x005"


# Books -- Query by barcode number
@app.route('/msrv2/book/book_query_by_barcode/', methods=["POST"])
@cross_origin()
def book_query_by_barcode():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:book_query_by_barcode()"+str(datetime.datetime.now())+"\r\n")

    try:
        #sending data from client , mut be json format
        request_data = request.data
        log.write("request data type: "+str(type(request_data))+"\r\n")
        if type(request_data) is bytes:
            request_data = request_data.decode("utf-8")
        log.write("request data content: "+str(request_data)+"\r\n")
    except Exception as e:
        log.write("request data fail: "+str(e)+"\r\n")
        log.close()
        return "01x004"

    query_book_json = {conf.BOOK_IN_STOCK_FIELD_BARCODE:request_data}
    log.write("query_book_json: "+str(query_book_json)+"\r\n")
    book_find_result = record_query(conf.DB_BOOKS, conf.COLLECTION_BOOK_STOCK, query_book_json)
    log.write("book_find_result count: "+str(book_find_result.count())+"\r\n")

    book_json = {}
    for idx, idoc in enumerate(book_find_result):
        idoc_json = bson.json_util.dumps(idoc, ensure_ascii=False)
        book_json.update({idx:idoc_json})
        log.write("book_json: "+str(book_json)+"\r\n")
    log.close()
    return bson.json_util.dumps(book_json, ensure_ascii=False)


#=================================== App security service =====================================


# App validation request(app info check: user -> idfa)
@app.route("/msrv2/security/app_validation_request/", methods=["POST"])
@cross_origin()
def app_validation_request():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:app_validation_request()"+str(datetime.datetime.now())+"\r\n")

    request_data = request.json
    log.write("request data content: "+str(request_data)+"\r\n")

    if not isinstance(request_data, dict):
        log.write("Request not JSON object.\r\n")
        log.close()
        return "00x009"

    #check the app idfa is consistent with record
    app_idfa = request_data.get("Idfa")
    app_username = request_data.get("Username")
    app_password = request_data.get("Password")
    app_name = request_data.get("App_Name")

    #check user exists and password correct
    find_user_condition = {conf.ACCOUNT_FIELD_USER_NAME:app_username,
                           conf.ACCOUNT_FIELD_USER_PASSWORD:app_password}
    find_user_result = record_query(conf.DB_USERS, conf.COLLECTION_USERS, find_user_condition)
    log.write("find user count: "+str(find_user_result.count())+"\r\n")
    #check user exists
    if find_user_result.count() == 0:
        log.write("查無使用者帳號\r\n")
        log.close()
        return "00x004"
    elif find_user_result is False:
        log.write("使用者帳號查詢失敗\r\n")
        log.close()
        return "00x005"

    #get user email
    for user in find_user_result:
        user_email = str(user[conf.ACCOUNT_FIELD_USER_EMAIL])
        log.write("user email:"+str(user[conf.ACCOUNT_FIELD_USER_EMAIL])+"\r\n")

    #check app registration
    find_app_condition = {conf.APP_REGISTER_FIELD_APP_NAME:app_name,
                          conf.APP_REGISTER_FIELD_APP_IDFA:app_idfa,
                          conf.APP_REGISTER_FIELD_APP_USER:app_username}
    find_app_result = record_query(conf.DB_APPS, conf.COLLECTION_APP_REGISTER, find_app_condition)
    log.write("find app count: "+str(find_app_result.count())+"\r\n")
    if find_app_result.count() == 0:
        log.write("無符合條件APP記錄\r\n")
        #app idfa not match or have no any record for this app
        #send pass security number by email random 4 numbers
        sn = str(random.randrange(1000,9999))
        from_address = "service1@snoone.net"
        to_address = user_email
        mail_subject = "App中心密語發送"
        mail_body = "請在App中輸入下列數字：\r\n"+ str(sn)
        send_mail_result = send_mail(from_address, to_address, mail_subject, mail_body)
        #send security number to user
        if send_mail_result is False:
            log.write("密語發送失敗\r\n")
            log.close()
            return "密語發送失敗，請稍後再試。"
        # save pass word into recode, wating for user check
        now_time = datetime.datetime.now()
        log.write("query json: "+str(find_app_condition)+"\r\n")
        update_json = {conf.APP_REGISTER_FIELD_APP_NAME:app_name,
                       conf.APP_REGISTER_FIELD_APP_IDFA:app_idfa,
                       conf.APP_REGISTER_FIELD_APP_USER:app_username,
                       conf.APP_REGISTER_FIELD_Sys_Pass_Word:sn,
                       conf.APP_REGISTER_FIELD_REGISTER_TIME:now_time,
                       conf.APP_REGISTER_FIELD_ACTIVE:"false",
                       conf.APP_REGISTER_FIELD_ACTION:datetime.datetime.now()}
        log.write("update json: "+str(update_json)+"\r\n")
        register_result = record_update(conf.DB_APPS, conf.COLLECTION_APP_REGISTER, find_app_condition, update_json)
        if register_result is False:
            return "00x006"
        log.write("系統已註冊APP資訊及通關密語: "+str(register_result)+"\r\n")
        #log.write("註冊APP內容: "+str(app_register_data)+"\r\n")
        return "00x002"
    elif find_app_result is False:
        #db query fail
        log.write("APP記錄查詢失敗\r\n")
        log.close()
        return "00x003"

    #app idfa match
    #check app active status
    for record in find_app_result:
        #app idfa not active
        if record[conf.APP_REGISTER_FIELD_ACTIVE]=="false":
            return "00x008"
    #update action time

    log.close()
    return "00x000"


#force reset app pass word
@app.route("/msrv2/security/app_reset_pass_word/", methods=["POST"])
@cross_origin()
def app_reset_pass_word():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:app_reset_pass_word()"+str(datetime.datetime.now())+"\r\n")

    request_data = request.json
    log.write("request data content: "+str(request_data)+"\r\n")

    if not isinstance(request_data, dict):
        log.write("Request not JSON object.\r\n")
        log.close()
        return "00x009"

    #check the app idfa is consistent with record
    app_idfa = request_data.get("Idfa")
    app_username = request_data.get("Username")
    app_password = request_data.get("Password")
    app_name = request_data.get("App_Name")

    #check user exists and password correct
    find_user_condition = {conf.ACCOUNT_FIELD_USER_NAME:app_username,
                           conf.ACCOUNT_FIELD_USER_PASSWORD:app_password}
    find_user_result = record_query(conf.DB_USERS, conf.COLLECTION_USERS, find_user_condition)
    log.write("find user count: "+str(find_user_result.count())+"\r\n")
    #check user exists
    if find_user_result.count() == 0:
        log.write("查無使用者帳號\r\n")
        log.close()
        return "00x004"
    elif find_user_result is False:
        log.write("使用者帳號查詢失敗\r\n")
        log.close()
        return "00x005"

    #get user email
    for user in find_user_result:
        user_email = str(user[conf.ACCOUNT_FIELD_USER_EMAIL])
        log.write("user email:"+str(user[conf.ACCOUNT_FIELD_USER_EMAIL])+"\r\n")

    #generate new pass number and send
    sn = str(random.randrange(1000,9999))
    #send security number to user
    from_address = "service1@snoone.net"
    to_address = user_email
    mail_subject = "App中心密語發送"
    mail_body = "請在App中輸入下列數字：\r\n"+ str(sn)
    send_mail_result = send_mail(from_address, to_address, mail_subject, mail_body)
    if send_mail_result is False:
        log.write("密語發送失敗\r\n")
        log.close()
        return "密語發送失敗，請稍後再試。"

    #update active, action, register time, pass word
    find_app_json = {conf.APP_REGISTER_FIELD_APP_NAME:app_name,
                          conf.APP_REGISTER_FIELD_APP_IDFA:app_idfa,
                          conf.APP_REGISTER_FIELD_APP_USER:app_username}
    update_json = {conf.APP_REGISTER_FIELD_APP_NAME:app_name,
                   conf.APP_REGISTER_FIELD_APP_IDFA:app_idfa,
                   conf.APP_REGISTER_FIELD_APP_USER:app_username,
                   conf.APP_REGISTER_FIELD_Sys_Pass_Word:sn,
                   conf.APP_REGISTER_FIELD_REGISTER_TIME:datetime.datetime.now(),
                   conf.APP_REGISTER_FIELD_ACTIVE:"false",
                   conf.APP_REGISTER_FIELD_ACTION:datetime.datetime.now()}
    log.write("update json: "+str(update_json)+"\r\n")
    update_app_info_result = record_update(conf.DB_APPS, conf.COLLECTION_APP_REGISTER, find_app_json, update_json)
    log.write("update_app_info_result: "+str(update_app_info_result)+"\r\n")
    if update_app_info_result is False:
        return "00x006"

    log.close()
    return "00x002"


# App register request(pass word check)
@app.route("/msrv2/security/app_register_request/", methods=["POST"])
@cross_origin()
def app_register_request():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:app_register_request() "+str(datetime.datetime.now())+"\r\n")

    request_data = request.json
    log.write("request data content: "+str(request_data)+"\r\n")

    if not isinstance(request_data, dict):
        log.write("Request not JSON object.\r\n")
        log.close()
        return "00x009"

    app_idfa = request_data.get("Idfa")
    app_username = request_data.get("Username")
    app_password = request_data.get("Password")
    app_name = request_data.get("App_Name")
    sys_pass_word = request_data.get("Sys_Pass_Word")

    #check user exists and password correct
    find_user_condition = {conf.ACCOUNT_FIELD_USER_NAME:app_username, conf.ACCOUNT_FIELD_USER_PASSWORD:app_password}
    find_user_result = record_query(conf.DB_USERS, conf.COLLECTION_USERS, find_user_condition)
    log.write("find user count: "+str(find_user_result.count())+"\r\n")
    #check user exists
    if find_user_result.count() == 0:
        log.write("查無使用者帳號\r\n")
        log.close()
        return "00x004"
    elif find_user_result is False:
        log.write("使用者帳號查詢失敗\r\n")
        log.close()
        return "00x005"

    # check if pass word match
    query_register_record = {conf.APP_REGISTER_FIELD_APP_NAME:app_name,
                             conf.APP_REGISTER_FIELD_APP_IDFA:app_idfa,
                             conf.APP_REGISTER_FIELD_APP_USER:app_username,
                             conf.APP_REGISTER_FIELD_Sys_Pass_Word:sys_pass_word}
    log.write("find app register json: "+str(query_register_record)+"\r\n")
    query_register_record_result = record_query(conf.DB_APPS, conf.COLLECTION_APP_REGISTER, query_register_record)
    log.write("find app register count: "+str(query_register_record_result.count())+"\r\n")
    if (query_register_record_result.count() == 0) or (query_register_record_result is False):
        return "00x003"
    #count time interval
    register_time = datetime.datetime.strptime(str(query_register_record_result[0][conf.APP_REGISTER_FIELD_REGISTER_TIME]),"%Y-%m-%d %H:%M:%S.%f")
    interval = datetime.datetime.now() - register_time
    #check interval
    if interval.seconds > 180:
        log.write("使用者密語已超過有效期限-已間隔(秒): "+str(interval.seconds)+"\r\n")
        return "00x007"
    log.write("使用者通過密語驗證-間隔(秒): "+str(interval.seconds)+"\r\n")
    #update app active status and action time
    update_json = {conf.APP_REGISTER_FIELD_ACTIVE:"true",
                   conf.APP_REGISTER_FIELD_ACTION:datetime.datetime.now()}
    update_result = record_update(conf.DB_APPS, conf.COLLECTION_APP_REGISTER, query_register_record, update_json)
    log.write("更新json: "+str(update_json)+"\r\n")
    log.write("更新啟用狀態: "+str(update_result)+"\r\n")
    log.close()
    return "00x000"


#=================================== Admin ================================

# Add User Account
@app.route("/msrv2/admin/account_create/", methods=["POST"])
@cross_origin()
def account_create():
    log = open(LOG_FILE_FULL_PATH, 'a+')
    log.write(">>>...MODULE:account_create() "+str(datetime.datetime.now())+"\r\n")

    request_data = request.json
    log.write("request data type: "+str(type(request_data))+"\r\n")
    log.write("request data content: "+str(request_data)+"\r\n")

    if not isinstance(request_data, dict):
        log.write("Request not JSON object.\r\n")
        log.close()
        return False

    #save user data
    user_id = record_save(conf.DB_USERS, conf.COLLECTION_USERS, request_data)
    if user_id is False:
        log.write("Add user fail.新增使用者失敗\r\n")
        log.close()
        return False
    else:
        log.write("Add user ok.\r\n")
        log.close()
        return str(user_id)


#============================= Common Module ====================================

# Send mail function
def send_mail(from_address, to_address, mail_subject, mail_body):
    log = open(LOG_SEND_MAIL, 'a+')
    log.write(">>>...>>>...MODULE:send_mail() "+str(datetime.datetime.now())+"\r\n")
    from_address = from_address
    to_address = to_address
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = Header(mail_subject, "utf-8")
    body = MIMEText(mail_body, "plain", "utf-8")
    msg.attach(body)

    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login("service1@snoone.net", "hl20140909")
        server.sendmail(from_address, to_address, msg.as_string())
        server.close()
        log.write("信件發送完成\r\n")
    except Exception as e:
        log.write("信件發送失敗: "+str(e)+"\r\n")
        log.close()
        return False

    log.close()
    return True


#query record
def record_query(use_db, use_collection, json_content):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_query() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(json_content)+"\r\n")

    if not isinstance(json_content, dict):
        log.write("Query content not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        find_result = collection.find(json_content)
        log.write("query data OK.\r\n")
        client.close()
        log.close()
        return find_result
    except Exception as e:
        log.write("query data error: "+str(e)+"\r\n")
        log.close()
        return False


#Save record
def record_save(use_db, use_collection, json_content):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_save() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Write Content: "+str(json_content)+"\r\n")

    if not isinstance(json_content, dict):
        log.write("Write content not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        record_id = collection.insert(json_content)
        log.write("save data OK.\r\n")
        client.close()
        log.close()
        return record_id
    except Exception as e:
        log.write("save data error: "+str(e)+"\r\n")
        log.close()
        return False


#update record(if query not exist, add)
def record_update(use_db, use_collection, query_json, update_json):
    log = open(LOG_DB_OPERATE, 'a+')
    log.write(">>>...>>>...MODULE:record_update() "+str(datetime.datetime.now())+"\r\n")

    log.write("DB: "+str(use_db)+"\r\n")
    log.write("Collection: "+str(use_collection)+"\r\n")
    log.write("Query Content: "+str(query_json)+"\r\n")
    log.write("Update Content: "+str(update_json)+"\r\n")

    if not isinstance(query_json, dict):
        log.write("query not JSON object\r\n")
        log.close()
        return False

    if not isinstance(update_json, dict):
        log.write("update not JSON object\r\n")
        log.close()
        return False

    try:
        client = MongoClient(conf.DB_IP, conf.DB_PORT)
        db = client[use_db]
        collection = db[use_collection]
        update_result = collection.update(query_json, {"$set": update_json}, upsert=True, multi=True)
        log.write("update data OK.\r\n")
        client.close()
        log.close()
        return update_result
    except Exception as e:
        log.write("save data error: "+str(e)+"\r\n")
        log.close()
        return False


#delete record
def record_delete():
    return True


#ccompare json object, compare target must be json array(list) type
def json_compare_key_value(source_json, json_list):
    log = open(LOG_SUB_FUNCTION_PATH, 'a+')
    log.write(">>>...>>>...MODULE:json_compare_key_value() "+str(datetime.datetime.now())+"\r\n")
    #get key and value from source json
    for source_key, source_value in source_json.items():
        log.write("source key:"+str(source_key)+" source value:"+str(source_value)+"\r\n")
        for single_item in json_list:
            log.write("compare target item:"+str(single_item)+"\r\n")
            for key, value in single_item.items():
                log.write("compare target item key:"+str(key)+" compare target item value:"+str(value)+"\r\n")
                if key == source_key and value == source_value:
                    log.write("source json match in json list."+"\r\n")
                    log.write("source json:"+str(source_json)+"\r\n")
                    log.write("json list:"+str(json_list)+"\r\n")
                    log.close()
                    return True
    log.write("no match key/value pairs.\r\n")
    log.close()
    return False


#compare array
def array_compare_value(source_value, array):
    log = open(LOG_SUB_FUNCTION_PATH, 'a+')
    log.write(">>>...>>>...MODULE:array_compare_value() "+str(datetime.datetime.now())+"\r\n")

    log.write("compare array:"+str(array)+"\r\n")
    log.write("compare value:"+str(source_value)+"\r\n")

    for item in array:
        if item == source_value:
            return True

    log.close()
    return False

#=================================================================


if __name__ == '__main__':
    #app.run(port=8088) #production environment
    app.run(host=conf.HOST_IP, port=conf.HOST_PORT)