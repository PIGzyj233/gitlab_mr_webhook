from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.tasks.mr_summary import send_mr_summary
from src.config import settings
from src.handlers import webhook_handler
from src.utils.queue_handler import webhook_queue
from src.utils.logger import setup_logger
import json

logger = setup_logger()
scheduler = AsyncIOScheduler()

# 启动时验证配置
if not settings.wechat.bot_key or settings.wechat.bot_key == "your-wechat-bot-key":
    logger.error("WECHAT_BOT_KEY 未正确配置")
    raise ValueError("WECHAT_BOT_KEY is not properly configured")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动应用")
    scheduler.add_job(
            send_mr_summary,
            CronTrigger(
                day_of_week='mon',
                hour=16,
                minute=0
            ),
            id='mr_weekly_summary',
            name='MR每周汇总',
            misfire_grace_time=3600,
            coalesce=True,
            max_instances=1
        )
    scheduler.start()
    logger.info("调度器已启动")
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭，停止调度器...")
    scheduler.shutdown()
    logger.info("调度器已停止")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/gitlab-hook")
async def gitlab_webhook(request: Request):
    logger.info("收到新的 GitLab Webhook 请求")
    
    # 验证 Gitlab Secret Token
    gitlab_token = request.headers.get("X-Gitlab-Token")
    if gitlab_token != settings.gitlab.webhook_secret:
        logger.warning(f"无效的 Webhook Token: {gitlab_token}")
        raise HTTPException(status_code=403, detail="Invalid token")
    
    data = await request.json()
    event_type = request.headers.get("X-Gitlab-Event")
    
    # 调试模式日志记录
    if settings.app.debug:
        logger.debug("Webhook Headers:")
        for header, value in request.headers.items():
            logger.debug(f"{header}: {value}")
        
        logger.debug("Webhook Data:")
        logger.debug(json.dumps(data, ensure_ascii=False, indent=2))
        
        from src.utils.logger import log_webhook_data
        log_webhook_data(data, event_type)
    
    logger.info(f"处理事件类型: {event_type}")
    
    # 获取对应的处理函数
    handler = webhook_handler.get_event_handler(event_type)
    if not handler:
        logger.warning(f"不支持的事件类型: {event_type}")
        return Response(
            content=json.dumps({"status": "event not supported"}),
            media_type="application/json",
            status_code=status.HTTP_202_ACCEPTED
        )
    
    # 将任务添加到队列
    await webhook_queue.add_task(handler, data)
    logger.info(f"成功将 {event_type} 事件添加到处理队列")
    
    # 明确返回 202 Accepted 状态码
    return Response(
        content=json.dumps({"status": "accepted"}),
        media_type="application/json",
        status_code=status.HTTP_202_ACCEPTED
    )