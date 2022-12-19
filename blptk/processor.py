import os.path
import shutil

import config
import niconvert


def generate(app, output_method=None):
    # ----------------- 基本检查 ----------------- #
    analysed_path = app.analysed_path
    if analysed_path is None:
        app.set_log('未选择正确的工作目录，请点击右方的”浏览“按钮，并将目录定位到录播的目录下，并点击【分析】按钮。')
        return
    if analysed_path != app.io_frame.values():
        app.set_log('分析的工作目录与选择的工作目录不一致，是不是您在点击分析了之后又更改了工作目录？请重新点击【分析】按钮。')
        return

    if output_method is None:
        output_method = app.output_method
    videos = app.videos
    if output_method == -1:
        if videos:
            app.insert_log('\n无法生成工作文件，请尝试在高级选项中“强制生成横屏或竖屏”。\n')
        else:
            app.set_log('无法生成工作文件。')
        return

    options = app.get_options()
    if not options['no_danmu'] and not options['danmu'] and not options['small_danmu']:
        app.set_log('没有生成任何工作文件，因为所有选项都没有被勾选，既不生成有弹幕版也不生成无弹幕版。')
    if not options['no_danmu'] and not options['danmu'] and options['small_danmu'] and output_method != 1:
        app.set_log('没有生成任何工作文件，因为既不生成有弹幕版也不生成无弹幕版，且输出竖屏模式下不会生成小弹幕版。')

    # 检查文件是否还存在
    for video in videos:
        if not os.path.isfile(analysed_path + '/' + video.flv):
            app.set_log(f'文件[{video.flv}]已消失，您是不是在点击分析后把这个文件删除了？请重新点击分析。')
            return
    if options['danmu'] or options['small_danmu']:
        for video in videos:
            # 检查是否开了弹幕但在分析的时候没有开启弹幕
            if video.xml is None:
                app.set_log(f'文件{video.flv}对应的弹幕文件没有被分析到，您是否在分析前取消勾选了弹幕，但在分析后又勾选上了？请重新点击分析。')
                return
            if not os.path.isfile(analysed_path + '/' + video.xml):
                app.set_log(f'文件[{video.flv}]已消失，您是不是在点击分析后把这个文件删除了？请重新点击分析。')
                return

    # --------------- 分析生成的分辨率 --------------- #
    """
    如果所有视频的分辨率长宽比都一样，则生成的最终视频以分辨率最大的一个为准。
    否则，横屏使用1920x1080，竖屏使用1080x1920。可在配置中调整。
    """
    crr = 0  # 长宽比
    max_columns = 0
    max_rows = 0
    for video in videos:
        if crr == 0:
            crr = video.columns / video.rows
            max_columns = video.columns
            max_rows = video.rows
        else:
            if abs(crr - video.columns / video.rows) < 0.0001:
                if video.columns > max_columns:
                    max_columns = video.columns
                    max_rows = video.rows
            else:
                crr = 0
                break

    # 所有视频长宽比相同
    if crr != 0:
        if max_rows < config.default_res_width:
            max_columns = int(config.default_res_width * crr)
            max_rows = config.default_res_width
        if max_columns < config.default_res_width:
            max_rows = int(config.default_res_width / crr)
            max_columns = config.default_res_width

        _generate(app, max_columns, max_rows, output_method)
    # 长宽比不同
    else:
        if output_method == 1:
            _generate(app, config.default_res_length, config.default_res_width, output_method)
        else:
            _generate(app, config.default_res_width, config.default_res_length, output_method)


def _generate(app, columns, rows, output_method):
    videos = app.videos
    if len(videos) == 1:
        # 只有一个视频的情况
        generate_single(app, videos, columns, rows, output_method)
    else:
        # 有多个视频的情况
        generate_multi(app, videos, columns, rows, output_method)


