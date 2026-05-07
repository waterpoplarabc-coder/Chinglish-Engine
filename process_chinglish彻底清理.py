#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理中式英语对照表，删除所有格式问题和重复条目
"""

def process_chinglish彻底清理(file_path):
    """
    彻底清理中式英语对照表文件
    :param file_path: 文件路径
    :return: 处理后的内容
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有有效条目，忽略所有格式
    entries = []
    seen = set()
    
    # 分割所有行
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') or line.startswith('| ---'):
            continue
        
        # 分割所有可能的表格行
        if '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            
            # 处理正常的中式英语-地道表达对
            if len(parts) == 2:
                chinglish, proper = parts
                if chinglish and proper and (chinglish, proper) not in seen:
                    seen.add((chinglish, proper))
                    entries.append((chinglish, proper))
            
            # 处理包含额外分隔符的情况
            elif len(parts) > 2:
                # 寻找中式英语和地道表达的有效对
                for i in range(len(parts) - 1):
                    chinglish = parts[i]
                    proper = parts[i+1]
                    if chinglish and proper and '中式英语' not in chinglish and '地道表达' not in proper:
                        if (chinglish, proper) not in seen:
                            seen.add((chinglish, proper))
                            entries.append((chinglish, proper))
                    # 跳过表头
                    if '中式英语' in chinglish or '地道表达' in proper:
                        break
    
    # 生成全新的统一格式表格
    new_content = "# 中式英语（Chinglish）全量分类清单\n\n"
    new_content += "| 中式英语 | 地道表达 |\n"
    new_content += "| -------- | -------- |\n"
    
    for chinglish, proper in entries:
        new_content += f"| {chinglish} | {proper} |\n"
    
    return new_content

if __name__ == "__main__":
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    processed_content = process_chinglish彻底清理(file_path)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"彻底清理完成！文件已更新：{file_path}")
    print(f"处理后条目数：{len(processed_content.split('\n')) - 3}")
