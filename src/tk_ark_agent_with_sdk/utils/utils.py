from typing import Callable, Type, TypeVar
from pathlib import Path
from datetime import datetime


from ..database import Curd, SqlAlChemyBase
from ..file import write_rsp, write_fail_rsp
from ..models import RspResult

from ..message import message
import re

import multiprocessing

T = TypeVar("T")


def fomart_agent_rsp(rsp: list[dict], ai_model: str) -> list[dict]:
    return [
        {
            "source_ip_query": item["IP称呼"],
            "source_character_query": item["角色名称"],
            "ai_rsp": {ai_model: item["IP官方名称"]},
        }
        for item in rsp
    ]


def fomart_rsp(rsp: list[dict], ai_model: str) -> list[dict]:
    return [
        {
            "source_ip_query": item["IP称呼"],
            "source_character_query": item["角色名称"],
            "ai_rsp": item["IP官方名称"],
            "ai_model": ai_model,
        }
        for item in rsp
    ]


def fomart_rsp_str(rsp: str):
    if "json" in rsp:
        pattern = r"```json\n([\s\S]*?)```"
        result = re.findall(pattern, rsp)[0].strip()
        return result

    return rsp


class MultiProcessingSave(object):
    TERMINATION_SENTINEL = None

    def __init__(
        self,
        temp_rsp_file_path: Path,
        fail_rsp_file_path: Path,
        db_table: Type[SqlAlChemyBase],
        temp_rsp_save_func: Callable = write_rsp,
        fail_rsp_save_func: Callable = write_fail_rsp,
        db_curd_class: Type[T] = Curd,
        runtime: str | None = None,
    ):
        self.temp_rsp_file_path = temp_rsp_file_path
        self.fail_rsp_file_path = fail_rsp_file_path
        self.temp_rsp_save_func = temp_rsp_save_func
        self.fail_rsp_save_func = fail_rsp_save_func
        self.db_curd_class = db_curd_class
        self.db_table = db_table
        self.runtime = runtime or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.queue = multiprocessing.Queue()

    def process_start(self):
        self.process = multiprocessing.Process(target=self.run, daemon=True)
        self.process.start()

    def process_join(self):
        self.process.join()

    def sent_rsp(self, rsp: list | dict):
        if isinstance(rsp, list):
            temp_rsp = rsp
        else:
            temp_rsp = [rsp]
        self.queue.put(temp_rsp)

    def run(self):
        inserted_count = 0
        fail_count = 0
        db_client = self.db_curd_class()
        while True:
            try:
                item: RspResult = self.queue.get()
                if item is self.TERMINATION_SENTINEL:
                    message.info("Terminating")
                    break
                if item.status == "fail":
                    self.fail_rsp_save_func(
                        self.fail_rsp_file_path.parent / self.runtime,
                        self.fail_rsp_file_path.name,
                        item.data,
                    )
                else:
                    data = [temp.model_dump() for temp in item.data]
                    self.temp_rsp_save_func(
                        self.temp_rsp_file_path.parent / self.runtime,
                        self.temp_rsp_file_path.name,
                        data,
                    )
                    db_save_result = db_client.bulk_insert_ignore_in_chunks(
                        self.db_table, data
                    )
                    inserted_count += len(db_save_result)
            except Exception as e:
                self.fail_rsp_save_func(
                    self.fail_rsp_file_path.parent / self.runtime,
                    self.fail_rsp_file_path.name,
                    data,
                )
                fail_count += len(item)
                message.error(e)
            finally:
                message.info(
                    f"从{self.runtime}开始多线程写入数据完毕,共成功{inserted_count}条,失败{fail_count}条"
                )
