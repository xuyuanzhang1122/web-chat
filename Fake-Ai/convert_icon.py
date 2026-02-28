from PIL import Image
import os

# 确保icons文件夹存在
if not os.path.exists('icons'):
    os.makedirs('icons')

# 打开PNG图像
img = Image.open('icons/logo.png')

# 转换为ICO格式并保存
img.save('icons/logo.ico', format='ICO') 