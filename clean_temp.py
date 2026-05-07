import os
import shutil

# 清理临时文件和目录
def clean_temp_files():
    """
    清理临时文件和目录
    """
    print("开始清理临时文件和目录...")
    
    # 1. 清理临时工作目录
    temp_dir = r'd:\1111\temp整理'
    print(f"\n1. 清理临时工作目录: {temp_dir}")
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"✓ 已删除临时工作目录: {temp_dir}")
        else:
            print(f"✓ 临时工作目录不存在: {temp_dir}")
    except Exception as e:
        print(f"✗ 删除临时工作目录失败: {e}")
    
    # 2. 清理临时脚本文件
    print("\n2. 清理临时脚本文件...")
    script_files = [
        r'd:\1111\create_temp_dir.py',
        r'd:\1111\scan_files.py',
        r'd:\1111\analyze_files.py',
        r'd:\1111\organize_files.py',
        r'd:\1111\verify_organization.py'
    ]
    
    for script_file in script_files:
        try:
            if os.path.exists(script_file):
                os.remove(script_file)
                print(f"✓ 已删除脚本文件: {script_file}")
            else:
                print(f"✓ 脚本文件不存在: {script_file}")
        except Exception as e:
            print(f"✗ 删除脚本文件失败 {script_file}: {e}")
    
    # 3. 检查清理结果
    print("\n3. 检查清理结果...")
    if not os.path.exists(temp_dir):
        print(f"✓ 临时工作目录已成功清理")
    else:
        print(f"✗ 临时工作目录未完全清理")
    
    all_scripts_removed = True
    for script_file in script_files:
        if os.path.exists(script_file):
            all_scripts_removed = False
            break
    
    if all_scripts_removed:
        print(f"✓ 所有临时脚本文件已成功清理")
    else:
        print(f"✗ 部分临时脚本文件未清理")
    
    print("\n清理操作完成！")

# 主函数
def main():
    clean_temp_files()

if __name__ == "__main__":
    main()