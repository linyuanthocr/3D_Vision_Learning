# convert_obsidian.py
import re
import os
import sys
from urllib.parse import quote

def convert_obsidian_md(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    input_dir = os.path.dirname(input_path)
    output_dir = os.path.dirname(output_path)

    def replace_image(match):
        img_name = match.group(1)
        # 获取完整图片原始路径
        abs_img_path = os.path.join(input_dir, img_name)
        # 计算相对路径（从 output_md 到图片）
        rel_path = os.path.relpath(abs_img_path, output_dir)
        return f"![{img_name}]({quote(rel_path)})"

    # 替换 Obsidian 图片语法
    content = re.sub(r'!\[\[(.*?)\]\]', replace_image, content)

    # 替换 LaTeX 公式块
    content = re.sub(r'\$\$(.*?)\$\$', r'<div class="math">\1</div>', content, flags=re.DOTALL)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 转换成功！输出路径: {output_path}")

if __name__ == '__main__':
    input_file = sys.argv[1]
    filename = os.path.splitext(os.path.basename(input_file))[0]
    parent_dir = os.path.dirname(os.path.dirname(input_file))
    output_dir = os.path.join(parent_dir, "github_markdown")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}-git.md")

    convert_obsidian_md(input_file, output_path)
