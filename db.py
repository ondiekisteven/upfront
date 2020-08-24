import pymysql
from loadConf import *


def getDb():
    return pymysql.connect(maindb_host(), maindb_user(), maindb_pass(), maindb_db())


# def getDb():
#     return pymysql.connect('localhost', 'root', '', 'upfront')


def get_categories():
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM categories')
    return cursor.fetchall()


def get_category_items(cat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM category_items WHERE cat_id = {cat_id}')
    return cursor.fetchall()


def get_one_cat_item(item_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT item_name, item_price FROM category_items WHERE item_id = {item_id}')
    return cursor.fetchone()


def get_services():
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM services')
    return cursor.fetchall()


def get_service_items(service_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM service_items WHERE service_id={service_id}')
    return cursor.fetchall()


def add_instance(phone, command, reply):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO instance (customer_phone, last_command, last_reply) VALUES ({phone}, "{command}", {reply})')
    db.commit()


def get_instance(phone):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM instance WHERE customer_phone = {phone}')
    return cursor.fetchone()


def update_instance(phone, new_command, new_reply):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE instance SET last_command = "{new_command}", last_reply = {new_reply}\
     WHERE customer_phone = {phone}')
    db.commit()


def add_user_item(user_phone, item_name, item_price):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO user_items (user_phone, item_name, item_price)\
     VALUES ({user_phone}, "{item_name}", {item_price})')
    db.commit()


def get_user_items(user_phone):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT user_phone, item_name, item_price FROM user_items WHERE user_phone = {user_phone}')
    return cursor.fetchall()


def remove_user_item(user_phone, item_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM user_items WHERE user_phone = {user_phone} AND item_name = "{item_name}"')
    db.commit()


def add_submitted(phone, amount):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO submitted (phone, amount) VALUES ({phone}, {amount})')
    db.commit()


def get_submitted(phone):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * from submitted WHERE phone = {phone}')
    return cursor.fetchone()


def update_submitted(phone, new_amount):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE submitted SET amount = {new_amount} WHERE phone = {phone}')
    db.commit()


def delete_submitted(phone):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM submitted WHERE phone = {phone}')
    db.commit()


# -------------------------------- STK PUSH DATABASE ------------------------------------
def getSTKDB():
    return pymysql.connect(stkdb_host(), stkdb_user(), stkdb_pass(), stkdb_db())


def initiateStkPush(phone, ref, amount, desc, status):
    db = getSTKDB()
    cursor = db.cursor()
    cursor.execute(f"insert into stk_requests (phone_number,account_reference,amount,transaction_desc,status) values ('{phone}','{ref}','{amount}','{desc}','{status}')")
    db.commit()
    return cursor.lastrowid


def insert_db_queue(orig, dest, msg, msg_direction):
    db = getSTKDB()
    cursor = db.cursor()
    cursor.execute(f"insert into dbqueue (Originator,Destination,Message,MessageDirection) values('{orig}','{dest}','{msg}','{msg_direction}')")
    db.commit()


def insert_request_queue(request_id, status):
    db = getSTKDB()
    cursor = db.cursor()
    cursor.execute(f"insert into stk_requests_queue (request_id,status) values ('{request_id}','{status}');")
    db.commit()


def check_payment():
    db = getSTKDB()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM transactions t join transactions_queue tq on tq.transaction_id = t.id")
    return cursor.fetchone()

#
# from time import time
# uniq = time()
# request_id = initiateStkPush(str('254745021668'), uniq, '5', 'Test', '0')
# print(f"request_id -> {request_id}")
# insert_request_queue(request_id, '0')
