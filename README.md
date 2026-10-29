# 知伴 · AI 期末伴学

面向有编程基础的大三学生的 Python + DeepSeek 学习助手原型。

## 已实现

- 粘贴课程资料（最多 20000 字）及查看资料行号。
- 按剩余天数、每日时间和目标生成复习计划。
- 多轮答疑、代码讲解，以及先答题再反馈的自测模式。
- 下载当前复习记录。切换课程、资料或模式会清空当前对话。
- API 密钥通过环境变量读取；超时、密钥错误、余额不足和限流提示。

这些学习行为由提示词引导，不是确定性评分系统。资料引用由模型生成，未做自动校验。

## 本地运行（Python 3.10+，PowerShell）

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DEEPSEEK_API_KEY = '替换为你自己的密钥'
$env:DEEPSEEK_MODEL = 'deepseek-flash'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

在本机浏览器打开终端显示的地址。不要将真实密钥写入源码或提交到 GitHub。
本项目不自动读取 `.env` 文件。密钥只需在运行应用的终端配置，无需发送到聊天中。

## 接入说明

使用标准库调用 `https://api.deepseek.com/chat/completions`，默认模型 `deepseek-flash`，可通过环境变量覆盖。
官方接入文档：https://api-docs.deepseek.com/
问题、当前资料和部分近期对话会发送到 DeepSeek；最多保留 16000 字的近期完整对话作为历史上下文。
代码仅作讲解文本，不执行用户提交的程序。

## 验证

```powershell
python -m unittest discover -s tests -v
```

自动测试使用模拟响应，不消耗 API 额度。真实模型调用需要配置有效密钥后验证。

## 后续开发

PDF/PPT 解析、带检索与引用校验的课程知识库、SQLite 学习记录、错题复习与掌握度统计。
当前没有账号体系、持久化存储、自动代码判题或生产部署配置。
