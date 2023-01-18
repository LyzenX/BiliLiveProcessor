# 如果你的显卡是N卡，且正确安装了显卡驱动，请设为True，这样能用GPU来渲染视频，速度会快些
# 如果是其他显卡，或者显卡不支持Cuda，或者驱动不能支持Cuda，请设为False
# 如果该项为True时无法正常渲染，请设为False
n_cuda = True

# 复制一个ffmpeg到工作目录下
# 如果你已经安装ffmpeg并将其添加到了环境变量中，可以设为False以延长硬盘寿命
copy_ffmpeg = True

# 字体
font_name = '微软雅黑'
# 最大弹幕行数
max_danmu_line = 9999

# 输出码率
bps = '5824k'

# 如果多个视频分辨率不一致，将他们统一成的分辨率，会根据实际情况(横屏还是竖屏)，调整长、短边是高还是宽
# 长边
default_res_length = 1920
# 短边
default_res_width = 1080

# 在1080p模式下，(大)弹幕的大小(整数，像素)，会随实际分辨率缩放
danmu_size_default = 80
# 在1080p横屏模式下，小弹幕的大小(整数，像素)，会随实际分辨率缩放
small_danmu_size_default = 40
