from typing import Callable, Type, TypeVar
from pathlib import Path
from datetime import datetime
import multiprocessing

from ..database import (
    Curd,
    SqlAlChemyBase,
    IpInfoDeepseekR1,
    IpInfoDeepseekV3,
    IpInfoDoubaoThinkPro,
    IpInfoDoubaoVersionPro,
)
from tk_base_utils.file import create_file_name_with_time,get_abs_file_path
from ..models import RspResult
from ..message import message

import re

T = TypeVar("T")


# 用 ## 替换 Windows 非法字符
def sanitize_windows_filename(filename):
    # 定义非法字符（包括 <>:"/\|?*）
    illegal_chars = r'[<>:"/\\|?*]'

    # 替换非法字符为 ##
    sanitized = re.sub(illegal_chars, "##", filename)

    # 处理保留名称（如 CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9）
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LP3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if sanitized.upper() in reserved_names:
        sanitized = f"#{sanitized}#"  # 在保留名称前后加 # 避免冲突

    # 去除结尾的空格和点
    sanitized = sanitized.rstrip(" .")

    return sanitized


def create_file_name_by_rsp(file_path: Path, rsp: RspResult):
    first_data = rsp.data[0]
    last_data = rsp.data[-1]
    first_rsp_info = sanitize_windows_filename(
        f"{first_data.source_ip_query}-{first_data.source_character_query}"
    )
    last_rsp_info = sanitize_windows_filename(
        f"{last_data.source_ip_query}-{last_data.source_character_query}"
    )
    new_file_path = file_path.with_name(
        f"{file_path.stem}_{first_data.ai_model}_{first_rsp_info}_{last_rsp_info}{file_path.suffix}"
    )
    return new_file_path


def add_time_path(file_path: Path, path_time: datetime | None = None):
    if path_time is None:
        return file_path
    else:
        file_parent_path = file_path.parent
        file_name = file_path.name
        file_new_parent_path = file_parent_path / path_time.strftime("%Y%m%d_%H%M%S")
        file_new_parent_path.mkdir(parents=True, exist_ok=True)
        file_new_path = file_new_parent_path / file_name
        return file_new_path


def success_rsp_local_save(
    config: dict, rsp: RspResult, path_time: datetime | None = None
) -> None:
    file_path = add_time_path(get_abs_file_path(config["SUCCESS_RSP_FILE_PATH"]), path_time)
    file_name = create_file_name_by_rsp(file_path, rsp)
    with open(file_name, "w", encoding="utf-8") as f:
        for temp in rsp.data:
            f.write(f"{temp}\n")


def fail_rsp_local_save(
    config: dict, rsp: RspResult, path_time: datetime | None = None
) -> None:
    file_path = add_time_path(get_abs_file_path(config["FAIL_RSP_FILE_PATH"]), path_time)
    file_name = create_file_name_with_time(file_path)
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(rsp.fail_data)


def insert_error_save(
    config: dict, rsp: RspResult, path_time: datetime | None = None
) -> None:
    file_path = add_time_path(get_abs_file_path(config["INSERT_ERROR_FILE_PATH"]), path_time)
    file_name = create_file_name_by_rsp(file_path, rsp)
    with open(file_name, "w", encoding="utf-8") as f:
        for temp in rsp.data:
            f.write(f"{temp}\n")


