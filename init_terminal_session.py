import os
import pty
import sys

def record_terminal_session(output_file_path="terminal_session.log"):
    """记录终端会话并保存到文件"""
    
    # 清空终端会话日志文件
    with open(output_file_path, "w") as f:
        f.write("")  # 清空文件内容
    
    def read(fd):
        """读取终端数据并写入文件"""
        data = os.read(fd, 1024)
        with open(output_file_path, "ab") as f:
            f.write(data)
        return data

    print(f"Recording terminal session to {output_file_path}. Press Ctrl+D to exit.")
    pty.spawn("/bin/bash", read)  # 启动 bash 并记录

if __name__ == "__main__":
    record_terminal_session()