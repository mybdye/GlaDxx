# GlaDxx 自动签到脚本 🤖

[![GlaDxx Checkin](https://github.com/mybdye/GlaDxx/actions/workflows/main.yml/badge.svg)](https://github.com/mybdye/GlaDxx/actions/workflows/main.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/mybdye/GlaDxx)](LICENSE)

一个基于GitHub Actions的GlaDxx自动签到脚本，支持多账户管理和多种推送通知方式。

## 🚀 功能特性

- ✅ **多账户支持** - 同时管理多个GlaDxx账户
- 📱 **多种推送方式** - 支持Bark、PushDeer、Telegram通知
- ⚡ **自动化执行** - 基于GitHub Actions定时执行
- 🔒 **安全可靠** - 环境变量配置，保护敏感信息
- 📊 **详细信息** - 显示流量使用情况和剩余天数
- 🛠️ **易于部署** - 一键配置，无需服务器

## 📋 更新日志

### 最新更新 (2026.02.24)
- 🔧 重构代码结构，提升可维护性
- 🛡️ 增强安全性和错误处理
- ⚡ 优化性能和网络请求
- 📦 完善依赖管理和版本控制
- 📝 改进文档和配置说明

### 历史更新
- 2026.02.23-24 - 更新API地址，添加Bark群组功能
- 2023.10.30 - 添加PushDeer推送支持
- 2023.07.23 - 切换到API方法 🚀
- 2023.04.01 - 添加用户流量信息显示
- 2023.01.19 - 修复Cookie错误通知
- 2022.12.22 - 添加账户过期判断
- 2022.12.05 - 免费用户无法签到，请升级到Basic/Pro套餐
- 2022.11.19 - 多项改进优化
- 2022.11.08 - 使用JSON替代替换方法，移除save_cookies文件
- 2022.11.06 - 项目初始构建

## 🛠️ 部署指南

### 1. Fork 本仓库
点击右上角的 Fork 按钮，将本仓库复制到你的 GitHub 账户下。

### 2. 配置 Secrets
在你 fork 的仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下环境变量：

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `COOKIES` | GlaDxx账户Cookies，多账户请换行分隔 | ✅ Yes |
| `BARK_TOKEN` | Bark推送Token (可选) | ❌ No |
| `PUSHDEER_KEY` | PushDeer推送Key (可选) | ❌ No |
| `TG_BOT_TOKEN` | Telegram Bot Token (可选) | ❌ No |
| `TG_USER_ID` | Telegram用户ID (可选) | ❌ No |

### 3. 获取 Cookies
1. 在浏览器中登录你的GlaDxx账户
2. 按 F12 打开开发者工具
3. 刷新页面，在 Network → Doc 中找到请求
4. 查看 Request Headers 中的 cookie 字段
5. 右键复制 cookie 值

### 4. 自定义执行时间
编辑 `.github/workflows/main.yml` 文件中的 schedule 部分：

```yaml
schedule:
  - cron: '02 3 * * *'  # UTC时间，对应北京时间上午11:02
```

**Cron表达式说明：**
```
* * * * *
│ │ │ │ │
│ │ │ │ └── 星期几 (0-7, 0和7都表示周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

## 📱 推送通知配置

### Bark 推送
- 访问 https://github.com/Finb/Bark 获取配置说明
- 在iOS设备上安装Bark应用

### PushDeer 推送
- 访问 https://www.pushdeer.com 获取配置说明
- 支持多平台推送

### Telegram 推送
1. 创建Bot：与 [@BotFather](https://t.me/BotFather) 对话创建Bot
2. 获取用户ID：给 [@userinfobot](https://t.me/userinfobot) 发送 `/start`
3. 将Bot添加为联系人并开始对话

## 🎯 使用说明

配置完成后，脚本会按照设定的时间自动执行签到。你可以通过以下方式查看执行结果：

- GitHub Actions 运行历史
- 配置的推送通知
- GitHub仓库的Actions标签页

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目！

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Python](https://www.python.org/) - 编程语言
- [Requests](https://docs.python-requests.org/) - HTTP库
- [GitHub Actions](https://github.com/features/actions) - CI/CD平台
- [Bark](https://github.com/Finb/Bark) - iOS推送工具
- [PushDeer](https://www.pushdeer.com) - 多平台推送服务

---

<p align="center">Made with ❤️ by <a href="https://github.com/mybdye">DanielWu</a></p>