class MultiProcessSave(object):
    """多进程保存类，用于将数据持久化到数据库和本地文件

    该类创建一个新的进程来处理数据保存任务，主进程可以通过队列发送数据到保存进程
    """

    TERMINATION_SENTINEL = None

    def __init__(
        self,
        config: dict,
        success_rsp_local_save: Callable = success_rsp_local_save,
        fail_rsp_local_save: Callable = fail_rsp_local_save,
        insert_error_save: Callable = insert_error_save,
        db_curd_class: Type[T] = Curd,
        runtime: str | None = None,
    ):
        """初始化多进程保存类

        Args:
            config: 配置信息
            success_rsp_local_save: 成功响应保存函数
            fail_rsp_local_save: 失败响应保存函数
            insert_error_save: 插入错误保存函数
            db_curd_class: 数据库CRUD类
            runtime: 运行时间，默认为当前时间
        """
        self.config = config
        self.success_rsp_local_save = success_rsp_local_save
        self.fail_rsp_local_save = fail_rsp_local_save
        self.insert_error_save = insert_error_save
        self.db_curd_class = db_curd_class
        self.runtime = runtime or datetime.now()
        # 创建进程间通信的队列
        self.queue = multiprocessing.Queue()
        # 保存进程
        self.process = None

    def start_process(self):
        """启动保存进程"""
        self.process = multiprocessing.Process(target=self._run, daemon=True)
        self.process.start()
        message.info(f"数据保存进程已启动，进程ID: {self.process.pid}")

    def join_process(self):
        """等待保存进程结束"""
        if self.process and self.process.is_alive():
            # 发送终止信号
            self.queue.put(self.TERMINATION_SENTINEL)
            self.process.join()
            message.info("数据保存进程已终止")

    def terminate_process(self):
        """强制终止保存进程"""
        if self.process and self.process.is_alive():
            self.process.terminate()
            message.info("数据保存进程已强制终止")

    def send_data(self, data: list | dict | RspResult):
        """发送数据到保存进程

        Args:
            data: 要保存的数据，可以是列表、字典或RspResult对象
        """
        if isinstance(data, RspResult):
            # 如果是RspResult对象，直接发送
            self.queue.put(data)
        elif isinstance(data, list):
            # 如果是列表，封装为RspResult对象
            result = RspResult(status="success", message="数据保存成功", data=data)
            self.queue.put(result)
        elif isinstance(data, dict):
            # 如果是字典，封装为列表再封装为RspResult对象
            result = RspResult(status="success", message="数据保存成功", data=[data])
            self.queue.put(result)
        else:
            # 其他类型，封装为失败的RspResult对象
            result = RspResult(
                status="fail", message="数据类型不支持", fail_data=str(data)
            )
            self.queue.put(result)

    def _get_table(self,ai_model):
        """获取数据库表ORM对象"""
        mapping_dict = {
            "DEEPSEEK-R1": IpInfoDeepseekR1,
            "DEEPSEEK-V3": IpInfoDeepseekV3,
            "DOUBAO-THINKING-PRO": IpInfoDoubaoThinkPro,
            "DOUBAO-VISION-PRO": IpInfoDoubaoVersionPro,
        }
        return mapping_dict[ai_model]
    def db_save_func(self, data: RspResult):
        """数据库保存函数，用于将数据保存到数据库"""
        db_client = self.db_curd_class()
        data = [temp.model_dump() for temp in data.data]
        table = self._get_table(data[0]['ai_model'])
        try:
            return db_client.bulk_insert_ignore_in_chunks(table, data)
        except Exception as e:
            raise e

    def _run(self):
        """保存进程的运行函数"""
        inserted_count = 0
        fail_count = 0
        message.info(f"数据保存进程开始运行，运行时间: {self.runtime}")

        while True:
            try:
                # 从队列获取数据
                item: RspResult = self.queue.get()

                # 检查是否是终止信号
                if item is self.TERMINATION_SENTINEL:
                    message.info("收到终止信号，保存进程即将结束")
                    break

                # 处理失败数据
                if item.status == "fail":
                    self.fail_rsp_local_save(self.config, item, self.runtime)
                    fail_count += 1
                    message.info(f"保存失败数据到本地文件，失败原因: {item.message}")
                else:
                    # 处理成功数据
                    self.success_rsp_local_save(self.config, item, self.runtime)

                    # 保存到数据库
                    db_save_result = self.db_save_func(item)
                    inserted_count += db_save_result
                    message.info(f"成功保存{db_save_result}条数据到数据库和本地文件")
            except Exception as e:
                # 处理异常
                message.error(f"数据保存过程中发生异常: {str(e)}")
                try:
                    # 尝试保存失败数据
                    self.insert_error_save(self.config, item, self.runtime)
                    fail_count += 1
                except Exception as save_e:
                    message.error(f"保存失败数据时发生异常: {str(save_e)}")

        # 进程结束时输出统计信息
        message.info(
            f"从{self.runtime}开始多进程写入数据完毕，共成功{inserted_count}条，失败{fail_count}次"
        )
