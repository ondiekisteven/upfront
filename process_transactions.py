import time
import signal
import sys
import pymysql
from loadConf import *

from db import get_submitted, update_submitted, delete_submitted
from whatsapp import ChatApi

import logging
import json


class BaseEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        hdlr = logging.StreamHandler()
        # formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        formatter = logging.Formatter(" %(name)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)

        signal.signal(signal.SIGINT, self.signalHandler)
        self.state = True

    def startEngine(self):
        self.logger.info("---------------------------------------------------------------------")
        self.logger.info("------------------------Engine STARTED ------------------------------")
        self.logger.info("---------------------------------------------------------------------\n\n")
        self.session = self.getSession()

        self.runEngine()

    def signalHandler(self, signal, frame):
        self.state = False
        self.stopEngine()

    def stopEngine(self):
        self.logger.info("---------------------------------------------------------------------")
        self.logger.info("------------------------Stopping Engine------------------------------")

        try:
            self.session.close()
        except:
            pass
        self.logger.info("-------------------Engine Stopped Successfully-----------------------")
        self.logger.info("---------------------------------------------------------------------")

        sys.exit(0)

    def getSession(self):
        return pymysql.connect(stkdb_host(), stkdb_user(), stkdb_pass(), stkdb_db(),
                               cursorclass=pymysql.cursors.DictCursor)

    def getDataToProcess(self):
        cursor = self.session.cursor()
        cursor.execute(f"SELECT t.* FROM transactions t join transactions_queue tq on tq.transaction_id = t.id")
        return cursor.fetchall()

    def runEngine(self):

        while self.state:
            try:
                self.session = self.getSession()
                results = self.getDataToProcess()
                for x in results:
                    self.process(x)
                self.session.close()

                sleep_time = 1
                time.sleep(sleep_time)

            except Exception as exc:
                # raise exc
                self.logger.info(exc)
                time.sleep(1)

    def log(self, x):
        self.logger.info(x)

    def process(self, trx):
        try:

            self.log(trx)
            '''SAMPLE REQUEST {'id': 7, 'TransactionType': 'Pay Bill', 'TransID': 'OHO6VZ6J4Q', 'TransTime': 
            '20200824122833', 'TransAmount': 5.0, 'BusinessShortCode': 932280, 'BillRefNumber': 'test1', 
            'InvoiceNumber': '', 'OrgAccountBalance': '2365.00', 'ThirdPartyTransID': '', 'MSISDN': '254705126329', 
            'FirstName': 'TIMOTHY', 'MiddleName': 'WAHOME', 'LastName': 'NDIRITU', 'status': 1, 'created_at': 
            datetime.datetime(2020, 8, 24, 9, 28, 35), 'updated_at': datetime.datetime(2020, 8, 24, 9, 28, 35)} '''

            mpesa_trx_id=trx['id']
            trx_id = int(trx['MSISDN'])
            trx_amt = trx['TransAmount']  # amount paid by user
            # CHECK ONLY THOSE THAT HAVE ACTIVE ACCOUNTS ON YOUR SIDE
            # isRegistered = True

            isRegistered = get_submitted(trx_id)
            user_amt = isRegistered[3]  # this is amount the user is supposed to pay

            if isRegistered:
                if trx_amt == user_amt:
                    comment = 'You have paid full amount.'
                    delete_submitted(trx_id)  # delete user record from submitted
                elif trx_amt < user_amt:
                    comment = f'You have a balance of Ksh. {user_amt - trx_amt}'
                    update_submitted(trx_id, user_amt - trx_amt)  # update with remaining money to be paid
                else:
                    comment = f'You have overpayment of Ksh. {trx_amt - user_amt}.'
                    delete_submitted(trx_id)

                self.log(f'We have received Ksh. {trx_amt}. {comment}')

                # SENDING MESSAGE TO USER
                bot = ChatApi({'messages': ['message']})
                bot.send_message(f'{trx_id}@c.us', f'We have received Ksh. {trx_amt}. {comment}')
            else:
                pass

            #  When Done, Do the this.. 
            self.deleteQueuedTrx(mpesa_trx_id)
            self.recordQueudTrxAs(mpesa_trx_id, success=True)

            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            self.logger.error(exc)
            self.log("----------ROLLBACK due to Error Above---------")

        self.log("---------------------------DONE PROCESSING------------------------------------")

    def getQueueTrx(self):
        cursor = self.session.cursor()
        cursor.execute(f"SELECT * FROM transactions t join transactions_queue tq on tq.transaction_id = t.id")
        return cursor.fetchall()

    def deleteQueuedTrx(self, transaction_id):
        cursor = self.session.cursor()
        cursor.execute(f"delete from transactions_queue where transaction_id={transaction_id}")

    def recordQueudTrxAs(self, transaction_id, success=True, response='DEFAULT'):
        cursor = self.session.cursor()
        cursor.execute(
            f"insert into {'transactions_confirmed' if success else 'transactions_faileds'} (transaction_id,response) values ({transaction_id},'{response}')")
        return cursor.lastrowid


if __name__ == '__main__':
    engine = BaseEngine()
    engine.startEngine()
