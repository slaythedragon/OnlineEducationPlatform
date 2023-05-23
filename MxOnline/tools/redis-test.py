import redis
# 设置charset和decode_responses，将值进行类型转换，不然默认为bytes类型，输出为b'123'
r = redis.Redis(host='localhost', port=6379, db=0, charset="utf8", decode_responses=True)
r.set('mobile', '123')
# 设置过期时间为1秒
r.expire("mobile", 1)
import time
# 休眠1秒
time.sleep(1)
print(r.get('mobile'))
# 运行，输出None