# ai_cli
1. 初始化config，```python ai-cli-suggest --setup```，填写自己拥有的大模型参数
```
[DEFAULT]
api_key = 
base_url = 
model = ep-20250330114043-rjgt6
max_history_line = 30  #prompt会依赖30行命令行历史信息
show_confidence = False
cache_suggestions = False
```

2. 在.bashrc文件中设置快捷键alt+enter以及一些配置，在bashrc最后一行增加```source /data/ai_cli/init_terminal_session.sh```
