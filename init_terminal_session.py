import os
import pty
import sys
from datetime import datetime

def record_terminal_session(output_dir="~/terminal_logs"):
    """记录终端会话，日志默认存储到用户根目录下的 terminal_logs/"""
    
    # 展开 ~ 为用户根目录（如 /home/username/）
    output_dir = os.path.expanduser(output_dir)
    
    # 确保日志目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成带时间戳的日志文件名（格式：terminal_YYYY-MM-DD_HH-MM-SS.log）
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"terminal_{timestamp}.log")
    
    def read(fd):
        """读取终端数据并写入文件"""
        data = os.read(fd, 1024)
        with open(output_file, "ab") as f:
            f.write(data)
        return data

    print(f"Recording terminal session to {output_file}. Press Ctrl+D to exit.")
    pty.spawn("/bin/bash", read)

if __name__ == "__main__":
    record_terminal_session()