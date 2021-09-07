use qrcode::render::unicode;
use qrcode::QrCode;
use regex::Regex;
use rqrr::PreparedImage;
use std::io::{self, Write};

fn main() {
    print!("请输入机器人运行端口号：");
    let mut port = String::new();
    io::stdout().flush().unwrap();
    io::stdin().read_line(&mut port).unwrap();
    let url = format!("http://127.0.0.1:{}/v1/Login/GetQRcode", port);

    let resp =
        reqwest::blocking::get(url.clone()).expect(format!("请检查地址是否正确：{}", url).as_str());
    let text = resp.text().unwrap();

    let re = Regex::new(r#"data:image/png;base64,(.*?)""#).unwrap();
    let matches = re.captures(text.as_str()).unwrap();
    let base64 = &matches[1];

    let buffer = base64::decode(base64).unwrap();
    let img = image::load_from_memory(&buffer).unwrap().to_luma8();

    let mut img = PreparedImage::prepare(img);
    let grids = img.detect_grids();
    let (_, content) = grids[0].decode().unwrap();
    println!("===============================");
    println!("使用手机QQ访问该地址：");
    println!("{}", content);

    let code = QrCode::new(content).unwrap();
    let image = code
        .render::<unicode::Dense1x2>()
        .dark_color(unicode::Dense1x2::Light)
        .light_color(unicode::Dense1x2::Dark)
        .build();
    println!("===============================");
    println!("使用手机QQ扫描该二维码：");
    println!("{}", image);
}