def generate_multi(app, videos, columns, rows, output_method):
    path = app.analysed_path
    options = app.get_options()
    command = "chcp 65001\n\r"  # 调整命令行编码为UTF-8
    clear = "chcp 65001\n\r"  # 清理用命令
    crr = columns / rows  # 长宽比
    filelist_no_danmu = ''
    filelist_danmu = ''
    filelist_danmu_small = ''

    # 所有视频分辨率和帧率一致的话，就可以先无损快速合并无弹幕视频
    if app.fast_no_danmu and options['no_danmu']:
        for video in videos:
            # 为防止视频名中出现单引号，导致无法合并，将加入filelist的视频名中的单引号转义
            safe_video_name = video.flv.replace("'", "'\\''")
            filelist_no_danmu += f"file '{safe_video_name}'\n"
        generate_file(path, 'filelist0.txt', filelist_no_danmu)
        command += 'ffmpeg -y -safe 0 -f concat -i filelist0.txt -c copy "!!!无弹幕.mp4"\n\r'

    index: int = 0
    for video in videos:
        index += 1
        # 生成高质量中间文件
        # 开启了生成弹幕，或无法快速无损合并，才需要生成中间文件
        if options['danmu'] or options['small_danmu'] or not app.fast_no_danmu:
            # 生成中间文件
            if abs(video.columns / video.rows - crr) < 0.0001:
                # 分辨率比例一致，缩放即可
                command += f'ffmpeg -y -i "{video.flv}" ' \
                           f'-c:v {get_cv()} ' \
                           f'-profile:v main ' \
                           f'-c:a copy ' \
                           f'-b:v {config.bps} ' \
                           f'-vf scale={columns}:{rows} ' \
                           f'-max_muxing_queue_size 1024 ' \
                           f'-r 60 ' \
                           f'input{index}.mp4\n\r'
            else:
                # 分辨率比例不一致，矫正视频比例(加黑边)
                if video.columns / video.rows > crr:
                    # 宽过长，上下加黑边
                    # 先计算出缩放后的分辨率，由于是上下加黑边，左右即视频宽要缩放至与目标一致
                    scale_ratio = columns / video.columns
                    scale_columns = columns
                    scale_rows = int(video.rows * scale_ratio)
                    # 在黑色底，将视频居中放置，则视频左上角的位置应该在(0, y)
                    # y是黑边总高度的一半
                    x = 0
                    y = (rows - scale_rows) // 2
                else:
                    # 高过长，左右加黑边
                    # 先计算出缩放后的分辨率，由于是左右加黑边，上下即视频高要缩放至与目标一致
                    scale_ratio = rows / video.rows
                    scale_columns = int(video.columns * scale_ratio)
                    scale_rows = rows
                    # 在黑色底，将视频居中放置，则视频左上角的位置应该在(x, 0)
                    # x是黑边总长度的一半
                    x = (columns - scale_columns) // 2
                    y = 0
                command += f'ffmpeg -y -i "{video.flv}" ' \
                           f'-c:v {get_cv()} ' \
                           f'-profile:v main ' \
                           f'-c:a copy ' \
                           f'-b:v {config.bps} ' \
                           f'-vf scale={scale_columns}:{scale_rows},pad={columns}:{rows}:{x}:{y}:black ' \
                           f'-max_muxing_queue_size 1024 ' \
                           f'-r 60 ' \
                           f'"input{index}.mp4"\n\r'
            clear += f"del input{index}.mp4\n\r"

        if not app.fast_no_danmu:
            filelist_no_danmu += f"file 'input{index}.mp4'\n"

        # 弹幕
        if options['danmu']:
            generate_ass(path, video, columns, rows, index, get_danmu_font_size(columns, rows), 1)  # 生成弹幕文件
            # 生成有弹幕的视频
            command += f'ffmpeg -y -i input{index}.mp4 ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows},ass=input{index}.ass ' \
                       f'-r 60 ' \
                       f'"output{index}.mp4"\n\r'
            clear += f'del "input{index}.ass"\n\r'
            clear += f'del "output{index}.mp4"\n\r'
            filelist_danmu += f"file 'output{index}.mp4'\n"
        if output_method == 1 and options['small_danmu']:
            generate_ass(path, video, columns, rows, index, get_danmu_font_size(columns, rows, True), 4, 'sync', True)  # 生成弹幕文件
            # 生成有弹幕的视频
            command += f'ffmpeg -y -i input{index}.mp4 ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows},ass=input{index}_small.ass ' \
                       f'-r 60 ' \
                       f'"output{index}_small.mp4"\n\r'
            clear += f'del "input{index}_small.ass"\n\r'
            clear += f'del "output{index}_small.mp4"\n\r'
            filelist_danmu_small += f"file 'output{index}_small.mp4'\n"

    app.set_log('')
    output_tips(app)
    # 合并无弹幕版
    if options['no_danmu']:
        clear += 'del filelist0.txt\n\r'
        if app.fast_no_danmu:
            app.insert_log('无弹幕版可以在短时间内合并完成，您可以在渲染其他视频过程中先上传它。\n\n')
        else:
            generate_file(path, 'filelist0.txt', filelist_no_danmu)
            command += 'ffmpeg -y -f concat -i filelist0.txt -c copy "!!!无弹幕.mp4"\n\r'
    # 合并有弹幕版
    if options['danmu']:
        generate_file(path, 'filelist1.txt', filelist_danmu)
        if output_method == 1 and options['small_danmu']:
            command += 'ffmpeg -y -f concat -i filelist1.txt -c copy "!!!大弹幕(适合手机).mp4"\n\r'
        else:
            command += 'ffmpeg -y -f concat -i filelist1.txt -c copy "!!!有弹幕.mp4"\n\r'
        clear += 'del filelist1.txt\n\r'
    if output_method == 1 and options['small_danmu']:
        generate_file(path, 'filelist2.txt', filelist_danmu_small)
        command += 'ffmpeg -y -f concat -i filelist2.txt -c copy "!!!小弹幕(适合电脑).mp4"\n\r'
        clear += 'del filelist2.txt\n\r'

    if options['bell']:
        command += 'echo '+chr(7)+'\n\r'
        command += 'timeout /t 5'
    clear += 'del ffmpeg.exe\n\r'
    clear += 'del "!!!开始渲染.bat"\n\r'
    clear += 'del %0'
    shutil.copy('bin/ffmpeg.exe', path)
    generate_file(path, '!!!开始渲染.bat', command)
    generate_file(path, '!!!清理所有中间文件.bat', clear)


