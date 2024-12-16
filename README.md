# GitLab MR 通知机器人

一个基于 Python 的 GitLab Merge Request 通知机器人，可以将 MR 相关事件推送到企业微信群。本项目使用poetry管理依赖，使用uvicorn作为web启动器，使用fastapi作为web框架。

##安装poetry
```bash
$ curl -sSL https://install.python-poetry.org | python3

$ poetry --version
```
### poetry 配置查看
```bash
$ poetry config --list
```

### poetry 配置在项目目录下创建虚拟环境
```bash
$ poetry config virtualenvs.in-project true
```



## 功能特性

- 监听 GitLab Webhook 事件
- 支持以下 MR 相关通知：
  - MR 创建
  - MR 更新
  - MR 关闭
  - MR 重开
  - MR 合并
  - MR 评论
  - MR 评审通过/不通过

## 环境要求

- Python 3.8+
- 企业微信群机器人
- GitLab 实例（支持 Webhook）

## 安装

1. 克隆仓库 
   ```bash
   git clone  [repository-url]
   cd [repository-name]
   ```
2. 安装依赖
   ```bash
   poetry install
   ```
3. 配置 config.toml
   修改config.example.toml为config.toml，并填入相关配置 务必使用自己的配置
   其中branches_regex.versions 是目标分支的正则表达式，支持多个，如果匹配到多个分支，则发送通知到群
4. 运行
   ```bash
   poetry run python ./src/run.py
   ```

## gitlab 配置

1. 创建企业微信群机器人
2. 获取机器人 webhook 地址
3. 配置 gitlab webhook
   - 进入项目设置 -> Webhooks
   - URL: `http://your-server:8000/gitlab-hook`
   - 配置 gitlab webhook secret
   - Secret Token: 配置文件中的 webhook_secret
   - 选择触发事件：
     - Merge requests events
     - Comments

