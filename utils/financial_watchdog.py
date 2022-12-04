import os
import time
import webbrowser

from PIL import ImageGrab
import numpy as np
import cv2
import easyocr


#  模板匹配
def template_match(img, template, mask=None):
    # 都转成灰度图
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(template.shape) > 2:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # 模板匹配
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED, mask)
    # 返回最大最小值及索引
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
    x_1, y_1 = maxLoc
    x_2 = x_1 + template.shape[1]
    y_2 = y_1 + template.shape[0]
    return x_1, y_1, x_2, y_2  # [左上x, 左上y, 右下x, 右下y]


class Financial_Watchdog:
    def __init__(self, params):
        self.screen_roi = params.screen_roi  # 屏幕截图分辨率, 如 (0, 0, 2560, 1600)
        self.aim_url = params.aim_url  # 目标网站地址
        self.default_browser = params.default_browser  # 默认浏览器, 如 'msedge.exe'
        self.text_recognizer = easyocr.Reader(['ch_sim'])  # ocr 语言选择, 并生成识别器
        # 将匹配模板图片加载至列表, 如用 ocr 定位可忽略
        self.template_img = []
        for file_name in params.template_name:
            self.template_img.append(cv2.imread(file_name, 0))

    def grab_img(self):
        # 打开网站
        webbrowser.open(self.aim_url)
        time.sleep(10)  # 等待打开
        # 截图
        img = ImageGrab.grab(bbox=self.screen_roi)
        # 关闭浏览器进程
        os.system('taskkill /F /IM ' + self.default_browser)
        # 转为 cv2 格式
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img

    def detect_data(self, img, ocr_position=True):
        # 二值化
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # cv2.imwrite('test.png', img)  # 可选择记录捕获的二值化图片
        # 定位 (以下代码需根据需求自定义)
        left_x = None
        right_x = None
        top_y = None
        # 用 ocr 方式定位
        if ocr_position:
            img_det = self.text_recognizer.readtext(img)
            for element in img_det:
                if element[1] == '份额净值':
                    left_x = np.min(element[0], axis=0)[0] - 10
                    top_y = np.max(element[0], axis=0)[1]
                elif element[1] == '认购价格':
                    right_x = np.min(element[0], axis=0)[0] - 10
        # 用模板匹配方式定位
        else:
            match_res = template_match(img, self.template_img[0], mask=None)
            left_x = match_res[0] - 10
            top_y = match_res[3]
            match_res = template_match(img, self.template_img[1], mask=None)
            right_x = match_res[0] - 10
        # 切分感兴趣区域
        if None not in (left_x, right_x, top_y):
            roi_interest = img[top_y:, left_x:right_x]
            # OCR 提取数据
            img_det = self.text_recognizer.readtext(roi_interest)
            price_list = []
            for element in img_det:
                price_list.append(float(element[1]))
            price_list = np.array(price_list[::-1])
            print(f'solve result: {price_list}')
            return price_list
        else:
            return None
