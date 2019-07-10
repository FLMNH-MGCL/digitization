from pylibdmtx.pylibdmtx import decode
from PIL import Image

print('Start')
var = decode(Image.open('default.jpg'))
print(var.data)
print('End')
