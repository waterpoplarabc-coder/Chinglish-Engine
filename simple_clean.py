#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理中式英语对照表，只保留有效条目并重新排版
"""
import re

def main():
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有有效的中式英语-地道表达对
    # 匹配所有表格行，忽略表头和分隔线
    pattern = re.compile(r'\|\s*([^|\n]+?)\s*\|\s*([^|\n]+?)\s*\|', re.MULTILINE)
    matches = pattern.findall(content)
    
    # 去重并过滤无效条目
    unique_entries = set()
    for match in matches:
        chinglish, proper = match
        # 跳过表头和分隔线
        if '中式英语' in chinglish or '地道表达' in proper or '动词' in chinglish or '中式用法' in proper:
            continue
        # 跳过无效内容
        if not chinglish or not proper or chinglish == proper:
            continue
        # 跳过包含分隔符的无效行
        if '-' * 5 in chinglish or '-' * 5 in proper:
            continue
        # 添加有效条目
        unique_entries.add((chinglish, proper))
    
    # 转换为列表并排序
    sorted_entries = sorted(unique_entries, key=lambda x: x[0])
    
    # 生成全新的文件内容
    new_content = "# 中式英语（Chinglish）全量分类清单\n\n"
    new_content += "| 中式英语 | 地道表达 |\n"
    new_content += "| -------- | -------- |\n"
    
    for chinglish, proper in sorted_entries:
        new_content += f"| {chinglish} | {proper} |\n"
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"处理完成！")
    print(f"原始文件行数: {len(content.splitlines())}")
    print(f"处理后文件行数: {len(new_content.splitlines())}")
    print(f"有效条目数: {len(sorted_entries)}")

if __name__ == "__main__":
    main()
