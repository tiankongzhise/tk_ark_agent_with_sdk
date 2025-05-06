from pathlib import Path
from ..message import message
import re
# 用 ## 替换 Windows 非法字符
def sanitize_windows_filename(filename):
    # 定义非法字符（包括 <>:"/\|?*）
    illegal_chars = r'[<>:"/\\|?*]'
    
    # 替换非法字符为 ##
    sanitized = re.sub(illegal_chars, '##', filename)
    
    # 处理保留名称（如 CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9）
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LP3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    if sanitized.upper() in reserved_names:
        sanitized = f"#{sanitized}#"  # 在保留名称前后加 # 避免冲突
    
    # 去除结尾的空格和点
    sanitized = sanitized.rstrip(' .')
    
    return sanitized
def create_file_name_by_rsp(file_path:Path,rsp:list):
    first_rsp_info = sanitize_windows_filename(f'{rsp[0]["source_ip_query"]-rsp[0]["source_character_query"]}')
    last_rsp_info = sanitize_windows_filename(f'{rsp[-1]["source_ip_query"]-rsp[-1]["source_character_query"]}')
    new_file_path = file_path.with_name(f"{file_path.stem}_{first_rsp_info}_{last_rsp_info}{file_path.suffix}")
    return new_file_path
    
def write_fail_rsp(dir_path:Path,file_name:str,rsp:list):
    """
    将未能正常写入数据库的rsp写入本地文件,降低AI的无效token占用
    """
    try:
        file_path = create_file_name_by_rsp(dir_path / file_name,rsp)
        #  创建文件
        if not file_path.exists():
            file_path.touch()
            
        with open(file_path,'w',encoding='utf-8') as f:
            f.write('\n'.join(rsp))
        return file_path.name
    except Exception as e:
        message.error(f"写入失败rsp文件失败,{e}")

def write_rsp(dir_path:Path,file_name:str,rsp:list):
    """
    将rsp写入本地文件
    """
    try:
        file_path = create_file_name_by_rsp(dir_path / file_name,rsp)
        if not file_path.exists():
            file_path.touch()
        with open(file_path,'w',encoding='utf-8') as f:
            f.write('\n'.join(rsp))
        return file_path.name
    except Exception as e:
        message.error(f"写入rsp文件失败,{e}")

