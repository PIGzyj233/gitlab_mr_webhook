import sys
import uvicorn
import os
from pathlib import Path
from config import settings

root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from main import app

if __name__ == "__main__":
    # 确保工作目录是项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.server.host,
        port=settings.server.port,
        workers=settings.server.workers,
        log_level=settings.log.level
    ) 