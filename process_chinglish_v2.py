#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理中式英语对照表文件，彻底清理格式并删除重复条目
"""

def process_chinglish_file(file_path):
    """
    处理中式英语对照表文件
    :param file_path: 文件路径
    :return: 处理后的内容
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 提取标题
    title = "# 中式英语（Chinglish）全量分类清单\n\n"
    
    # 存储所有有效条目
    entries = []
    seen = set()
    
    # 遍历所有行，提取有效条目
    for line in lines:
        line = line.strip()
        
        # 跳过空行、标题行和分隔线
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('| ---') or line.startswith('| --'):
            continue
        if line.count('|') < 2:
            continue
        
        # 分割表格行
        parts = line.split('|')
        
        # 处理特殊表格（动词用法表）
        if '动词' in parts and '中式用法' in parts and '正确场景' in parts:
            continue  # 跳过表头
        
        # 提取中式英语和地道表达
        if len(parts) >= 3:
            chinglish = parts[1].strip()
            proper = parts[2].strip()
            
            # 过滤掉无效条目
            if not chinglish or not proper:
                continue
            if chinglish == proper:
                continue
            
            # 处理特殊格式
            if proper.startswith('|'):
                proper = proper[1:].strip()
            
            # 去重
            if (chinglish, proper) not in seen:
                seen.add((chinglish, proper))
                entries.append((chinglish, proper))
        
        # 处理动词表格内容
        elif len(parts) >= 4:
            verb = parts[1].strip()
            chinglish_usage = parts[2].strip()
            correct = parts[3].strip()
            
            if verb and chinglish_usage and correct:
                chinglish_combined = f"{verb}（{chinglish_usage}）"
                if (chinglish_combined, correct) not in seen:
                    seen.add((chinglish_combined, correct))
                    entries.append((chinglish_combined, correct))
    
    # 生成新的统一表格
    new_content = title
    new_content += '| 中式英语 | 地道表达 |\n'
    new_content += '| -------- | -------- |\n'
    
    for chinglish, proper in entries:
        new_content += f'| {chinglish} | {proper} |\n'
    
    return new_content

if __name__ == "__main__":
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    processed_content = process_chinglish_file(file_path)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"处理完成！文件已更新：{file_path}")
    print(f"处理后条目数：{len(processed_content.split('\n')) - 3}")
