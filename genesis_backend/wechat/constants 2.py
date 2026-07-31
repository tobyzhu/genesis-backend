# -*- coding: utf-8 -*-
import os

from genesis.settings import BASE_DIR

# 使用大谷美东东账号
use_dagu = False

_cert_dir = os.path.join(BASE_DIR, "wechat", "cacert")

# 与微信公众平台 / 商户平台配置一致，全部从环境变量读取（见 .env / .env.example）


def _e(name, default=""):
    return os.environ.get(name, default)


my_appid = _e("WECHAT_APPID")
my_secret = _e("WECHAT_APP_SECRET")
my_mch_id = _e("WECHAT_MCH_ID")
my_trade_type = "JSAPI"
my_api_key = _e("WECHAT_API_KEY")
token = _e("WECHAT_TOKEN")
my_username = _e("WECHAT_USERNAME")
encodingAESKey = _e("WECHAT_ENCODING_AES_KEY")

UFDODER_URL = _e("WECHAT_UFDODER_URL", "https://api.mch.weixin.qq.com/pay/unifiedorder")
NOTIFY_URL = _e("WECHAT_NOTIFY_URL", "http://localhost:8080/wechat/payment_notify")
CREATE_IP = _e("WECHAT_SPBILL_CREATE_IP", "127.0.0.1")

app_100 = _e("WECHAT_APP_100_APPID", _e("WECHAT_APPID"))
app_200 = _e("WECHAT_APP_200_APPID")
APPIDLIST = (
    ("帮小主", app_100),
    ("小主咖", app_200),
)

wx_host = ""
wx_common_appid = my_appid
wx_common_appsecret = my_secret
wx_artisan_appid = _e("WECHAT_ARTISAN_APPID")
wx_artisan_appsecret = _e("WECHAT_ARTISAN_APP_SECRET")

JWT_PAYLOAD_HANDLER = ""
JWT_ENCODE_HANDLER = ""

my_cert_path = _e(
    "WECHAT_APICLIENT_CERT", os.path.join(_cert_dir, "apiclient_cert.pem")
)
my_cert_key_path = _e(
    "WECHAT_APICLIENT_KEY", os.path.join(_cert_dir, "apiclient_key.pem")
)
