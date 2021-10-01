import base64
import re
import sys

try:
    import qrcode
    import requests
except ImportError:
    sys.exit("请安装依赖: pip install qrcode requests")

port = None

try:
    with open("CoreConf.conf") as f:
        for i in f.readlines():
            if re.findall(r":(\d+)", i):
                port = re.findall(r":(\d+)", i)[0]
                port = int(port)
                break
except Exception:
    pass

port = port or int(input("读取配置错误, 请手动输入端口号："))

login_url = f"http://127.0.0.1:{port}/v1/Login/GetQRcode"


def main():
    print(f"获取二维码 {login_url}")
    try:
        resp = requests.get(login_url, timeout=10)
        b64 = re.findall(r'base64,(.*?)"', resp.text)[0]
    except Exception:
        sys.exit("获取二维码失败")

    content = base64.b64decode(b64)

    print("解码二维码")
    files = {"file": ("qrcode.png", content, "image/png")}
    try:
        resp = requests.post("https://zxing.org/w/decode", files=files, timeout=10)
        qrcode_data = re.findall(
            r"<td>Raw text</td><td><pre>(.*?)</pre></td>", resp.text
        )[0]
    except Exception:
        sys.exit("二维码解码失败")

    # link
    print("请使用手机QQ访问该地址：")
    print(qrcode_data)
    print()

    # scan
    print("请使用手机QQ扫描该二维码")
    qr = qrcode.QRCode()
    qr.add_data(qrcode_data)
    qr.make()
    qr.print_ascii()


if __name__ == "__main__":
    main()
