# b站录播姬视频处理器
## 介绍
[b站录播姬](https://github.com/BililiveRecorder/BililiveRecorder)是一个用于b站直播的工具，它可以同时监控并自动录制多个直播间，还能录制直播时的弹幕。

而这其中有许多痛点，比如怎么将录制的弹幕渲染到视频中。<br>
幸运的是，网上有许多工具可以将xml格式的弹幕文件转换为ass字幕文件，但将字幕渲染到视频中，许多视频编辑软件要么不支持，要么渲染速度慢、渲染质量差。<br>
[ffmpeg](http://ffmpeg.org/)是一个开源的视频转码工具，用它可以快速地将将字幕渲染到视频中，但缺点是，你需要用命令行来使用它，而且，要渲染高质量的视频，需要多条指令。

但这并不是最常见的痛点。由于(主播)的网络波动，一次直播可能会分为好几个文件，严重的时候可能会有几百甚至上千个文件，这会使合并文件变得极为困难。

更更糟的是，由于b站直播会根据网络情况自动切换画质，这几百个文件中会混入不同分辨率和帧率的视频，导致它们无法直接合并。
如果是用手机直播，还会出现一会横屏一会竖屏的情况。

本软件可以自动识别并解决这些情况，并一键处理，将它们合并，根据需求生成有弹幕版、无弹幕版等最终文件。

案例：
- 有一个录播文件和xml弹幕文件，需要输出一个有弹幕的视频文件。
- 有多个720x1280 15fps的录播文件需要合并，输出一个720x1280 15fps无损合并的无弹幕版视频，和一个1080x1920 60fps的有弹幕版视频，有弹幕版提高分辨率和帧率是因为低分辨率和帧率下，弹幕看起来会模糊且一卡一卡的。
- 有多个视频，同时包含720x1280 15fps，720x1280 25fps，1080x1920 30fps等多个画质，输出1080x1920 60fps的有、无弹幕版两个视频。
- 有多个视频，多个画质，但都是16:9的横屏视频，需要输出1920x1080的大、小、无弹幕版三个视频，大弹幕版方便手机用户观看，小弹幕版方便电脑用户观看。
- 有多个视频，主播一开始不小心调成了竖屏直播，在三分钟后调回了横屏。将前面竖屏部分左右两边用黑色填充变成横屏，最终输出横屏视频。
- 有多个视频，主播到了一个网络不好的地方，手机也没拿稳，导致中间有很多文件一会横屏一会竖屏，你想要生成横屏视频。
- 处理后，会生成许多中间文件，一键将它们清理掉，只留下原始文件和合并后的有、无弹幕版视频文件。

本软件使用[niconvert](https://github.com/muzuiget/niconvert)进行弹幕转换，使用[ffmpeg](http://ffmpeg.org/)编码视频。

## 下载软件
TODO

## 使用方法
软件暂时只支持Windows平台，需要安装Python。

安装过程中注意**一定要关联Python文件以及将Python添加到环境变量中**，建议看[这篇保姆级教程](https://blog.csdn.net/weixin_49237144/article/details/122915089)。

如果你使用的是NVIDIA的显卡并且正确地安装了驱动程序，则可以使用硬件编码，速度会快一些。<br>
如果没有，或是无法正确渲染，你可以关闭硬件渲染，关闭的方式是：<br>
用文本编辑器打开config.py(或者将它的后缀名修改为.txt，改完记得将后缀名改回.py)，将`n_cuda = True`改为`n_cuda = False`。

双击`BiliLiveProcessor.pyw`，打开软件，根据提示使用。

## 注意事项
要处理的视频文件的文件名中必须包含`yyyyMMdd`格式的的日期和`-HHmmss-`的时间。

建议在b站录播姬的设置中，将录制文件名改为：
```
{{ name }}-{{ "now" | format_date: "yyyyMMdd" }}/{{ name }}-{{ title }}-{{ "now" | format_date: "yyyyMMdd" }}-{{ "now" | format_date: "HHmmss" }}-{{ "now" | format_date: "fff" }}ms.flv
```
这样录制出来的文件名称示例：`哈仔十一-看看小狗！-20221125-184619-364ms.flv`

处理过程中要生成大量中间文件，请预留足够的硬盘空间(至少原始文件总大小的三倍)。

如果录播文件中出现错误，合并后的结果可能不符合预期，比如音画不同步、到某个时刻卡住等。如果遇到这种情况，可以尝试把视频分段合并，并分p上传。

上传录播建议取得up主同意，若发生版权纠纷，与本软件无关。

## 软件截图

![](https://raw.githubusercontent.com/LyzenX/BiliLiveProcessor/main/assets/example1.jpg)

![](https://raw.githubusercontent.com/LyzenX/BiliLiveProcessor/main/assets/example2.jpg)

![](https://raw.githubusercontent.com/LyzenX/BiliLiveProcessor/main/assets/example3.jpg)

![](https://raw.githubusercontent.com/LyzenX/BiliLiveProcessor/main/assets/example4.jpg)

清理后：

![](https://raw.githubusercontent.com/LyzenX/BiliLiveProcessor/main/assets/example5.jpg)


## 开源协议
本软件使用 GPLv3 许可证。

依赖：
- [niconvert](https://github.com/muzuiget/niconvert)
- [ffmpeg](http://ffmpeg.org/)
