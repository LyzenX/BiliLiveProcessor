import os

from niconvert.libass.studio import Studio
from niconvert.libsite.producer import Producer


def convert(io_args, danmaku_args, subtitle_args):
    input_filename = io_args['input_filename']
    output_filename = io_args['output_filename']

    # 弹幕预处理
    producer = Producer(danmaku_args, input_filename)
    producer.start_handle()
    # print('屏蔽条数：游客(%(guest)d) + 顶部(%(top)d) + '
    #       '底部(%(bottom)d) + 自定义(%(custom)d) = %(blocked)d\n'
    #       '通过条数：总共(%(total)d) - 屏蔽(%(blocked)d) = %(passed)d'
    #       % producer.report())

    # 字幕生成
    danmakus = producer.keeped_danmakus
    studio = Studio(subtitle_args, danmakus)
    studio.start_handle()
    studio.create_ass_file(output_filename)
    # print(f'字幕大小:{subtitle_args["font_size"]}')
    # print('字幕条数：总共(%(total)d) - 丢弃(%(droped)d) = %(keeped)d' %
    #       studio.report())
    # print('字幕文件：%s' % os.path.basename(output_filename))
