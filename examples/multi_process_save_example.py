# 多进程保存示例

from pathlib import Path
import time
import random

from src.tk_ark_agent_with_sdk.utils import MultiProcessSave
from src.tk_ark_agent_with_sdk.database import IpInfoDoubaoVersionPro
from src.tk_ark_agent_with_sdk.models import Response


def generate_sample_data(count: int = 10):
    """生成示例数据
    
    Args:
        count: 生成数据的数量
        
    Returns:
        生成的示例数据列表
    """
    data = []
    for i in range(count):
        data.append(Response(
            **{
                "IP称呼": f"测试IP{i}",
                "角色名称": f"测试角色{i}",
                "ai_model": "gpt-4",
                "IP官方名称": f"官方IP名称{i}"
            }
        ))
    return data


def main():
    # 设置文件路径
    temp_dir = Path("./temp_data")
    fail_dir = Path("./fail_data")
    
    # 确保目录存在
    temp_dir.mkdir(exist_ok=True)
    fail_dir.mkdir(exist_ok=True)
    
    # 创建多进程保存实例
    saver = MultiProcessSave(
        temp_rsp_file_path=temp_dir / "success.json",
        fail_rsp_file_path=fail_dir / "fail.json",
        db_table=IpInfoDoubaoVersionPro
    )
    
    # 启动保存进程
    saver.start_process()
    
    try:
        # 模拟数据生成和发送
        for i in range(5):
            print(f"生成第{i+1}批数据...")
            # 生成示例数据
            data = generate_sample_data(random.randint(5, 15))
            # 发送数据到保存进程
            saver.send_data(data)
            # 模拟处理间隔
            time.sleep(1)
            
        # 模拟发送单条数据
        single_data = Response(
            **{
                "IP称呼": "单条测试IP",
                "角色名称": "单条测试角色",
                "ai_model": "gpt-4",
                "IP官方名称": "单条官方IP名称"
            }
        )
        saver.send_data(single_data)
        
        # 等待所有数据处理完成
        print("等待数据处理完成...")
        time.sleep(3)
    finally:
        # 确保进程正常结束
        saver.join_process()
        
    print("示例运行完成，请查看temp_data和fail_data目录下的文件")


if __name__ == "__main__":
    main()
