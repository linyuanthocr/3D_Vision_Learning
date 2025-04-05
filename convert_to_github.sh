#!/bin/bash

# 用法提示
if [ $# -ne 1 ]; then
  echo "❗用法: bash convert_to_github.sh path/to/your/file.md"
  exit 1
fi

# 输入文件路径
INPUT_FILE="$1"

# 调用 Python 脚本
python3 convert_obsidian.py "$INPUT_FILE"

