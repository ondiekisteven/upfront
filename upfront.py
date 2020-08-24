import db


class UpfrontUser:
    def __init__(self, phone, message):
        self.phone = phone
        self.message = message
        self._last_command = None
        self._last_reply = None
        user = db.get_instance(self.phone)
        if user:
            self._last_command = user[1]
            self._last_reply = user[2]
        else:
            print(f"{self.phone} -> {self.message}")
            db.add_instance(self.phone, "join", -1)

            user = db.get_instance(self.phone)
            self._last_reply = user[2]
            self._last_command = user[1]

    @property
    def last_command(self):
        return self._last_command

    @property
    def last_reply(self):
        return self._last_reply

    def set_instance(self, new_command, new_reply):
        db.update_instance(self.phone, new_command, new_reply)


def float_items(user_phone, menu):
    sItems = db.get_user_items(user_phone)
    if sItems:
        menu += f'\n\n_Selected items: ('
        total = 0
        for item in sItems:
            menu += f'{item[1][:12]}, '
            total += item[2]
        menu += f')_ *Total: Sh. {total}*\n_Reply with \U0001F911 to submit them_\n'
    return menu


def direct_payment_float(user_phone, menu):
    sItems = db.get_user_items(user_phone)
    if sItems:
        menu += f'\n\n_Selected items: ('
        total = 0
        for item in sItems:
            menu += f'{item[1][:12]}, '
            total += item[2]
        menu += f')_ *Total: Sh. {total}*'
    return menu


def home_menu(user_phone):
    menu = """
Select an option:
1. Services
2. Get quotation
3. Ask for delivery
4. Ask for office/company clean up
    """

    return float_items(user_phone, menu)


def quotation_menu(phone):
    items = db.get_user_items(phone)
    if not items:
        return 'You have not selected any items yet. Go back and click services to select items\n\n0 - Go back'
    message = 'You have selected the following\n'
    total = 0
    i = 1
    for item in items:
        message += f'{i}. {item[1]} -> Sh. {item[2]}\n'
        total += item[2]
        i += 1
    message += f'\nTotal Cost: -> Ksh {total}\n\nDoes this look correct?\n1 -> Yes it is ok\n2 -> No'
    return message


def incorrect_items_menu(phone):
    message = 'Choose an item from below to remove\n'
    items = db.get_user_items(user_phone=phone)
    i = 1
    for item in items:
        message += f'{i}. {item[1]} -> Sh. {item[2]}'
        i += 1

    message += '\n\n0 - Take me to main menu'
    return message


def get_payment_amount(phone):
    user_items = db.get_user_items(phone)
    total = 0
    for item in user_items:
        total += item[2]
    return total


def payment_menu(user_phone, amount):
    menu = "Payment Summary\n"
    menu += f"Phone number: {user_phone}\n"
    menu += f"Amount: {amount}"

    return menu + "\n\n 1- confirm\n0 - Exit"


def services_menu():
    return "This is the cleaning services menu"


def delivery_menu():
    return "This is the delivery menu"


def categories_menu(user_phone):
    menu = "Select one category below\n"
    categories = db.get_categories()
    for number, name in categories:
        menu += f'{number}. {name}\n'
    menu = float_items(user_phone, menu)
    menu += f'\n\n0 - Go back'

    return menu


def category_item_menu(user_phone, cat_id):
    cat_items = db.get_category_items(cat_id)
    if cat_items:
        menu = "Reply with a number to add item to your liset:\n\n"
        for index, item in enumerate(cat_items):
            menu += f'{index+1}. {item[2]} - Sh. {item[3]}\n'

        menu = float_items(user_phone, menu)
        menu += '\n\n0- Go back'
        return menu
    else:
        msg = f"Invalid choice. Try again\n\n{categories_menu()}"
        return msg
