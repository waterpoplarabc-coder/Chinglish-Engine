#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理中式英语对照表，删除重复条目并重新排版
"""

import re

def process_chinglish_file(file_path):
    """
    处理中式英语对照表文件
    :param file_path: 文件路径
    :return: 处理后的内容
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.match(r'(#.*?\n\n)', content)
    title = title_match.group(1) if title_match else "# 中式英语（Chinglish）全量分类清单\n\n"
    
    # 识别特殊表格（动词用法表）
    verb_table_pattern = re.compile(r'(\|\s*动词\s*\|.*?\|\s*正确场景\s*\|\n\|.*?\|\n)(.*?)(?=\n\|\s*中式英语\s*\|)', re.DOTALL)
    verb_table_match = verb_table_pattern.search(content)
    verb_table = verb_table_match.group(0) if verb_table_match else ""
    
    # 提取所有中式英语-地道表达表格
    table_pattern = re.compile(r'\|\s*中式英语\s*\|.*?\|\n\|.*?\|\n(.*?)(?=\n\|\s*中式英语\s*\||\Z)', re.DOTALL)
    tables = table_pattern.findall(content)
    
    # 提取所有条目
    entries = set()
    
    for table_content in tables:
        # 解析表格行
        lines = table_content.strip().split('\n')
        for line in lines:
            if line.strip() and not line.strip().startswith('| ---'):
                # 分割表格行
                parts = line.split('|')
                if len(parts) >= 3:
                    chinglish = parts[1].strip()
                    proper = parts[2].strip()
                    if chinglish and proper:
                        entries.add((chinglish, proper))
    
    # 保留动词表格中的特殊条目
    if verb_table:
        verb_entries = verb_table.split('\n')[2:]
        for entry in verb_entries:
            if entry.strip() and not entry.strip().startswith('| ---'):
                parts = entry.split('|')
                if len(parts) >= 4:
                    verb = parts[1].strip()
                    chinglish_usage = parts[2].strip()
                    correct = parts[3].strip()
                    if verb and chinglish_usage and correct:
                        entries.add((f"{verb}（{chinglish_usage}）", correct))
    
    # 转换为列表并排序（保持原顺序）
    unique_entries = []
    seen = set()
    
    # 再次遍历原始内容，保持顺序
    all_lines = content.split('\n')
    for line in all_lines:
        if line.strip() and not line.strip().startswith('| ---') and '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                chinglish = parts[1].strip()
                proper = parts[2].strip()
                if chinglish and proper and (chinglish, proper) not in seen:
                    unique_entries.append((chinglish, proper))
                    seen.add((chinglish, proper))
    
    # 生成新的表格
    new_content = title
    
    # 添加动词表格（如果有）
    if verb_table:
        new_content += verb_table + '\n\n'
    
    # 添加主表格
    new_content += '| 中式英语 | 地道表达 |\n'
    new_content += '| -------- | -------- |\n'
    
    for chinglish, 地道 in unique_entries:
        new_content += f'| {chinglish} | {地道} |\n'
    
    return new_content

if __name__ == "__main__":
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    processed_content = process_chinglish_file(file_path)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"处理完成！文件已更新：{file_path}")
    print(f"原始条目数：未知，处理后条目数：{len(processed_content.split('\n')) - 3}")
