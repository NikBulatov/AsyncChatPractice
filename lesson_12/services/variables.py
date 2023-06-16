DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = ""
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 4096
ENCODING = "utf-8"

# JIM constants
ACTION = "action"
TIME = "time"
USER = "user"
ACCOUNT_NAME = "account_name"
SENDER = "sender"
RECEIVER = "to"
ALERT = "alert"
ERROR = "error"
PRESENCE = "presence"
RESPONSE = "response"
MESSAGE_TEXT = "mess_text"
MESSAGE = 'message'
USER_LOGIN = "user_login"

# JIM actions
EXIT = "exit"
GET_CONTACTS = "get_contacts"
ADD_CONTACT = "add_contacts"
DEL_CONTACTS = "del_contacts"

# Responses
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
RESPONSE_404 = {RESPONSE: 404, ERROR: None}