def generate_single(app, videos, columns, rows, output_method):
    options = app.get_options()
    video = videos[0]
    if not options['danmu'] and not options['small_danmu']:
        app.set_log(f'不生成弹幕的话，直接上传无弹幕版的【{video.flv}】就行了。')
        return
    app.set_log(f'【{video.flv}】就是无弹幕版，你可以在渲染的过程中先上传它。\n\n')
    if not options['no_danmu']:
        app.insert_log('虽然您没有勾选输出无弹幕版，但不能删除原始文件，您如果真的不需要无弹幕版，不上传它就行了。\n\n')
    output_tips(app)

    path = app.analysed_path
    command = "chcp 65001\n\r"  # 调整命令行编码为UTF-8
    clear = "chcp 65001\n\r"  # 清理用命令
    # 生成横屏视频
    if output_method == 1:
        if options['danmu'] or options['small_danmu']:
            # 生成一个高帧率中间文件
            command += f'ffmpeg -y -i "{video.flv}" ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows} ' \
                       f'-max_muxing_queue_size 1024 ' \
                       f'-r 60 ' \
                       f'input.mp4\n\r'
            clear += "del input.mp4\n\r"
        if options['danmu']:
            generate_ass(path, video, columns, rows, 0, get_danmu_font_size(columns, rows))  # 生成弹幕文件
            # 生成有弹幕的视频
            command += f'ffmpeg -y -i input.mp4 ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows},ass=input.ass ' \
                       f'-r 60 ' \
                       f'"!!!大弹幕(适合手机).mp4"\n\r'
            clear += 'del "input.ass"\n\r'
        if options['small_danmu']:
            generate_ass(path, video, columns, rows, 0, get_danmu_font_size(columns, rows, True), 4, 'sync', True)
            # 生成有弹幕的视频
            command += f'ffmpeg -y -i input.mp4 ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows},ass=input_small.ass ' \
                       f'-r 60 ' \
                       f'"!!!小弹幕(适合电脑).mp4"\n\r'
            clear += f'del "input_small.ass"\n\r'
    else:  # 生成竖屏视频
        # 弹幕
        if options['danmu']:
            generate_ass(path, video, columns, rows)
            # 生成高质量中间文件
            command += f'ffmpeg -y -i "{video.flv}" ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows} ' \
                       f'-max_muxing_queue_size 1024 ' \
                       f'-r 60 ' \
                       f'input.mp4\n\r'
            # 生成有弹幕的视频
            command += f'ffmpeg -y -i input.mp4 ' \
                       f'-c:v {get_cv()} ' \
                       f'-profile:v main ' \
                       f'-c:a copy ' \
                       f'-b:v {config.bps} ' \
                       f'-vf scale={columns}:{rows},ass=input.ass ' \
                       f'"!!!有弹幕.mp4"\n\r'
            clear += "del input.mp4\n\r"
            clear += f'del "input.ass"\n\r'

    if options['bell']:
        command += 'echo '+chr(7)+'\n\r'
        command += 'timeout /t 5'
    clear += 'del ffmpeg.exe\n\r'
    clear += 'del "!!!开始渲染.bat"\n\r'
    clear += 'del %0'
    shutil.copy('bin/ffmpeg.exe', path)
    generate_file(path, '!!!开始渲染.bat', command)
    generate_file(path, '!!!清理所有中间文件.bat', clear)


