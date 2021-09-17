# coding: utf-8
import base64
import logging
import os
import re
import subprocess
import sys
import urllib.parse

import qrcode
import requests
import zxing


class OPQLogin(object):

    def __init__(self):
        self.DEBUG = False
        self.port = 8888

    def loadConfig(self):
        try:
            conf = {}
            path_conf = os.path.join(sys.path[0], 'CoreConf.conf')
            with open(path_conf, encoding='utf-8') as fp:
                for line in fp:
                    key, val = line.strip().split('=')
                    conf[key.strip()] = val.strip().replace('"', '')
            if 'Port' in conf:
                if 'http' in conf['Port']:
                    url = conf['Port']
                else:
                    url = 'http://' + conf['Port']
                self.port = int(urllib.parse.urlparse(url).port)
                print('[*] Port: {}'.format(self.port))
                return True
            else:
                print('CoreConf.conf 文件中未找到 Port 配置项')
        except FileNotFoundError:
            print('CoreConf.conf 文件未找到，请将本程序放在 OPQBot 目录下运行')
        except Exception as e:
            print('未知错误({})'.format(e))
        return False

    def _saveFile(self, filename, data):
        dirName = os.path.join(sys.path[0], 'LoginQRcodes')
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        fn = os.path.join(dirName, filename)
        logging.debug('Saved file: %s' % fn)
        with open(fn, 'wb') as f:
            f.write(data)
            f.close()
        return fn

    def genQRCode(self):
        if sys.platform.startswith('win'):
            self._showQRCodeImg('win')
        elif sys.platform.find('darwin') >= 0:
            self._showQRCodeImg('macos')
        else:
            self._showQRCodeImg('cmd')

    def _showQRCodeImg(self, str):
        url = 'http://127.0.0.1:{}/v1/Login/GetQRcode'.format(self.port)
        try:
            resp = requests.get(url)
        except:
            print('[*] 获取失败，请检查 OPQBot 是否运行. ')
            return
        data = resp.text
        info_ret = re.findall(r'data:image/png;base64,(.*?)"', data)
        if info_ret and len(info_ret) > 0:
            image_data = base64.b64decode(info_ret[0])
            QRCODE_PATH = self._saveFile('qrcode.jpg', image_data)
            if str == 'win':
                os.startfile(QRCODE_PATH)
                print('[*] 二维码图片已打开，请使用手机QQ扫描该二维码')
            elif str == 'macos':
                subprocess.call(["open", QRCODE_PATH])
                print('[*] 二维码图片已打开，请使用手机QQ扫描该二维码')
            else:
                barcode = zxing.BarCodeReader().decode(QRCODE_PATH)
                self._str2qr(barcode.parsed)

    def start(self):
        print('[*] OPQBot Get Login QRcode')
        print('[*] 正在获取 OPQBot 端口 ... ')
        if self.loadConfig():
            print('[*] 正在获取登录二维码 ... ')
            self.genQRCode()
        print('[*] 程序退出.')

    def _str2qr(self, url):
        print("===============================")
        print("请使用手机QQ访问该地址：\n{}".format(url))
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make()
        print("===============================")
        print("请使用手机QQ扫描该二维码：")
        try:
            qr.print_ascii(tty=True, invert=True)
        except:
            qr.print_ascii(invert=True)


if __name__ == '__main__':
    opqlogin = OPQLogin()
    opqlogin.start()
