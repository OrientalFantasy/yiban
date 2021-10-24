# 原项目地址：https://github.com/apecodex/yibanAutoSgin
# 原作者：apecode.
# 原作者Blog：https://liuyangxiong.cn
#
# 本版本是基于 apecode. 的项目 yibanAutoSgin 的二次开发版本
# 仅修改了邮件模板，aes加密模块来自 https://github.com/Sricor/Yiban 感谢 Sricor 大佬！
# 新版表单加密方式和加密密钥来自 https://github.com/xk-mt 感谢！
# 

# -*- coding: utf-8 -*-
import json
import os
import time
import datetime
import util
from yiban import Yiban
import config
from notice import Notice



# ===========================================================
# Github actions 使用，本地使用请注释
# try:
#     config.account[0]["mobile"] = os.environ["YB_MOBILE"]
#     config.account[0]["password"] = os.environ["YB_PASSWORD"]
#     config.account[0]["mail"] = os.environ["YB_MAIL"]
#     config.account[0]["pushToken"] = os.environ["YB_PUSHTOKEN"]
#     config.account[0]["notice"] = os.environ["YB_NOTICE"]
# except KeyError:
#     pass
# # # ===========================================================

for ac in config.account:
    yb = Yiban(ac.get("mobile"), ac.get("password"))
    nowPeriod = util.getTimePeriod()  # 获取签到时段数值

    if nowPeriod != 0:
        login = yb.login()

        if (login["response"]) != 100:
            print(login["message"])

        else:
            notice = Notice(config.admin, ac)

            try:
                auth = yb.auth()

                if auth["code"] == 0:
                    timePeriod = util.fromIntGetTimePeriod(nowPeriod)
                    now_task = yb.getUncompletedListTime(timePeriod[0], timePeriod[1])

                    if not len(now_task["data"]):
                        print("没有找到要提交的表单")

                    else:
                        now_task_id = now_task["data"][0]["TaskId"]
                        detail = yb.getDetail(now_task_id)
                        extend = {
                            "TaskId": now_task_id,
                            "title": "任务信息",
                            "content": [
                                {"label": "任务名称", "value": detail["data"]["Title"]},
                                {"label": "发布机构", "value": detail["data"]["PubOrgName"]},
                                {"label": "发布人", "value": detail["data"]["PubPersonName"]}
                            ]
                        }
                        sb_result = yb.submitApply(config.tasks[nowPeriod - 1], extend)

                        if nowPeriod != 3:

                            if sb_result["code"] == 0:
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
	                                "nick": nick,
	                                "status": "表单签到成功",
	                                "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # 设置间隔时间
                                time.sleep(3)
                                # result = "{\"nick\" : " + nick + "\"status\" : \"提交成功\",\"sgin_time\" : " + sgin_time + "\"address\" : " + address + "\"sgin_URL\" : " + share_url + "}"
                                # notice.send(result)

                            else:
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
	                                "nick": nick,
	                                "status": "表单签到失败",
	                                "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # result = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())) + "表单提交失败！请检查\n")
                                # notice.send(time.strftime(result))
                                Notice.log(str(result))
                                # 设置间隔时间
                                time.sleep(3)
                        else:
                            # 位置签到
                            yb.photoRequirements()
                            yb.deviceState()
                            yb.signPostion()
                            ns_result = yb.nightAttendance(config.address)

                            if sb_result["code"] == 0 and ns_result["code"] == 0:
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
                                    "nick": nick,
                                    "status": "表单和位置签到成功",
                                    "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # 设置间隔时间
                                time.sleep(3)

                                # result = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) + " 表单和位置签到提交成功 url: " + share_url + " 位置: " + json.loads(config.address)["Address"] + "\n"
                                # notice.send(result)

                            elif sb_result["code"] == 0 and ns_result["code"] != 0:
                                # print(str(sb_result["data"]))
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
                                    "nick": nick,
                                    "status": "表单签到成功，位置签到失败",
                                    "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # 设置间隔时间
                                time.sleep(3)

                                # result = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) +" 表单提交成功 url: " + share_url + "\n"
                                # notice.send(result)

                            elif sb_result["code"] != 0 and ns_result["code"] == 0:
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
                                    "nick": nick,
                                    "status": "表单签到失败，位置签到成功",
                                    "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # 设置间隔时间
                                time.sleep(3)
                                # result = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))) +" 位置: " + json.loads(config.address)["Address"] + "\n"
                                # notice.send(result)

                            else:
                                nick = ac.get("nick")
                                sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                address = json.loads(config.address)["Address"]
                                result = {
                                    "nick": nick,
                                    "status": "表单和位置签到失败",
                                    "sgin_time": sgin_time,
                                    "address": address
                                    }
                                notice.send(json.dumps(result,ensure_ascii=False))
                                # 设置间隔时间
                                time.sleep(3)
                                # result = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())) + "签到失败，请检查\n")
                                # notice.send(result)

                else:
                    print("登录授权失败，请重新登录!")
                    nick = ac.get("nick")
                    sgin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                    address = json.loads(config.address)["Address"]
                    result = {
                        "nick": nick,
                        "status": "登录授权失败",
                        "sgin_time": sgin_time,
                        "address": address
                        }
                    notice.send(json.dumps(result,ensure_ascii=False))
                    # 设置间隔时间
                    time.sleep(3)
                    # notice.send(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())) + "登录授权失败，请重新登录\n"))

            except Exception as e:
                nick = ac.get("nick")
                status = nick + "状态异常！请检查易班校本化授权！" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                print(status)
                print(e)
                log = str(e) + str(status)
                Notice.saveLocal(log)
            
    else:
        print("未到签到时间")