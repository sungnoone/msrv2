HOST_IP = "192.168.1.229"
HOST_PORT = 8088

TEST_DB_IP = "192.168.1.225"
TEST_DB_PORT = 27017
TEST_DB_NAME = "test2"
TEST_DB_COLLECTION_NAME = "post1"


DB_IP = "192.168.1.225"
DB_PORT = 27017


# DB -- Order
DB_ORDERS = "orders"
COLLECTION_ORDER_SHIPPING = "order_shipping"
#fields name map
ORDER_SHIPPING_BARCODE = "order_barcode"
ORDER_SHIPPING_SUBSCRIBER = "order_subscriber"
ORDER_SHIPPING_ADDRESS = "order_address"
ORDER_SHIPPING_CONTENT = "order_content"


#DB -- Books
DB_BOOKS = "books"
COLLECTION_BOOK_STOCK = "book_in_stock"
#fields name map
BOOK_IN_STOCK_FIELD_NAME = "book_name"
BOOK_IN_STOCK_FIELD_BARCODE = "book_barcode"
BOOK_IN_STOCK_FIELD_PRICE = "book_price"
BOOK_IN_STOCK_FIELD_DESCRIPTION = "book_description"


#DB -- Users
DB_USERS = "users"
COLLECTION_USERS = "account"
#fields name map
ACCOUNT_FIELD_USER_NAME = "User_Name"
ACCOUNT_FIELD_USER_PASSWORD = "User_Password"
ACCOUNT_FIELD_USER_EMAIL = "User_Email"
ACCOUNT_FIELD_USER_PHONE_MOBILE = "User_Phone_Mobile"


#DB -- Apps
DB_APPS = "apps"
COLLECTION_APP_REGISTER = "app_register"
#fields name map
APP_REGISTER_FIELD_APP_NAME = "App_Name"
APP_REGISTER_FIELD_APP_USER = "App_User"
APP_REGISTER_FIELD_APP_IDFA = "App_Idfa"
APP_REGISTER_FIELD_Sys_Pass_Word = "Sys_Pass_Word"
APP_REGISTER_FIELD_REGISTER_TIME = "Register_Time"
APP_REGISTER_FIELD_ACTIVE = "App_Active"
APP_REGISTER_FIELD_ACTION = "App_Action"


##代碼
## app security
# 00x000:記錄資訊完全符合
# 00x002:使用者身份確認但APP編號有異動或第一次註冊App資訊
# 00x003:APP資料庫查詢失敗
# 00x004:使用者身份無法確認
# 00x005:使用者資料庫查詢失敗
# 00x006:APP資料庫寫入失敗
# 00x007:通關密語已超過時限
# 00x008:IDFA未啟用

## books
# 01x000: OK
# 01x001:資料庫查詢失敗
# 01x004: request data fail
# 01x005: 資料庫插入失敗
# 01x006: 沒有書本記錄

## orders
# 02x000 OK
# 02x004 request data fail
# 02x005: 資料庫失敗
# 02x006: 沒有訂單記錄