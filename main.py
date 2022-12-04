import time

from utils.financial_watchdog import Financial_Watchdog
from utils.sl_plot import sl_plot
from utils.mail_send import Mail_Sender


class Test_Options:
    def __init__(self):
        # mail
        self.mail_host = 'smtp.163.com'  # 服务器地址
        self.email_sender = 'xxx@163.com'  # 发送人邮箱
        self.mail_license = 'XXXX'  # 邮箱授权码
        self.email_receivers = ['xxx@126.com', 'xxx@qq.com']  # 收件人邮箱, 可以为多个收件人
        # creeper
        self.target_name = '中银理财-悦享天添卓越版-YXTTZY01F'
        self.screen_roi = (0, 0, 2560, 1600)  # 屏幕分辨率 (0, 0, 2560, 1600); (0, 0, 1920, 1080)
        self.aim_url = 'https://www.bankofchina.com/sdbapp/wmpnetworth/7784/7788/8975/index_1719.html'  # 目标网站地址
        self.default_browser = 'msedge.exe'  # 默认浏览器
        # detect
        self.use_ocr_position = True  # True: 使用ocr定位; False: 使用模板匹配定位
        self.template_name = ['./anchor/anchor_1.png', './anchor/anchor_2.png']  # 模板图片地址
        # common
        self.check_time = ('07:30', '15:00')  # 定期发送时间


def main(opt):
    # 初始化
    auto_sender = Mail_Sender(opt)
    financial_watchdog = Financial_Watchdog(opt)
    with open('library.txt', encoding='utf-8') as str_book:
        words_list = str_book.read().split('\n\n')  # 随附的每日一句
    first_start = True  # 第一次运行就发送, 不需要等到特定时间段
    day_count = 0  # 记录运行天数
    # 开始工作
    while True:
        # 获取时间
        time_now = time.strftime("%H:%M", time.localtime())
        if time_now in opt.check_time or first_start:
            # 获取图像
            web_img = financial_watchdog.grab_img()
            # 获取识别结果
            res_det = financial_watchdog.detect_data(web_img, ocr_position=opt.use_ocr_position)
            if res_det is not None:
                # 绘图并保存
                sl_plot(res_det, x=None, save_switch=True)
                send_str = f'Your latest financial has arrived!\n\nTarget name: {opt.target_name}\n'
                value_growth = round(res_det[-1] - res_det[-2], 6)  # 相比昨天增长量 (一阶)
                earn_1w_per = round(1e4 / res_det[-2] * value_growth, 2)  # 直观化
                d_growth = round(res_det[-1] + res_det[-3] - 2 * res_det[-2], 6)  # 相比昨天增长量的增长量 (二阶)
                earn_1w_per_d = round(1e4 / res_det[-2] * d_growth, 2)  # 直观化
                send_str += f'The latest value growth is: {value_growth} (except to earn ￥{earn_1w_per} per 1w)\n'
                if d_growth >= 0:
                    send_str += f'Compared to yesterday, value growth: +{d_growth} (more ￥{earn_1w_per_d} per 1w)\n'
                else:
                    send_str += f'Compared to yesterday, value growth: {d_growth} (more ￥{earn_1w_per_d} per 1w)\n'
                send_str += f'Detail:\n{res_det}\n\nDaily tip: {words_list[day_count]}\n\nHave a nice day!'
                auto_sender.edit_text(subject_content='Hi! Boss', body_content=send_str, img_dir='statistic.png')
            else:
                auto_sender.edit_text(subject_content='Hi! Boss', body_content='Error!', img_dir=None)
            # 发送邮件
            auto_sender.send_email(opt.email_receivers, send_times=1, interval_time=1)
            day_count += 1
            if not first_start:
                time.sleep(25200)  # 睡眠7小时
            first_start = False
        else:
            time.sleep(55)  # 必须小于一分钟这个采样周期


if __name__ == '__main__':
    test_options = Test_Options()
    main(test_options)
