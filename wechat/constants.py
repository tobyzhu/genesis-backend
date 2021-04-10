# -*- coding: utf-8 -*-
import common.constants
from genesis.settings import  BASE_DIR

# should be the same as in weixin developer center
use_dagu = False  # 使用大谷美东东账号

my_appid = 'wx2c96228775369c88'
my_secret = '32d998417a1efa1059bcaa150770ef9d'

my_mch_id='1575233481'
my_trade_type='JSAPI'
my_api_key ='32d998417a1efa1059bcaa150770ef9d'

UFDODER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 该url是微信下单api
NOTIFY_URL = "http://localhost:8080/wechat/payment_notify"  # 微信支付结果回调接口，需要改为你的服务器上处理结果回调的方法路径
CREATE_IP = '202'  # 你服务器的IP

token = 'fkfix9jn2nVMzdfk0921Fzwik32'
my_username = 'gh_bef61927eda5'
encodingAESKey = 'EKmn6KjeDvfS7Av90ljAUwhmTDJvpSkuqE3ZE19ZQq1'

if common.constants.COMPANYID == 'youlan':
    my_appid = 'wx2c96228775369c88'
    my_secret = '05828429c23e5cd7f9c15b2ad360c28f'

    token = 'fkfix9jn2nVMzdfk0921Fzwik32'
    my_username = 'gh_bef61927eda5'
    encodingAESKey = 'EKmn6KjeDvfS7Av90ljAUwhmTDJvpSkuqE3ZE19ZQq1'

if common.constants.COMPANYID == 'yfy':
    my_appid = 'wx2c96228775369c88'
    my_secret = '05828429c23e5cd7f9c15b2ad360c28f'

    token = 'fkfix9jn2nVMzdfk0921Fzwik32'
    my_username = 'gh_bef61927eda5'
    encodingAESKey = 'EKmn6KjeDvfS7Av90ljAUwhmTDJvpSkuqE3ZE19ZQq1'

if common.constants.COMPANYID == 'demo':
    token='fkfix9jn2nVMzdfk0921Fzwik32'
    username=''
    EncodingAESKey='EKmn6KjeDvfS7Av90ljAUwhmTDJvpSkuqE3ZE19ZQq1'

APPIDLIST=(
    ('帮小主','wx2c96228775369c88'),
    ('小主咖','wx0963eedb54cee209')
)

# else:
#     token = 'fkfix9jn2nVMzdfk0921Fzwik33'
#     my_username = 'gh_d4cef29a3d87'
#     my_appid = 'wxcd864f6c078394e0'
#     my_secret = '32d998417a1efa1059bc00150770ef9d'
#     encodingAESKey = 'DYqozm9uLHBwpnCFZiaerMh5KeJGqqE1h8iceTOY09j'

wx_host=''

# wx_appid = 'wx7514c514050f9ba4'
# wx_appsecret = '1cf1870f38cc3aceafeee5d28684865f'

wx_common_appid = my_appid
wx_common_appsecret = my_secret

wx_artisan_appid = 'wxd8d8c4adcab0b3f5'
wx_artisan_appsecret = '11ac92350958c3e87285485eed398d35'

JWT_PAYLOAD_HANDLER=''
JWT_ENCODE_HANDLER=''

# APP_ID = my_appid  # 你公众账号上的appid
# MCH_ID = my_mch_id  # 你的商户号
# API_KEY = my_api_key  # 微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里
# APP_SECRECT = "32d998417a1efa1059bcaa150770ef9d"
UFDODER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 该url是微信下单api
NOTIFY_URL = "http://xxx/wechat/"  # 微信支付结果回调接口，需要改为你的服务器上处理结果回调的方法路径
CREATE_IP = '101.86.1.173'  # 你服务器的IP

# wx_common_mchid = '1575233481'
my_cert_path = BASE_DIR + '/wechat/cacert/apiclient_cert.pem'
my_cert_key_path = BASE_DIR + '/wechat/cacert/apiclient_key.pem'