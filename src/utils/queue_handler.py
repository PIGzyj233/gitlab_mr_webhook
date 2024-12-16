import asyncio
from typing import Any, Callable, Coroutine
from collections import deque
import logging

logger = logging.getLogger(__name__)

class WebhookQueue:
    def __init__(self):
        self.queue = deque()
        self.is_processing = False
        self._task = None
        logger.info("WebhookQueue 初始化完成")

    async def add_task(self, handler: Callable[[dict], Coroutine[Any, Any, None]], data: dict):
        """添加任务到队列"""
        self.queue.append((handler, data))
        logger.info(f"新任务已添加到队列，当前队列长度: {len(self.queue)}")
        
        if not self.is_processing:
            logger.info("启动队列处理器")
            self._task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """处理队列中的任务"""
        self.is_processing = True
        logger.info("开始处理队列任务")
        
        try:
            while self.queue:
                handler, data = self.queue.popleft()
                logger.info(f"正在处理任务，剩余任务数: {len(self.queue)}")
                
                try:
                    await handler(data)
                    logger.info("任务处理成功")
                except Exception as e:
                    logger.error(f"处理webhook消息时出错: {str(e)}", exc_info=True)
        finally:
            self.is_processing = False
            logger.info("队列处理完成")

webhook_queue = WebhookQueue()