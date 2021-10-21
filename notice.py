# 邮件模板来自 樱花庄的白猫 主题 Sakura
# https://2heng.xin/


# -*- coding: utf-8 -*-
"""
@Time ： 2021/8/24 13:00
@Auth ： apecode
@File ：notice.py
@IDE ：PyCharm
@Blog：https://liiuyangxiong.cn

"""
import json
import re
from os import access, replace
import time
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from email.utils import formataddr
import requests
import config



class Notice:

    def __init__(self, admin: dict, account: dict):
        self.admin = admin,
        self.account = account

    def send(self, content):
        if self.account.get("notice") == "" or self.account.get("notice") == "local":
            return Notice.saveLocal(content)
        elif self.account.get("notice") == "mail":
            if self.admin[0]["mail"]["sendMail"] == "" and self.admin[0]["mail"]["authCode"] == "":
                print("未设置发送者邮箱信息，转为本地记录")
                Notice.saveLocal(content)
            else:
                self.send_mail(content)
        else:
            self.sendPushPlus(content)

    def send_mail(self, message: str):
        try:
            mail_template = """
                <div style="background: white; width: 95%; max-width: 800px; margin: auto auto; border-radius: 5px; border:orange 1px solid; overflow: hidden; -webkit-box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.12); box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.18); font-family : YouYuan;">
                <header style="overflow: hidden;">
                <img style="width:100%;z-index: 666;" src="https://cdn.jsdelivr.net/gh/OrientalFantasy/file/pigeon_msg/img/mail_head.jpg">
                </header>
                <div style="padding: 5px 20px;">
                <p style="position: relative;color: white;float: left;z-index: 999;background: orange;padding: 5px 30px;margin: -25px auto 0 ;box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.30)">Dear&nbsp; user_name</p>
                <br>
                <h3>签到表单于 <font style="text-decoration: none;color: orange ">sgin_time</font> 提交，表单状态：<font style="text-decoration: none;color: orange ">status</font>！</h3>
                <h3>详细信息：</h3>
                <div style="border-bottom:#ddd 1px solid;border-left:#ddd 1px solid;padding-bottom:20px;background-color:#eee;margin:15px 0px;padding-left:20px;padding-right:20px;border-top:#ddd 1px solid;border-right:#ddd 1px solid;padding-top:20px">签到状态：status</a><br>晚点名地址：address</div>
                <div style="text-align: center;">
                <img src="https://cdn.jsdelivr.net/gh/OrientalFantasy/file/pigeon_msg/img/mail_footer.png" alt="hr" style="width:100%;margin:5px auto 5px auto;display: block;">
                </div>
                <p style="font-size: 12px;text-align: center;color: #999;">本邮件为系统自动发出，请勿回复。<br>
                Copyright &copy; 2021 <a style="text-decoration:none; color: #66ccff;" target="_blank" href="https://github.com/rookiesmile/yibanAutoSgin">yibanAutoSgin</a> All Rights Reserved.</p>
                </div>
                </div>
                """

            host_server = self.admin[0]["mail"]["smtpServer"]
            # 发件人的邮箱
            sendMail = self.admin[0]["mail"]["sendMail"]
            # 邮箱的授权码
            authCode = self.admin[0]["mail"]["authCode"]
            # 收件人邮箱
            receiver = self.account.get("mail")
            # 收件人昵称
            nick = self.account.get("nick")
            # 解析传入的json
            message = json.loads(message)
            # 获取签到时间
            sgin_time = message["sgin_time"]
            # 获取状态
            status = message["status"]
            # 获取预览链接
            # sgin_URL = message["sgin_URL"]
            # 获取晚点名地址
            address = message["address"]
            # 邮件标题
            mail_title = "易班 " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + " 签到情况"
            # ssl登录
            smtp = SMTP_SSL(host_server)
            smtp.ehlo(host_server)
            smtp.login(sendMail, authCode)

            # 替换邮件模板中的字符
            rep = re.sub
            template1 = rep("user_name", nick, mail_template)# 替换用户昵称
            template2 = rep("sgin_time", sgin_time, template1)# 替换签到时间
            template3 = rep("status", status, template2)# 替换签到状态
            # template4 = rep("sgin_URL", sgin_URL, template3)# 替换预览链接
            template = rep("address", address, template3)# 替换晚点名地址

            msg = MIMEText(template, "html", 'utf-8')
            msg["Subject"] = Header(mail_title, 'utf-8')
            msg["From"] = formataddr(["某鸽子的邮件提醒", sendMail])
            msg["To"] = receiver
            smtp.sendmail(sendMail, receiver, msg.as_string())
            smtp.quit()

            # 控制台日志
            print("【邮件记录】\n" + "收件人：" + nick + "\n邮箱地址：" + receiver + "\n时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + "\n")

            return True

        except Exception as e:
            print("发送失败，转为本地记录")
            print(e)
            Notice.saveLocal(e)
            return False

    # 发送pushPlus
    def sendPushPlus(self, content: str):
        url = 'https://www.pushplus.plus/send'
        headers = {"Content-Type": "application/json"}
        data = json.dumps({
            "token": self.account.get("pushToken"),
            "title": "易班签到通知",
            "content": content,
            "template": "txt"
        })
        response = requests.post(url=url, data=data, headers=headers).json()
        if response['code'] == 200:
            return Notice.log(f"{self.account.get('mobile')}\tPush Plus发送成功！\n")
        else:
            print("发送失败，转为本地记录")
            Notice.saveLocal(content)
            return Notice.log(f"{self.account.get('mobile')}\tPush Plus发送失败！原因: {response['msg']}\n")

    @staticmethod
    def log(message: str):
        with open(file="data/logs.log", mode="a+", encoding="utf-8") as f:
            f.write(message)
            print(message)

    @staticmethod
    def saveLocal(message: str):
        with open("data/result.log", mode="a+", encoding="utf-8") as w:
            w.write(message+"\n")