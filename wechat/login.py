# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
from flask import Flask, redirect, request, url_for
from requests import request

from weixin.login import WeixinLogin
from wechat.constants import wx_appid,wx_appsecret

# import wechat as Weixin


app = Flask(__name__)
# app='wechat'
print(app)

app_id = wx_appid
app_secret = wx_appsecret
wx_login = WeixinLogin(app_id, app_secret)

# config = dict(WEIXIN_APP_ID='', WEIXIN_APP_SECRET='')
# weixin = Weixin(config)

@app.route("/login")
def login():
    openid = request.cookies.get("openid")
    next = request.args.get("next") or request.referrer or "/",
    if openid:
        return redirect(next)

    callback = url_for("authorized", next=next, _external=True)
    url = wx_login.authorize(callback, "snsapi_base")
    return redirect(url)


@app.route("/authorized")
def authorized():
    code = request.args.get("code")
    if not code:
        return "ERR_INVALID_CODE", 400
    next = request.args.get("next", "/")
    data = wx_login.access_token(code)
    openid = data.openid
    resp = redirect(next)
    expires = datetime.now() + timedelta(days=1)
    resp.set_cookie("openid", openid, expires=expires)
    return resp