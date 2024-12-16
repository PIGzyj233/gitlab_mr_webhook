import datetime
from typing import Any, Dict, List, Optional
from fastapi import logger
import requests
from src.config import settings

class GitLabAPIError(Exception):
    """GitLab API 异常基类"""
    pass

class GitlabAPI:
    @staticmethod
    def _make_request(method: str, endpoint: str, params: dict = None, headers: dict = None) -> Optional[dict]:
        """
        发送请求到GitLab API
        
        Returns:
            Optional[dict]: 成功返回响应数据，失败返回None
        """
        if headers is None:
            headers = {}
        headers["PRIVATE-TOKEN"] = settings.gitlab.access_token
        
        url = f"{settings.gitlab.api_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(method, url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitLab API请求失败: {str(e)}, URL: {url}, Method: {method}")
            logger.error(f"请求参数: {params}")
            return None
        except ValueError as e:  # JSON解析错误
            logger.error(f"GitLab API响应解析失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"GitLab API未知错误: {str(e)}")
            return None

    @staticmethod
    def get_user_info(user_id: int) -> Optional[dict]:
        """获取GitLab用户信息"""
        result = GitlabAPI._make_request("GET", f"/users/{user_id}")
        if result is None:
            logger.warning(f"获取用户信息失败，用户ID: {user_id}")
            return {"name": "未知用户"}  # 返回默认值而不是None
        return result

    @staticmethod
    def get_merge_request_url_from_webhook(webhook_data: dict) -> str:
        """从webhook数据中获取合并请求的URL"""
        try:
            project_namespace: str = webhook_data['project']['namespace'].lower()
            project_name: str = webhook_data['project']['name'].lower()
            if webhook_data['event_type'] == 'note':
                mr_iid: int = webhook_data['merge_request']['iid']
            else:
                mr_iid: int = webhook_data['object_attributes']['iid']
            return f"{settings.gitlab.url}/{project_namespace}/{project_name}/-/merge_requests/{mr_iid}"
        except KeyError as e:
            logger.error(f"解析webhook数据失败: {str(e)}")
            return f"{settings.gitlab.url}"  # 返回基础URL而不是失败
    
    @staticmethod
    def get_project_merge_requests(project_id: int, state: str = "opened", created_after: datetime = None) -> List[Dict[str, Any]]:
        """获取项目的合并请求列表"""
        if created_after is None:
            created_after = datetime.datetime.now() - datetime.timedelta(days=30)
        
        params = {
            "state": state,
            "created_after": created_after.isoformat(),
            "order_by": "created_at",
            "sort": "desc",
            "per_page": 100
        }
        
        result = GitlabAPI._make_request("GET", f"/projects/{project_id}/merge_requests", params=params)
        if result is None:
            logger.warning(f"获取项目MR列表失败，项目ID: {project_id}")
            return []  # 返回空列表而不是None
        if settings.app.debug:
            logger.info(f"获取项目MR列表成功，项目ID: {project_id}, MR列表: {result}")
        return result
    
    @staticmethod
    def get_merge_request_details(project_id: int, mr_iid: int) -> Optional[Dict[str, Any]]:
        """获取特定合并请求的详细信息"""
        result = GitlabAPI._make_request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}")
        if result is None:
            logger.warning(f"获取MR详情失败，项目ID: {project_id}, MR IID: {mr_iid}")
            return {}  # 返回空字典而不是None
        return result
    
    @staticmethod
    def get_merge_request_changes(project_id: int, mr_iid: int) -> Optional[Dict[str, Any]]:
        """获取合并请求的变更内容"""
        result = GitlabAPI._make_request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}/changes")
        if result is None:
            logger.warning(f"获取MR变更内容失败，项目ID: {project_id}, MR IID: {mr_iid}")
            return {}  # 返回空字典而不是None
        return result
    
    @staticmethod
    def get_merge_request_approvals(project_id: int, mr_iid: int) -> Optional[Dict[str, Any]]:
        """获取合并请求的审批状态"""
        result = GitlabAPI._make_request("GET", f"/projects/{project_id}/merge_requests/{mr_iid}/approvals")
        if result is None:
            logger.warning(f"获取MR审批状态失败，项目ID: {project_id}, MR IID: {mr_iid}")
            return {"approved": False}  # 返回默认值而不是None
        return result
    

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加项目根目录到 Python 路径
    root_dir = str(Path(__file__).parent.parent.parent)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    # 设置日志
    from src.utils.logger import setup_logger
    logger = setup_logger()
    
    # 测试获取MR列表
    project_id = 266  # 替换为您的项目ID
    mrs = GitlabAPI.get_project_merge_requests(project_id)
    
    print("\n=== 最近一个月的开放MR列表 ===")
    for mr in mrs:
        print(f"\n标题: {mr.get('title')}")
        print(f"作者: {mr.get('author', {}).get('name')}")
        print(f"创建时间: {mr.get('created_at')}")
        print(f"状态: {mr.get('state')}")
        print(f"URL: {mr.get('web_url')}")
        print("-" * 50)
