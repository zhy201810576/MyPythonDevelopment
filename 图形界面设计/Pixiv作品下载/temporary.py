
import base64

a = base64.b64encode('zhy08112'.encode('utf-8'))
b = base64.b64decode(a).decode('utf-8')
print(b,type(b))
