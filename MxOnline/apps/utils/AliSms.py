# -*- coding: utf-8 -*-
import json

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models


def send_single_sms(code, mobile):
    def create_client():
        config = open_api_models.Config(
            # AccessKey ID,从用户信息管理-安全信息管理中复制
            access_key_id="LTAI5tJf7j43hvncGaxrDVWB",
            # AccessKey Secret
            access_key_secret="8QcN3wTLqFyGvxdVSvZ4xz47WGvFVK"
        )
        # 访问的域名
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    client = create_client()
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        # 电话
        phone_numbers=mobile,
        # 复制出签名
        sign_name='KLearn',
        # 复制出模板code
        template_code='SMS_238462872',
        # 传入模板中的code值
        # 使用f格式化，传入code参数，要多加一对括号
        template_param=f'{{"code":"{code}"}}'
        # template_param='{"code":"9999"}'
    )
    # API返回值
    res = client.send_sms(send_sms_request)
    # 转化为字符串，再将单引号变为双引号
    res = str(res).replace("'", '"')
    # 变为json字典形式
    res_json = json.loads(res)

    return res_json


# 当这个程序被导入时，__name__不为__main__，便不会执行以下
if __name__ == "__main__":
    res = send_single_sms(2727, '18535111908')
    # 转化为字符串，再将单引号变为双引号
    res = str(res).replace("'", '"')
    # 变为json字典形式
    res_json = json.loads(res)

    # 取code的值
    code = res_json["body"]["Code"]
    print(code)
    # 取msg的值
    msg = res_json["body"]["Message"]
    print(msg)

    if code == "OK":
        print("发送成功")
    else:
        print("发送失败: {}".format(msg))

    print(res)
