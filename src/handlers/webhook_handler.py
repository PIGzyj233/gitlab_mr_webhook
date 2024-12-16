from src.utils.wechat_bot import WeChatBot
from src.utils.gitlab_api import GitlabAPI
from src.utils.markdown import md
import logging
import re
from src.config import settings


logger = logging.getLogger(__name__)

def is_target_branch(branch_name: str) -> bool:
    """检查分支是否是目标分支"""
    return any(re.match(pattern, branch_name) for pattern in settings.branches_regex.versions)

async def handle_merge_request(data: dict):
    """处理合并请求事件"""
    try:
        action = data["object_attributes"]["action"]
        mr = data["object_attributes"]
        project = data["project"]
        target_branch = mr['target_branch']
        
        if not is_target_branch(target_branch):
            logger.info(f"跳过非master分支的MR: {mr['title']}")
            return
        logger.info(f"处理合并请求事件: {action}")
        logger.info(f"MR标题: {mr['title']}, 项目: {project['name']}")
        assignee = data['assignees'][0]['name']
        reviewer = data['reviewers'][0]['name']
        author = GitlabAPI.get_user_info(data['object_attributes']['author_id'])['name']
        gitlab_link = GitlabAPI.get_merge_request_url_from_webhook(data)
        messages = {
            "open": (
                md("有新的合并请求").info().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line() +
                md(f"评审:").info().quote() + md(reviewer).mark().new_line() +
                md(f"经办人:").info().quote() + md(assignee).mark().new_line()
            ),
            "close": (
                md("你的MR已关闭").warning().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line()
            ),
            "reopen": (
                md("你的MR已重新打开").warning().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line() +
                md(f"评审人:").info().quote() + md(reviewer).mark().new_line() +
                md(f"经办人:").info().quote() + md(assignee).mark().new_line()
            ),
            "update": (
                md("MR存在更新，请拨冗查看").warning().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"评审:").info().quote() + md(reviewer).mark().new_line()
            ),
            "merge": (
                md("MR请求已合并").success().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line()
            ),
            "approved": (
                md("MR请求已评审通过，请您合并").success().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"经办人:").info().quote() + md(assignee).mark().new_line()
            ),
            "unapproved": (
                md("MR请求未评审通过，请根据评审意见修改代码").error().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"分支: {target_branch}").quote().new_line() +
                md(f"标题: {mr['title']}").quote().new_line() +
                md(f"内容：{mr['description']}").quote().new_line() +
                md(f"链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line()
            )
        }
        
        if action in messages:
            message = messages[action]
            logger.info(f"发送MR {action}通知: {mr['title']}")
            await WeChatBot.send_message(str(message))
        else:
            logger.warning(f"未知的MR动作类型: {action}")
            
    except Exception as e:
        logger.error(f"处理MR消息时出错: {str(e)}", exc_info=True)
        raise

async def handle_note(data: dict):
    """处理评论事件"""
    try:
        note = data["object_attributes"]
        project = data["project"]
        mr = data['merge_request']
        target_branch = mr['target_branch']
        
        gitlab_link = GitlabAPI.get_merge_request_url_from_webhook(data)
        auther_id = data['merge_request']['author_id']
        author = GitlabAPI.get_user_info(auther_id)['name']
        if note["noteable_type"] == "MergeRequest":
            logger.info(f"处理评论事件: {note['note']}")
            message = (
                md("你的MR有新的评论，请及时查看").error().bold().new_line() +
                md(f"项目: {project['name']}").quote().new_line() +
                md(f"目标分支: {target_branch}").quote().new_line() +
                md(f"评论内容：{note['description']}").quote().new_line() +
                md(f"MR链接: {gitlab_link}").quote().new_line() +
                md(f"申请人:").info().quote() + md(author).mark().new_line()
            )
            await WeChatBot.send_message(str(message))
    except Exception as e:
        logger.error(f"处理评论消息时出错: {str(e)}", exc_info=True)
        raise

def get_event_handler(event_type: str):
    """获取事件对应的处理函数"""
    handlers = {
        "Merge Request Hook": handle_merge_request,
        "Note Hook": handle_note,
    }
    return handlers.get(event_type) 