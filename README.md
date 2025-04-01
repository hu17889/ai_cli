# ai_cli
1. 初始化命令行记录文件，用于prompt中，执行init_terminal_session.py 
2. 设置快捷键alt+enter，
···shell
function suggest_cmd() {
  local input="$*"
  local suggestion

  # 调用建议工具
  suggestion=$(/data/ai_cli/ai-cli-suggest "$input")

  # 在终端下方显示建议（原命令保留在输入行）
  printf "\n建议命令:\n\033[1;33m%s\033[0m\n" "$suggestion" >&2
}

# 使用单引号确保 $READLINE_LINE 正确传递
bind -x '"\e\r": "suggest_cmd \"$READLINE_LINE\""'

···