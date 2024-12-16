from datetime import datetime
import logging
import sys
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler
from src.config import settings

def setup_logger():
    """配置日志系统"""
    # 创建logs目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    logger = logging.getLogger()
    # 在调试模式下设置为DEBUG级别
    logger.setLevel(logging.DEBUG if settings.app.debug else logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        log_dir / "webhook.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 在调试模式下创建单独的调试日志文件
    if settings.app.debug:
        debug_handler = RotatingFileHandler(
            log_dir / "webhook.debug.log",
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        logger.addHandler(debug_handler)
    
    # 为某些模块单独设置日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logger

def log_webhook_data(data: dict, event_type: str):
    """记录webhook详细数据（仅在调试模式下）"""
    if not settings.app.debug:
        return
        
    log_dir = Path("logs/webhook_data")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # 使用时间戳和事件类型作为文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{event_type.replace(' ', '_')}.json"
    
    with open(log_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2) 