import requests
from src.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class WeChatBot:
    @staticmethod
    async def send_message(content: str, mentioned_users: list = None):
        """发送企业微信机器人消息"""
        webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={settings.wechat.bot_key}"
        
        # 替换内容中的双引号为单引号
        content = content.replace('"', "'")
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        if mentioned_users:
            message["markdown"]["mentioned_list"] = mentioned_users
            
        if settings.app.debug:
            logger.info(f"企业微信机器人地址: {webhook_url}")
            logger.info(f"发送企业微信机器人消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(webhook_url, json=message)
            response_json = response.json()
            
            if response.status_code != 200 or response_json.get('errcode', 0) != 0:
                logger.error(f"发送消息失败: {response_json}")
            else:
                logger.info("消息发送成功")
                
            return response_json
            
        except Exception as e:
            logger.error(f"发送消息时出错: {str(e)}", exc_info=True)
            raise 