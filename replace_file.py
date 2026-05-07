#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
替换原文件
"""
import os

def replace_file():
    """
    替换原文件
    """
    old_file = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版.md"
    new_file = r"d:\1111\中式英语（Chinglish）全量分类清单_整理版_new.md"
    
    # 读取新文件内容
    with open(new_file, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    # 写入原文件
    with open(old_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 删除临时文件
    os.remove(new_file)
    
    print(f"文件替换完成！")
    print(f"原文件已更新")

if __name__ == "__main__":
    replace_file()
