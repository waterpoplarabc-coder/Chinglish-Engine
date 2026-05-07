#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确处理中式英语对照表，只保留有效条目并统一格式
"""

def process_chinglish_precise(file_path):
    """
    精确处理中式英语对照表文件
    :param file_path: 文件路径
    :return: 处理后的内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 存储所有有效条目
    valid_entries = set()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 跳过所有分隔线和表头
        if line.startswith('| ---') or '中式英语' in line or '地道表达' in line or '动词' in line:
            continue
        
        # 处理各种表格行
        if '|' in line:
            # 分割并清理
            parts = [p.strip() for p in line.split('|') if p.strip()]
            
            # 处理正常的2列条目
            if len(parts) == 2:
                chinglish, proper = parts
                if chinglish and proper and not chinglish.startswith('-') and not proper.startswith('-'):
                    valid_entries.add((chinglish, proper))
            
            # 处理包含多余分隔符的情况
            elif len(parts) > 2:
                # 寻找有效的中式英语-地道表达对
                for i in range(len(parts) - 1):
                    part1 = parts[i]
                    part2 = parts[i+1]
                    # 跳过分隔符
                    if part1.startswith('-') or part2.startswith('-'):
                        continue
                    # 跳过无效内容
                    if not part1 or not part2:
                        continue
                    # 添加有效对
                    valid_entries.add((part1, part2))
    
    # 转换为列表并排序
    sorted_entries = sorted(valid_entries, key=lambda x: x[0])
    
    # 生成统一格式的新文件
    new_content = "# 中式英语（Chinglish）全量分类清单\n\n"
    new_content += "| 中式英语 | 地道表达 |\n"
    new_content += "| -------- | -------- |\n"
    
    for chinglish, proper in sorted_entries:
        new_content += f"| {chinglish} | {proper} |\n"
    
    return new_content

if __name__ == "__main__":
    file_path = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    processed_content = process_chinglish_precise(file_path)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    print(f"处理完成！文件已更新：{file_path}")
    print(f"处理后条目数：{len(processed_content.split('\n')) - 3}")