def generate_file(path, file, info):
    with open(path+"/"+file, "w", encoding='UTF-8') as file_obj:
        file_obj.write(info)


def generate_ass(path, video, columns, rows, index=0, font_size=80, tune_duration=0, algorithm='async', is_small=False):
    io_args = {
        'input_filename': path + '/' + video.xml,
        'output_filename': path + '/input' + (str(index) if index != 0 else '')+('_small' if is_small else '') + '.ass'
    }
    danmuku_args = {
        'custom_filter': None,
        'bottom_filter': False,
        'guest_filter': False,
        'top_filter': False,
    }
    subtitle_args = {
        'play_resolution': str(columns)+'x'+str(rows),
        'line_count': config.max_danmu_line,
        'font_name': config.font_name,
        'font_size': font_size,
        'layout_algorithm': algorithm,
        'tune_duration': tune_duration,
        'drop_offset': 2,
        'bottom_margin': 0,
        'custom_offset': '00:00',
        'header_file': None,
    }
    niconvert.convert(io_args, danmuku_args, subtitle_args)


def get_cv():
    if config.n_cuda:
        return 'h264_nvenc'
    else:
        return 'h264'


def output_tips(app):
    app.insert_log(f'在工作目录下运行【!!!开始渲染.bat】即可开始渲染。\n\n')
    app.insert_log(f'当渲染完成时，运行【!!!清理所有中间文件.bat】即可清理垃圾。请勿在渲染过程中运行它。\n\n')
    app.insert_log(f'如果您需要备份的话，建议只备份原始文件，因为输出的文件不能逆向回到原始文件，原始文件不仅比输出文件小，还能随时转为输出文件。'
                   f'而且输出的文件可能会有音画不同步等问题，日后发现问题时可以靠原始文件来修复它。')


def get_danmu_font_size(columns, rows, is_small=False):
    if columns >= rows:
        if is_small:
            return rows / 1080 * config.small_danmu_size_default
        else:
            return rows / 1080 * config.danmu_size_default
    else:
        if is_small:
            return columns / 1080 * config.small_danmu_size_default
        else:
            return columns / 1080 * config.danmu_size_default

