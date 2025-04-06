import os
import pty
import fcntl
from datetime import datetime
import sys
import errno
import signal

def record_terminal_session(term_id, output_dir="~/terminal_logs"):
    """接收从Bash传递的term_id"""
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用传入的term_id
    lock_file = output_dir+f"/terminal_{term_id}.lock"
    pid_file = output_dir+f"/terminal_{term_id}.pid"
    
    # 尝试获取锁
    try:
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, OSError) as e:
        print(f"⚠️ Session already active (Terminal: {term_id}): {e}", file=sys.stderr)
        return
    
    # 写入当前进程ID
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    #timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(output_dir, f"terminal_{term_id}.log")
    with open(log_file, 'w') as f:
        f.write('')
    
    # 设置信号处理函数
    def handle_signal(signum, frame):
        cleanup()
        if signum == signal.SIGTERM:
            sys.exit(0)
    
    def cleanup():
        for f in [lock_file, pid_file]:
            try:
                os.unlink(f)
            except OSError:
                pass
        try:
            lock_fd.close()
        except:
            pass
    
    # 注册信号处理
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    def read(fd):
        try:
            data = os.read(fd, 4096)  # 增加缓冲区大小
            if data:
                try:
                    # 将数据写入日志文件
                    with open(log_file, 'ab') as f:
                        f.write(data)
                except Exception as e:
                    print(f"写入日志错误: {e}", file=sys.stderr)
            return data
        except Exception as e:
            print(f"读取错误: {e}", file=sys.stderr)
            return b''
    
    print(f"📝 Recording session to {log_file}", file=sys.stderr)
    
    try:
        # 设置环境变量
        os.environ['TERMINAL_RECORDING'] = '1'
        os.environ['FTERMID'] = term_id
        
        # 使用--login以确保加载用户配置
        pty.spawn(['/bin/bash', '--login'], read)
    except Exception as e:
        print(f"PTY错误: {e}", file=sys.stderr)
    finally:
        cleanup()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        record_terminal_session(sys.argv[1])
    else:
        print("Error: Terminal ID not provided", file=sys.stderr)
        sys.exit(1)