#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单直接的方式处理中式英语对照表
"""

def process_file():
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 提取有效条目
    entries = []
    seen = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        if line.startswith('| ---') or '中式英语' in line or '地道表达' in line or '动词' in line:
            continue
        
        # 处理表格行
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            
            # 寻找有效的中式英语-地道表达对
            i = 0
            while i < len(parts) - 1:
                chinglish = parts[i]
                proper = parts[i+1]
                
                # 跳过无效内容
                if not chinglish or not proper:
                    i += 1
                    continue
                if '-' * 5 in chinglish or '-' * 5 in proper:
                    i += 1
                    continue
                if '中式英语' in chinglish or '地道表达' in proper:
                    i += 1
                    continue
                
                # 添加有效条目
                if (chinglish, proper) not in seen:
                    seen.add((chinglish, proper))
                    entries.append((chinglish, proper))
                    i += 2
                else:
                    i += 1
    
    # 生成新内容
    new_content = "# 中式英语（Chinglish）全量分类清单\n\n"
    new_content += "| 中式英语 | 地道表达 |\n"
    new_content += "| -------- | -------- |\n"
    
    for chinglish, proper in entries:
        new_content += f"| {chinglish} | {proper} |\n"
    
    # 强制写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"处理完成！共处理 {len(entries)} 个条目")
    print(f"已删除 {len(seen)} 个重复条目")

if __name__ == "__main__":
    process_file()
