from datetime import datetime
import logging
import re
from src.utils.gitlab_api import GitlabAPI
from src.utils.wechat_bot import WeChatBot
from src.utils.markdown import md
from src.config import settings

logger = logging.getLogger(__name__)

def is_target_branch(branch_name: str) -> bool:
    return any(re.match(pattern, branch_name) for pattern in settings.branches_regex.versions)

async def send_mr_summary():
    """发送每周MR汇总"""
    try:
        # 获取所有项目的未完成MR
        mrs = GitlabAPI.get_project_merge_requests(settings.gitlab.project_id, state="opened")
        
        # 过滤目标分支的MR
        filtered_mrs = [mr for mr in mrs if is_target_branch(mr.get('target_branch', ''))]
        
        if not filtered_mrs:
            logger.info("没有未完成的目标分支MR")
            return
        
        # 获取当前时间
        now = datetime.now(datetime.fromisoformat('2024-01-01T00:00:00+00:00').tzinfo)
        
        # 构建消息
        message = (
            md("MR周报汇总").info().bold().new_line() +
            md(f"统计时间: {now.strftime('%Y-%m-%d %H:%M')}").new_line() +
            md(f"待处理MR数量: {len(filtered_mrs)}").new_line() +
            md("---").new_line()
        )
        
        # 按目标分支分组
        branch_groups = {}
        for mr in filtered_mrs:
            target_branch = mr.get('target_branch', '未知分支')
            if target_branch not in branch_groups:
                branch_groups[target_branch] = []
            branch_groups[target_branch].append(mr)
        
        # 按分支输出MR信息
        for branch, branch_mrs in branch_groups.items():
            message = message + md(f"\n分支: {branch}").bold().new_line()
            
            # 对每个分支内的MR按时间排序
            branch_mrs.sort(key=lambda x: x['created_at'], reverse=True)
            
            for mr in branch_mrs:
                created_at = datetime.fromisoformat(mr['created_at'].replace('Z', '+00:00'))
                days_old = (now - created_at).days
                author_name = mr.get('author', {}).get('name', '未知作者')
                
                mr_line = (
                    md(f"[{mr['title']}]({mr['web_url']})").new_line() +
                    md(f"提交人: {author_name}  ").info() +
                    md(f"创建时间: {created_at.strftime('%Y-%m-%d')} ({days_old}天)").new_line()
                )
                
                message = message + mr_line
            
            message = message + md("---").new_line()
        
        # 添加提醒信息
        message = message + md("请及时处理您负责的合并请求").warning()
        
        # 发送消息
        await WeChatBot.send_message(str(message))
        logger.info("已发送MR周报")
        
    except Exception as e:
        logger.error(f"发送MR周报时出错: {str(e)}", exc_info=True)
