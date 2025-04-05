# convert_obsidian.py
import re
import os
import sys
from urllib.parse import quote

def convert_obsidian_md(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    input_dirname = os.path.basename(input_dir)  # 只取文件夹名

    def replace_image(match):
        img_name = match.group(1)
        # 构建路径：dirname/image.png，并进行 URL 编码
        rel_path = quote(f"{input_dirname}/{img_name}")
        return f"![{img_name}]({rel_path})"

    # 替换图片语法
    content = re.sub(r'!\[\[(.*?)\]\]', replace_image, content)

    # 替换 $$公式$$ 为 <div class="math">...</div>
    content = re.sub(r'\$\$(.*?)\$\$', r'<div class="math">\1</div>', content, flags=re.DOTALL)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 转换成功！输出文件：{output_path}")

if __name__ == '__main__':
    input_file = sys.argv[1]
    filename = os.path.splitext(os.path.basename(input_file))[0]
    parent_dir = os.path.dirname(os.path.dirname(input_file))
    output_dir = os.path.join(parent_dir, "github_markdown")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}-git.md")

    convert_obsidian_md(input_file, output_path)
