from upfront import *
import emojis
from time import time


def main(user_phone, response):
    user = UpfrontUser(user_phone, response.lower())

    last_command = user.last_command
    user_response = user.message

    if last_command == 'join':
        user.set_instance('home', -1)
        return {'body': [home_menu(user.phone)]}  # 7631

    elif emojis.decode(user_response) == ':handshake:':
        wallet = db.get_wallet(user.phone)[1]
        total_cost = get_payment_amount(user.phone)
        if total_cost <= wallet:
            user.set_instance('home', -1)
            db.add_transaction(user.phone, 'payment', total_cost)
            db.update_wallet_balance(user.phone, wallet - total_cost)
            if db.get_submitted(user.phone):
                db.delete_submitted(user.phone)
            db.remove_all_user_items(user.phone)
            return {'body': ['Payment has been made.',
                             f'You new wallet balance is {db.get_wallet(user.phone)[1]}',
                             home_menu(user.phone)]}

        else:
            user.set_instance('home', -1)
            return{'body': ['You have insufficient funds. Top up and try again', home_menu(user.phone)]}

    if emojis.decode(user_response).startswith(':money_mouth_face:'):
        amount = emojis.decode(user_response).replace(':money_mouth_face:', '').strip()
        print(f'Detected amount = {amount}')
        try:
            amount = int(amount)
            uniq = time()
            request_id = db.initiateStkPush(str(user.phone), uniq, amount, 'Test', '0')
            print(f"request_id -> {request_id}")
            db.insert_request_queue(request_id, '0')
            user.set_instance('home', -1)
            return {'body': ['You will receive mpesa notification asking you to enter mpesa pin, enter and conform to '
                             'continue', home_menu(user.phone)]}
        except ValueError:
            return {'body': [emojis.encode("Incorrect format. write :money_mouth_face: then amount example: "
                                           ":money_mouth_face: 100")]}
        # items = db.get_user_items(user.phone)
        # if items:
        #     total = get_payment_amount(user.phone)
        #     return payment_menu(user.phone, total)
        # else:
        #     return f'You have not selected any items:\n\n{home_menu(user.phone)}'

    elif user_response.lower().startswith('pay'):
        amount = user_response.replace('pay', '').strip()
        try:
            amount = int(amount)
            print(f'PAY COMMAND amount -> {amount}')
            uniq = time()
            request_id = db.initiateStkPush(str(user.phone), uniq, amount, 'Test', '0')
            print(f"request_id -> {request_id}")
            db.insert_request_queue(request_id, '0')
            return {'body': ['Enter your mpesa pin in the mpesa notification you receive, to top up your wallet',
                             home_menu(user.phone)]}
        except ValueError:
            return {'body': ['Incorrect format. Write *pay then amount* eg pay 1000']}

    # ------------------ home navigation ---------------------
    elif last_command == 'home':
        if user_response == '1':
            user.set_instance('categories', 1)
            return {'body': ['Service Categories', categories_menu(user.phone)]}
        elif user_response == '2':
            user.set_instance('quotation', 2)
            quotation_resp = quotation_menu(user.phone)
            print(f'Quotation resp -> {quotation_resp}')
            return {'body': ['Checkout Menu', quotation_menu(user.phone)]}
        elif user_response == '3':
            user.set_instance('my account', 3)
            return {'body': ['My Account Menu', 'Select an option below', my_account_menu()]}
        else:
            return {'body': [f'Invalid response, try again', home_menu(user.phone)]}

    # ------------ begin Categories navigation ----------------
    elif last_command == 'categories':
        if user_response == '0':
            user.set_instance('home', -1)
            return {'body': [home_menu(user.phone)]}
        rsp = category_item_menu(user.phone, int(user_response))
        if 'Invalid choice' in rsp:
            return {'body': [rsp]}
        user.set_instance('category_items', int(user_response))
        return {'body': [rsp]}
    elif last_command == 'category_items':

        if user_response == '0':
            user.set_instance('categories', user.last_reply)
            return {'body': [categories_menu(user.phone)]}
        else:
            try:
                user_response = int(user_response)
            except ValueError:
                return {'body': ['Invalid input. Try again']}
            try:
                cat_item_id = db.get_category_items(user.last_reply)[int(user_response - 1)][0]
            except IndexError:
                return {'body': [f'Not found. Try again']}
            selected_item = db.get_one_cat_item(cat_item_id)
            if not selected_item:
                return {'body': ['Invalid input. Try again']}
            user.set_instance('category_item_selected', selected_item[1])
            db.add_user_item(user.phone, selected_item[0], selected_item[1])
            message = f'You have chosen ```{selected_item[0]}``` for ```Ksh. {selected_item[1]}```'
            message = float_items(user.phone, message)
            return {'body': [message + '\n\n0- Go back\n1- Take me to main menu']}
    elif last_command == 'category_item_selected':
        if response == '0':
            user.set_instance('categories', user.last_reply)
            return {'body': [categories_menu(user.phone)]}
        elif response == '1':
            user.set_instance('home', -1)
            return {'body': [home_menu(user.phone)]}
        else:
            return {'body': ['unknown']}
    # ------------ End Categories navigation ----------------

    # ------------ begin quotation navigation ----------------
    elif last_command == 'quotation':
        if user_response == '0':
            user.set_instance('home', -1)
            return {'body': [home_menu(user.phone)]}
        elif user_response == '1':
            total = get_payment_amount(user.phone)
            user.set_instance('confirmed quotation', int(user_response))
            return {'body': [payment_menu(user.phone, total)]}
        elif user_response == '2':
            user.set_instance('incorrect items', int(user_response))
            return {'body': [incorrect_items_menu(user.phone)]}

    # ---------  if the user confirms that items selected are correct... -----------
    elif last_command == 'confirmed quotation':
        if user_response == '0':
            # CANCELLED
            user.set_instance('home', -1)
            return {'body': [home_menu(user.phone)]}
        elif user_response == '2':
            total = get_payment_amount(user.phone)
            wallet = db.get_wallet(user.phone)[1]
            if wallet >= total:
                db.update_wallet_balance(user.phone, wallet - total)
                user.set_instance('home', -1)
                db.delete_submitted(user.phone)
                db.remove_all_user_items(user.phone)
                resp = f'Payment has been deducted from your wallet. Your new balance = {wallet - total}'

                return {'body': [resp, home_menu(user.phone)]}
            else:
                return {'body': [f'You balance is insufficient. You need Sh. {total - wallet} more. Send \U0001F911 '
                                 f'to deposit funds and try again. ']}

        elif user_response == '1':
            # USER HAS CONFIRMED PAYMENT DETAILS
            uniq = time()
            total = get_payment_amount(user.phone)

            wallet = db.get_wallet(user.phone)[1]

            print(f'Amount -> {total}')
            print(f'Uniq -> {uniq}')
            print(f'Phone -> {str(user.phone)}')
            request_id = db.initiateStkPush(str(user.phone), uniq, total, 'Test', '0')
            print(f"request_id -> {request_id}")
            db.insert_request_queue(request_id, '0')
            print("Done with push")
            user.set_instance('home', -1)
            db.remove_all_user_items(user.phone)
            if db.get_submitted(user.phone):
                db.delete_submitted(user.phone)
            return {'body': ["Enter your mpesa pin to confirm payments\nYou will be notified when we "
                    "receive payments", home_menu(user.phone)]}

    # ---------- if selected items are not correct -----------------
    # ---------- Has an option to remove items  -----------------
    elif last_command == 'incorrect items':
        if user_response == '0':
            user.set_instance('home', -1)
            return {'body': ['OK, lets go back', home_menu(user.phone)]}
        else:
            # lets get what item was selected:
            try:
                user_response = int(user_response)
            except ValueError:
                return {'body': ['Invalid input. Try again']}
            item = db.get_user_items(user.phone)[user_response-1]

            if item:
                db.remove_user_item(user.phone, item[1])
                items = db.get_user_items(user.phone)
                if items:
                    user.set_instance('quotation', 2)
                    return {'body': [quotation_menu(user.phone)]}
                else:
                    user.set_instance('categories', 2)
                    return {'body': ['No items remain in your cart. Select items from the categories to continue',
                                     categories_menu(user.phone)]}
            else:
                user.set_instance('home', -1)
                return {'body': ['An error occurred when removing your items', home_menu(user.phone)]}

    # ---------------------- MY ACCOUNT NAVIGATION -------------------
    elif last_command == 'my account':
        if user_response == '1':
            wallet = db.get_wallet(user.phone)
            details = f'Here are your details:\n\nPhone number -> +{wallet[0]}\nBalance -> {wallet[1]}'
            user.set_instance('my account', 3)
            return {'body': [details, my_account_menu()]}
        elif user_response == '2':
            transactions = db.get_transactions(user.phone)
            detail = f'Here is a statement summary of your account\n\n'
            for index, item in enumerate(transactions):
                detail += f'{index+1}. +{item[1]}- {item[2]} - sh.{item[3]}\n'
            user.set_instance('home', -1)
            return {'body': [detail, home_menu(user.phone)]}
        else:
            return {'body': ['Invalid input. Try again']}
