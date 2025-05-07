from typing import Callable,Type,TypeVar
from pathlib import Path
from datetime import datetime


from ..database.models import IpInfoTable


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
            "ai_model": ai_model
        }
        for item in rsp
    ]
    
def fomart_rsp_str(rsp:str):
    if 'json' in rsp:
        pattern = r'```json\n([\s\S]*?)```'
        result = re.findall(pattern, rsp)[0].strip()
        return result
    
    return rsp
        


class MultiProcessingSave(object):
    TERMINATION_SENTINEL = None

    def __init__(
        self,
        temp_rsp_save_func: Callable,
        fail_rsp_save_func: Callable,
        db_curd_class:Type[T] ,
        temp_rsp_dir_path: Path,
        temp_rsp_save_file_name: str,
        fail_rsp_dir_path: Path,
        fail_rsp_save_file_name: str,
        db_model: IpInfoTable,
        runtime: str | None = None,
    ):
        self.temp_rsp_save_func = temp_rsp_save_func
        self.fail_rsp_save_func = fail_rsp_save_func
        self.db_curd_class = db_curd_class
        self.temp_rsp_save_dir = temp_rsp_dir_path
        self.temp_rsp_save_file_name = temp_rsp_save_file_name
        self.fail_rsp_save_dir = fail_rsp_dir_path
        self.fail_rsp_save_file_name = fail_rsp_save_file_name
        self.db_model = db_model
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
                item = self.queue.get()
                if item is self.TERMINATION_SENTINEL:
                    message.info("Terminating")
                    break
                self.temp_rsp_save_func(
                    self.temp_rsp_save_dir / self.runtime,
                    self.temp_rsp_save_file_name,
                    item,
                )
                db_save_result = db_client.add_or_update_table_banch(self.db_model, item)
                if db_save_result:
                    inserted_count += len(item)
                else:
                    self.fail_rsp_save_func(
                        self.fail_rsp_save_dir / self.runtime,
                        self.fail_rsp_save_file_name,
                        item,
                    )
                    fail_count += len(item)
            except Exception as e:
                fail_count += len(item)
                message.error(e)
            finally:
                message.info(
                    f"从{self.runtime}开始多线程写入数据完毕,共成功{inserted_count}条,失败{fail_count}条"
                )
