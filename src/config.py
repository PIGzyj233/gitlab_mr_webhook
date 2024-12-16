from pydantic import BaseModel
import tomli
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class GitLabConfig(BaseModel):
    api_url: str
    url: str
    access_token: str
    webhook_secret: str
    project_id: int

class WeChatConfig(BaseModel):
    bot_key: str

class ServerConfig(BaseModel):
    host: str
    port: int
    workers: int

class LogConfig(BaseModel):
    level: str
    max_size: int
    backup_count: int

class AppConfig(BaseModel):
    debug: bool

class BranchesRegexConfig(BaseModel):
    versions: list[str]

class Settings(BaseModel):
    gitlab: GitLabConfig
    wechat: WeChatConfig
    server: ServerConfig
    log: LogConfig
    app: AppConfig
    branches_regex: BranchesRegexConfig

    @classmethod
    def load_settings(cls, config_path: Optional[str] = None) -> 'Settings':
        try:
            if config_path is None:
                config_path = str(Path(__file__).parent.parent / "config.toml")

            config_file = Path(config_path)
            if not config_file.exists():
                logger.error(f"找不到配置文件: {config_file}")
                raise FileNotFoundError(f"Config file not found: {config_file}")

            with open(config_file, "rb") as f:
                config_dict = tomli.load(f)

            settings = cls(**config_dict)
            logger.info(f"成功加载配置文件: {config_file}")

            if settings.app.debug:
                # 在调试模式下打印配置（隐藏敏感信息）
                safe_config = config_dict.copy()
                if "gitlab" in safe_config:
                    safe_config["gitlab"]["access_token"] = "***"
                if "wechat" in safe_config:
                    safe_config["wechat"]["bot_key"] = "***"
                logger.debug(f"当前配置: {safe_config}")

            return settings

        except Exception as e:
            logger.error(f"加载配置文件时出错: {str(e)}", exc_info=True)
            raise

settings = Settings.load_settings()