import os
import re
import subprocess
import time

import blptk.app_win
from blptk.video import Video

date_reg = r'((\d{3}[1-9]|\d{2}[1-9]\d|\d[1-9]\d{2}|[1-9]\d{3})(((0[13578]|1[02])(0[1-9]|[12]\d|3[01]))|((0[469]|11)(' \
           r'0[1-9]|[12]\d|30))|(02(0[1-9]|[1]\d|2[0-8]))))|(((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][' \
           r'048]|[3579][26])00))0229) '
date_reg = re.compile(date_reg)
time_reg = r'(-([0-1][0-9]|(2[0-3]))([0-5][0-9])([0-5][0-9])-)'
time_reg = re.compile(time_reg)
resolution_reg = r'\d+x\d+'
resolution_reg = re.compile(resolution_reg)
fps_reg = r'\d+ fps,'
fps_reg = re.compile(fps_reg)


def analyse(path, app):
    options = app.get_options()
    # 读取目录下的文件
    if path == '':
        app.insert_log("\n\n请选择目录！")
        return
    if not os.path.isdir(path):
        app.insert_log("\n\n选择的不是目录或目录不存在，请正确选择目录。")
        return
    app.set_log(path)

    videos = []
    flvs = []
    files = os.listdir(path)
    for file in files:
        if file.endswith('.flv'):
            flvs.append(file)

    if not flvs:
        app.insert_log("\n\n选择的目录没有找到视频，请重新选择。")
        return

    """
    对每个视频进行分析，判断视频是否符合要求
    视频名称中必须包含yyyyMMdd和-HHmmss-格式的数字，且没有其他相同长度数字混淆，以便排序
    每个视频流中包含分辨率、帧率、时长等信息
    """

    # 筛选视频文件
    for flv in flvs:
        date = date_reg.findall(flv)
        date_time = time_reg.findall(flv)
        if not date or not date_time:
            if not date:
                app.insert_log(f"\n\n文件【{flv}】\n没有YYYYMMDD格式的日期，是不是录播的文件设置错误，或者当前目录混入了其他视频？")
            if not date_time:
                app.insert_log(f"\n\n文件【{flv}】\n没有HHmmss格式的时间，是不是录播的文件设置错误，或者当前目录混入了其他视频？")
            app.insert_log('\n\n建议在b站录播姬的【设置】中将录制文件名格式设为【{{ name }}-{{ "now" | format_date: "yyyyMMdd" }}/{{ name '
                           '}}-{{ title }}-{{ "now" | format_date: "yyyyMMdd" }}-{{ "now" | format_date: "HHmmss" '
                           '}}-{{ "now" | format_date: "fff" }}ms.flv】')
            app.insert_log(f"\n这样录制得到的文件名示例：【哈仔十一-看看小狗！-20221125-184619-364ms.flv】")
            return
        date = int(date[0][0])
        date_time = int(date_time[0][0][1:-1])

        xml = None
        if options['danmu'] or options['small_danmu']:
            xml = flv[0:flv.index('.')]+".xml"
            if not os.path.exists(path+'\\'+xml):
                app.insert_log(f"\n\n文件【{flv}】\n没有找到对应的xml格式弹幕文件，您是否忘记了在b站录播姬的【设置】中开启了保存弹幕？"
                               f"或是该目录下混入了其他视频？或是该录播文件是由于错误产生的(请手动删除该视频文件)？")
                app.insert_log("\n\n如果您不需要渲染有弹幕版(比如没有录制弹幕)，请取消勾选【输出有弹幕版】和【横屏时输出小弹幕版】。")
                return

        videos.append(Video(flv, xml, date, date_time))

    videos.sort(key=lambda v: (v.date * 10000000 + v.time))

    # 获取视频元数据
    valid_videos = []
    app.insert_log("\n\n请检查下方各视频的顺序和数据是否符合要求：\n")
    index = 0
    ignore = 0
    warnings = 0
    for video in videos:
        r = subprocess.run(['bin/ffprobe.exe', path+"/"+video.flv], capture_output=True)
        info = str(r.stderr, "UTF-8")
        ori = info
        file_size: int = os.stat(path + '/' + video.flv).st_size
        # 从流中获取，而不是直接在元数据中读取，对于有元数据但损坏的视频，可直接忽略
        if 'Stream #0:0:' not in info:
            app.insert_log("[x]" + "-" * 45 + "\n")
            app.insert_log(video.flv)
            ignore += 1
            if file_size > 4 * 1024 * 1024:  # 文件大小超过4MB，可能不是因卡顿损坏的视频
                app.insert_log(f"无法获取视频信息，该视频可能不是损坏的，请检查该视频。已忽略({ignore})\n")
            else:
                app.insert_log(f"无法获取视频信息，已忽略({ignore})\n")
            continue

        # 分析元数据
        info = info[info.index('Stream #0:0:'):]
        # 分辨率
        resolution: list = resolution_reg.findall(info)
        if not resolution:
            app.insert_log("[x]" + "-" * 45 + "\n")
            app.insert_log(video.flv)
            ignore += 1
            app.insert_log(f"\n无法获取视频分辨率，可能是损坏文件，已忽略({ignore})\n")
            continue
        resolution: str = resolution[0]

        # 帧率
        fps: list = fps_reg.findall(info)
        if not fps:
            app.insert_log("[x]" + "-" * 45 + "\n")
            app.insert_log(video.flv)
            ignore += 1
            app.insert_log(f"\n无法获取视频帧率，可能是损坏文件，已忽略({ignore})\n")
            continue
        fps = fps[0]
        fps: str = fps[0:fps.index("fps")]

        # 时长
        if 'Duration' not in ori:
            app.insert_log("[x]" + "-" * 45 + "\n")
            app.insert_log(video.flv)
            ignore += 1
            app.insert_log(f"\n无法获取视频时长，可能是损坏文件，已忽略({ignore})\n")
            continue
        duration = ori[ori.index("Duration: ")+11:]
        duration = duration[:duration.index(",")]

        # 数据合法，显示信息
        index += 1
        app.insert_log(f"【{index}】" + "-" * (45 - index // 10) + "\n")
        app.insert_log(video.flv + "\n")
        app.insert_log(f"分辨率：{resolution}, 帧率：{fps}，时长：{duration}\n")

        if file_size < 4 * 1024 * 1024:
            app.insert_log(f"【警告】该视频文件大小过小({get_file_size_str(file_size)})，可能是部分损坏文件，"
                           f"合并成一个视频可能会导致音画不同步等问题、请尝试播放它，"
                           f"如果可以舍弃的话(比如确实损坏了或是只有超短时间、长时间卡顿)删除它并重新点击分析。\n")
            warnings += 1

        resolution: list = resolution.split("x")
        video.columns = int(resolution[0])
        video.rows = int(resolution[1])
        video.fps = int(fps.strip())
        video.duration = duration2ms(duration)

        valid_videos.append(video)

    if not valid_videos:
        app.insert_log('\n没有合法的视频，目录下没有符合要求的视频或所有视频都被忽略？\n')
        return

    # 单个视频分析完成，分割线
    app.insert_log('\n'+'='*45+'\n\n')
    # 接下来对整体进行分析，判断应该采取的合并方式

    # ------------------ 总结 ------------------ #
    """
    对于最理想的情况，所有视频分辨率、帧率都相同，无弹幕版可以直接快速无损合并
    如果分辨率或帧率中的一项不同，则无法无损合并，需要将视频转为相同分辨率、帧率才能合并
    如果相邻视频间存在过大间隙，比如15:00开播，持续1小时，而下一个视频却是在17:00开始，则可能是中途下播，而不是网络问题产生的分割
    如果分辨率比例不同，比如主播一开始不小心设为了横屏，然后切为竖屏，则可以把开头横屏的上下加上黑边，以保证分辨率一致
    """

    horizontal = 0  # 横屏时长
    vertical = 0  # 竖屏时长
    has_dif: bool = False  # 分辨率、帧率存在区别，则无法进行无损合并

    last_video = None
    for video in valid_videos:
        if last_video is None:
            last_video = video
        else:
            if last_video.rows != video.rows or last_video.columns != video.columns or last_video.fps != video.fps:
                has_dif = True

        if video.columns >= video.rows:
            horizontal += video.duration
        else:
            vertical += video.duration

    if not has_dif:
        if horizontal == 0:
            app.insert_log(f'所有视频的分辨率、帧率都相同，且为竖屏视频：{last_video.columns}x{last_video.rows} {last_video.fps}fps\n')
        elif vertical == 0:
            app.insert_log(f'所有视频的分辨率、帧率都相同，且为横屏视频：{last_video.columns}x{last_video.rows} {last_video.fps}fps\n')
    else:
        app.insert_log('所有视频存在以下不同：\n'+get_diffs(valid_videos))
        get_diffs(valid_videos)

    total_duration = vertical + horizontal
    app.insert_log(f'视频总时长：{ms2duration(total_duration)}\n\n')

    # 检查相邻视频间是否存在过长空隙
    last_time: int = 0
    last_video = None
    for video in valid_videos:
        time_arr = time.strptime(str(video.date)+' '+str(video.time), '%Y%m%d %H%M%S')
        timestamp = int(time.mktime(time_arr))
        if last_time != 0:
            if timestamp - last_time > 5 * 60:  # 相邻超过5分钟
                warnings += 1
                app.insert_log(f'【警告】视频({last_video.flv})的结尾与({video.flv})的开头间估计间隔有'
                               f'{(timestamp - last_time) // 60}分钟，请检查是否是两场不同的直播\n\n')
        last_video = video
        last_time = timestamp + video.duration // 1000

    # 分析合并方法
    if not has_dif:
        if horizontal == 0:
            app.output_method = 0
            app.insert_log('将输出竖屏视频，')
        elif vertical == 0:
            app.output_method = 1
            app.insert_log('将输出横屏视频，')
        app.fast_no_danmu = True
        app.insert_log('且无弹幕版可以快速无损合并完成。点击【生成处理文件】以生成处理文件。\n\n')
    else:
        app.fast_no_danmu = False
        if horizontal == 0:
            app.output_method = 0
            app.insert_log('将输出竖屏视频，需要更多时间和临时的储存空间进行转码。点击【生成处理文件】以生成处理文件。\n')
        elif vertical == 0:
            app.output_method = 1
            app.insert_log('将输出横屏视频，需要更多时间和临时的储存空间进行转码。点击【生成处理文件】以生成处理文件。\n')
        else:
            app.insert_log('由于同时存在横屏与竖屏视频，经分析')
            if horizontal / total_duration < 0.1:
                app.output_method = 0
                app.insert_log('竖屏视频占主导，将横屏视频上下加上黑边，最终输出竖屏视频，点击【生成处理文件】以生成处理文件。')
            elif vertical / total_duration < 0.1:
                app.output_method = 1
                app.insert_log('横屏视频占主导，将竖屏视频左右加上黑边，最终输出横屏视频，点击【生成处理文件】以生成处理文件。')
            else:
                app.output_method = -1
                app.insert_log('无法确定最终应输出横屏还是竖屏视频，为了观众的观看体验，您可以创建多个文件夹，'
                               '把横屏片段和竖屏片段放在不同文件夹后分开处理，然后分p上传。或者点击强制输出为横屏或竖屏。')
            app.insert_log('需要更多时间和临时的储存空间进行转码。\n\n')

    # 输出警告与忽略的数量
    app.insert_log(f"\n{'没有警告' if warnings == 0 else f'有{warnings}个警告'}"
                   f"{'。' if ignore == 0 else f'，有{ignore}个视频被忽略。'}\n")
    if warnings != 0 or ignore != 0:
        app.insert_log('请仔细检查以上内容。\n')

    app.videos = valid_videos
    app.analysed_path = path


def get_diffs(videos: list) -> str:
    res = ''
    last_count = 1
    last_property = None
    index = 1
    for video in videos:
        current_property = str(video.columns) + 'x' + str(video.rows) + ' ' + str(video.fps) + 'fps'
        if last_property is None:
            last_property = current_property
        elif current_property != last_property:
            if last_count == index-1:
                res += str(index-1)
            else:
                res += str(last_count) + '-' + str(index-1)
            res += ' ' + last_property + '\n'
            last_count = index
            last_property = current_property
        index += 1
    if last_count == index - 1:
        res += str(index - 1)
    else:
        res += str(last_count) + '-' + str(index - 1)
    res += ' ' + last_property + '\n'

    return res


def get_file_size_str(size: int) -> str:
    if size >= 1024 * 1024 * 1024:
        return f'{round(size / (1024 * 1024 * 1024), 2)}GiB'
    elif size >= 1024 * 1024:
        return f'{round(size / (1024 * 1024), 2)}MiB'
    elif size >= 1024:
        return f'{round(size / 1024, 2)}KiB'
    else:
        return f'{size}B'


def duration2ms(s: str) -> int:
    res: int = 0
    sec = s.split(':')
    res += int(sec[0]) * 1000 * 60 * 60
    res += int(sec[1]) * 1000 * 60
    res += float(sec[2]) * 1000
    return int(res)


def ms2duration(t: int) -> str:
    res: str = ""
    count: int = t // 1000

    temp = count // 60 // 60
    res += ("0" + str(temp) + ":") if temp < 10 else (str(temp) + ":")

    temp = count % 3600 // 60
    res += ("0" + str(temp) + ":") if temp < 10 else (str(temp) + ":")

    temp = count % 3600 % 60
    res += ("0" + str(temp)) if temp < 10 else (str(temp))

    return res
