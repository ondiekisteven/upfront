from upfront import *
import emojis
from time import time


def main(user_phone, response):
    user = UpfrontUser(user_phone, response.lower())

    last_command = user.last_command
    user_response = user.message

    if last_command == 'join':
        user.set_instance('home', -1)
        return home_menu(user.phone)
    if emojis.decode(user_response) == ':money_mouth_face:':
        items = db.get_user_items(user.phone)
        if items:
            total = get_payment_amount(user.phone)
            return payment_menu(user.phone, total)
        else:
            return f'You have not selected any items:\n\n{home_menu(user.phone)}'
    elif last_command == 'home':
        if user_response == '1':
            user.set_instance('categories', 1)
            return categories_menu(user.phone)
        elif user_response == '2':
            user.set_instance('quotation', 2)
            quotation_resp = quotation_menu(user.phone)
            print(f'Quotation resp -> {quotation_resp}')
            return quotation_menu(user.phone)
        elif user_response == '3':
            user.set_instance('delivery', 3)
            return delivery_menu()
        elif user_response == '4':
            return
        else:
            return f'Invalid response, try again\n\n{home_menu(user.phone)}'

    # ------------ begin Categories navigation ----------------
    elif last_command == 'categories':
        if user_response == '0':
            user.set_instance('home', -1)
            return home_menu(user.phone)
        rsp = category_item_menu(user.phone, int(user_response))
        if 'Invalid choice' in rsp:
            return rsp
        user.set_instance('category_items', int(user_response))
        return rsp
    elif last_command == 'category_items':

        if user_response == '0':
            user.set_instance('categories', user.last_reply)
            return categories_menu(user.phone)
        else:
            try:
                user_response = int(user_response)
            except ValueError:
                return 'Invalid input. Try again'
            try:
                cat_item_id = db.get_category_items(user.last_reply)[int(user_response-1)][0]
            except IndexError:
                return f'Not found. Try again'
            selected_item = db.get_one_cat_item(cat_item_id)
            if not selected_item:
                return 'Invalid input. Try again'
            # TODO: ADD THIS ITEM TO USER CHOICES
            user.set_instance('category_item_selected', selected_item[1])
            db.add_user_item(user.phone, selected_item[0], selected_item[1])
            message = f'You have chosen ```{selected_item[0]}``` for ```Ksh. {selected_item[1]}```'
            message = float_items(user.phone, message)
            return message + '\n\n0- Go back\n1- exit'
    elif last_command == 'category_item_selected':
        if response == '0':
            user.set_instance('categories', user.last_reply)
            return categories_menu(user.phone)
        elif response == '1':
            user.set_instance('home', -1)
            return home_menu(user.phone)
        else:
            return
    # ------------ End Categories navigation ----------------

    # ------------ begin quotation navigation ----------------
    elif last_command == 'quotation':
        if user_response == '0':
            user.set_instance('home', -1)
            return home_menu(user.phone)
        elif user_response == '1':
            total = get_payment_amount(user.phone)
            user.set_instance('confirmed quotation', user.phone)
            return payment_menu(user.phone, total)
        elif user_response == '2':
            user.set_instance('incorrect items', user.phone)
            return incorrect_items_menu(user.phone)

    elif last_command == 'confirmed quotation':
        if user_response == '0':
            # CANCELLED
            user.set_instance('home', -1)
            return home_menu(user.phone)
        elif user_response == '1':
            # USER HAS CONFIRMED PAYMENT DETAILS
            uniq = time()
            total = get_payment_amount(user.phone)
            request_id = db.initiateStkPush(str(user.phone), uniq, total, 'Test', '0')
            print(f"request_id -> {request_id}")
            db.insert_request_queue(request_id, '0')
            user.set_instance('home', -1)
            return "Enter your mpesa pin to confirm payments\nYou will be notified when we receive payments"
