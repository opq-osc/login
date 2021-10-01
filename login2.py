# coding: utf-8
# author: https://github.com/BrandTime
import base64
import logging
import os
import re
import subprocess
import sys
import urllib.parse

try:
    import requests
    from numpy import array
    from PIL import Image
except ImportError:
    sys.exit("请安装依赖：pip install numpy, requests, pillow")


class OPQLogin(object):
    def __init__(self):
        self.DEBUG = False
        self.port = 8888

    def loadConfig(self):
        try:
            conf = {}
            path_conf = os.path.join(sys.path[0], "CoreConf.conf")
            with open(path_conf, encoding="utf-8") as fp:
                for line in fp:
                    key, val = line.strip().split("=")
                    conf[key.strip()] = val.strip().replace('"', "")
            if "Port" in conf:
                if "http" in conf["Port"]:
                    url = conf["Port"]
                else:
                    url = "http://" + conf["Port"]
                self.port = int(urllib.parse.urlparse(url).port)
                print("[*] Port: {}".format(self.port))
                return True
            else:
                print("CoreConf.conf 文件中未找到 Port 配置项")
        except FileNotFoundError:
            print("CoreConf.conf 文件未找到，请将本程序放在 OPQBot 目录下运行")
        except Exception as e:
            print("未知错误({})".format(e))
        return False

    def _saveFile(self, filename, data):
        dirName = os.path.join(sys.path[0], "LoginQRcodes")
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        fn = os.path.join(dirName, filename)
        logging.debug("Saved file: %s" % fn)
        with open(fn, "wb") as f:
            f.write(data)
            f.close()
        return fn

    def genQRCode(self):
        if sys.platform.startswith("win"):
            self._showQRCodeImg("win")
        elif sys.platform.find("darwin") >= 0:
            self._showQRCodeImg("macos")
        else:
            self._showQRCodeImg("cmd")

    def matrix_to_ascii(self, modules, out=None, tty=False, invert=False):
        """
        Output the QR Code using ASCII characters.
        :param tty: use fixed TTY color codes (forces invert=True)
        :param invert: invert the ASCII characters (solid <-> transparent)
        """
        if out is None:
            out = sys.stdout

        if tty and not out.isatty():
            raise OSError("Not a tty")

        modcount = len(modules[0])
        codes = [bytes((code,)).decode("cp437") for code in (255, 223, 220, 219)]
        if tty:
            invert = True
        if invert:
            codes.reverse()

        def get_module(x, y):
            if invert and max(x, y) >= modcount:
                return 1
            if min(x, y) < 0 or max(x, y) >= modcount:
                return 0
            return not modules[x][y]

        for r in range(0, modcount, 2):
            if tty:
                if not invert or r < modcount + -1:
                    out.write("\x1b[48;5;232m")  # Background black
                out.write("\x1b[38;5;255m")  # Foreground white
            for c in range(0, modcount):
                pos = get_module(r, c) + (get_module(r + 1, c) << 1)
                out.write(codes[pos])
            if tty:
                out.write("\x1b[0m")
            out.write("\n")
        out.flush()

    def _showQRCodeImg(self, str):
        url = "http://127.0.0.1:{}/v1/Login/GetQRcode".format(self.port)
        try:
            resp = requests.get(url)
        except:
            print("[*] 获取失败，请检查 OPQBot 是否运行. ")
            return
        data = resp.text
        info_ret = re.findall(r'data:image/png;base64,(.*?)"', data)
        if info_ret and len(info_ret) > 0:
            image_data = base64.b64decode(info_ret[0])
            QRCODE_PATH = self._saveFile("qrcode.jpg", image_data)
            if str == "win":
                os.startfile(QRCODE_PATH)
                print("[*] 二维码图片已打开，请使用手机QQ扫描该二维码")
            elif str == "macos":
                subprocess.call(["open", QRCODE_PATH])
                print("[*] 二维码图片已打开，请使用手机QQ扫描该二维码")
            else:
                pic_qrcode = (
                    Image.open(QRCODE_PATH).crop((9, 9, 126, 126)).resize((39, 39))
                )
                print("[*] 请使用手机QQ扫描该二维码：")
                try:
                    self.matrix_to_ascii(array(pic_qrcode), tty=True, invert=True)
                except:
                    self.matrix_to_ascii(array(pic_qrcode), invert=True)

    def start(self):
        print("[*] OPQBot Get Login QRcode")
        print("[*] 正在获取 OPQBot 端口 ... ")
        if self.loadConfig():
            print("[*] 正在获取登录二维码 ... ")
            self.genQRCode()
        print("[*] 程序退出.")


if __name__ == "__main__":
    opqlogin = OPQLogin()
    opqlogin.start()
