# 获取统一格式的终端ID
get_unified_terminal_id() {
    local tty_name=$(tty 2>/dev/null)
    if [[ "$tty_name" =~ pts/[0-9]+ ]]; then
        echo "pts_${tty_name#*pts/}"
    elif [[ -n "$TMUX" ]]; then
        # 在tmux中，使用窗格ID前2个字符
        echo "tmux_${TMUX_PANE:0:2}"
    else
        # 回退方案: 使用shell PID
        echo "pid_$$"
    fi
}

# config for ai_cli
function suggest_cmd() {
  local input="$*"
  local suggestion
  local term_id="$FTERMID"

  # 调用建议工具
  suggestion=$(/data/ai_cli/ai-cli-suggest "$input" "$HOME/terminal_logs/terminal_${term_id}.log")

  # 在终端下方显示建议（原命令保留在输入行）
  printf "\n建议命令:\n\033[1;33m%s\033[0m\n" "$suggestion" >&2
}

# 使用单引号确保 $READLINE_LINE 正确传递
bind -x '"\e\r": "suggest_cmd \"$READLINE_LINE\""'





# 增强版Ctrl+D处理
enhanced_ctrl_d() {
    local term_id=$(get_unified_terminal_id)
    local pid_file="$HOME/terminal_logs/terminal_${term_id}.pid"

    
    if [[ -f "$pid_file" ]]; then
        # 检查PID文件是否可读
        local recorder_pid=""
        if recorder_pid=$(cat "$pid_file" 2>/dev/null); then
            # 停止记录进程
            kill -TERM "$recorder_pid" 2>/dev/null
            # 移除标识
            PS1="$ORIG_PS1"
            echo "终端记录已停止"
        else
            echo "无法读取PID文件: $pid_file"
        fi
        
        # 如果是空行则退出
        [[ -z "$READLINE_LINE" ]] && exit
    else
        [[ -z "$READLINE_LINE" ]] && exit
    fi
}

# 检查Python是否可用
check_python() {
    if ! command -v python3 &>/dev/null; then
        echo "错误: 未找到python3，无法启动终端记录"
        return 1
    fi
    return 0
}

if [[ -n "$TERMINAL_RECORDING" ]]; then
    PS1="(log_session)$PS1"
fi

# 启动终端记录
start_terminal_logging() {
    # 避免重复初始化
    [[ "$TERMINAL_LOGGING_INIT" == "1" ]] && return
    [[ "$TERMINAL_RECORDING" == "1" ]] && return  # 避免在记录会话中再次记录
    
    export TERMINAL_LOGGING_INIT=1
    
    # 检查Python可用性
    check_python || return
    
    # 获取终端ID
    local term_id=$(get_unified_terminal_id)
    local script_path="/data/ai_cli/init_terminal_session.py"
    
    # 确认脚本存在
    if [[ ! -f "$script_path" ]]; then
        echo "错误: 找不到记录脚本: $script_path"
        return
    fi
    
    # 启动记录进程并传递term_id
    echo "父级进程 $$"
    python3 "$script_path" "$term_id" 

    
    # 修改提示符以指示正在记录
    PS1="$ORIG_PS1"
    echo "当前进程 $$"
    
    # 绑定Ctrl+D
    bind -x '"\C-d": enhanced_ctrl_d'
    
    echo "终端记录已启动 (ID: $term_id)"
}

# 主执行流程
if [[ $- == *i* ]]; then  # 确保在交互式shell中运行
    # 保存原始提示符
    [[ -z "$ORIG_PS1" ]] && ORIG_PS1="$PS1"
    
    # 延迟启动以避免冲突
    sleep 1 
    start_terminal_logging
fi