import time
import datetime
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class Mail_Sender:
    def __init__(self, params):
        self.mail_host = params.mail_host  # 服务器地址 'smtp.163.com'
        self.email_sender = params.email_sender  # 发送人邮箱 'xxx@163.com'
        self.mail_license = params.mail_license  # 邮箱授权码, 不是密码!
        self.msg = None

    # 编辑邮件内容: 主题, 正文, 图片路径
    def edit_text(self, subject_content, body_content, img_dir=None):
        self.msg = MIMEMultipart('related')
        # self.msg["From"] = ''
        # self.msg["To"] = ''
        self.msg["Subject"] = Header(subject_content, 'utf-8')  # 主题
        self.msg.attach(MIMEText(body_content, 'plain', 'utf-8'))  # 正文
        # 图片
        if img_dir is not None:
            with open(img_dir, 'rb') as img:
                msg_img = MIMEImage(img.read(), img_dir.split('.')[-1])
            self.msg.attach(msg_img)

    # 发送邮件: 收件人邮箱, 发送次数, 间隔时间
    def send_email(self, email_receiver, send_times=1, interval_time=0):
        stp = smtplib.SMTP()  # 创建SMTP对象
        stp.connect(self.mail_host, 25)  # 设置发件人邮箱的域名和端口, 端口地址为25
        stp.login(self.email_sender, self.mail_license)  # 登录邮箱: 邮箱地址, 邮箱授权码
        print(f'{datetime.datetime.now()} <-* info: Login successfully *->')
        # 一次/多次发送
        for i in range(send_times):
            stp.sendmail(self.email_sender, email_receiver, self.msg.as_string())
            print(f'{datetime.datetime.now()} <-* info: Send successfully *->')
            time.sleep(interval_time)
        stp.quit()  # 退出登录
