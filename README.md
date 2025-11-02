# 抢票脚本

这是一个支持大麦网和B站展会的抢票脚本，可以帮助您自动化抢票流程。

## 功能特点

- 支持大麦网演唱会、话剧等票务抢票
- 支持B站展会门票抢票
- 支持自动等待开售时间
- 支持自动选择票档和数量
- 支持自动提交订单
- 详细的日志记录

## 安装依赖

在使用前，请确保安装了以下依赖：

```bash
pip install selenium requests
```

此外，您还需要安装Chrome浏览器和对应版本的ChromeDriver。

## 配置说明

在使用前，请先修改`config.json`文件，填写相关配置：

```json
{
    "damai": {
        "username": "",          // 大麦网账号（可选，推荐手动登录）
        "password": "",          // 大麦网密码（可选，推荐手动登录）
        "manual_login": true,    // 是否手动登录，建议设为true
        "show_browser": true,    // 是否显示浏览器界面
        "keep_browser": true,    // 抢票成功后是否保持浏览器打开
        "save_cookies": true,    // 是否保存cookies
        "cookie_path": "",       // cookies保存路径（可选）
        "target_url": "",        // 目标演出页面URL（必填）
        "ticket_type": "",       // 期望的票档名称（可选，如"VIP"）
        "allow_other_ticket": true, // 如果指定票档不可用，是否选择其他票档
        "ticket_count": 1,       // 购票数量
        "retry_times": 10,       // 重试次数
        "sale_time": ""          // 开售时间，格式："2023-12-31 12:00:00"（可选）
    },
    "bilibili": {
        // B站配置，字段含义同上
        "manual_login": true,
        "show_browser": true,
        "keep_browser": true,
        "save_cookies": true,
        "cookie_path": "",
        "target_url": "",        // 目标展会页面URL（必填）
        "ticket_type": "",
        "allow_other_ticket": true,
        "ticket_count": 1,
        "retry_times": 10,
        "sale_time": ""
    }
}
```

## 使用方法

1. 修改`config.json`配置文件，填写目标演出/展会的URL和其他配置
2. 运行脚本：

```bash
# 同时运行大麦网和B站抢票
python ticket_sniper.py

# 只运行大麦网抢票
python ticket_sniper.py --platform damai

# 只运行B站展会抢票
python ticket_sniper.py --platform bilibili

# 使用自定义配置文件
python ticket_sniper.py --config my_config.json
```

## 注意事项

1. 本脚本仅供学习交流使用，请勿用于商业用途
2. 频繁抢票可能导致账号被限制，请谨慎使用
3. 建议使用手动登录模式，避免账号安全问题
4. 抢票成功后，请在规定时间内完成支付，否则订单会自动取消
5. 不同平台的页面结构可能会变化，如遇问题请及时更新脚本

## 常见问题

1. **无法启动浏览器**：请确保已安装Chrome浏览器和对应版本的ChromeDriver
2. **登录失败**：建议使用手动登录模式，或检查账号密码是否正确
3. **无法选择票档**：可能是页面结构变化，请检查日志并更新脚本
4. **抢票失败**：热门演出/展会抢票难度较大，可以增加重试次数或使用多个账号同时抢票

## 免责声明

本脚本仅供学习交流使用，使用本脚本造成的任何问题与作者无关。请遵守相关平台的用户协议和规定。