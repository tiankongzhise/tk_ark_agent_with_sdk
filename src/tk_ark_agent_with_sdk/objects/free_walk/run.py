from typing import Any

from dotenv import load_dotenv
from tk_base_utils import get_abs_file_path, load_toml, get_target_file_path
from tk_base_utils.file import get_abs_dir_path

from .core import SyncArkAgent
from ...message import message
from ...database import Curd,IpInfoTable
from ...utils import MultiProcessingSave,fomart_agent_rsp

import pandas as pd
import asyncio
import json

load_dotenv()


def get_source_data(source_file_path: str) -> pd.DataFrame:
    """
    获取源数据
    :param source_file_path: 源数据文件路径,从配置文件读取以.或者$开头的路径,
    :return: 源数据
    """
    source_file_path = source_file_path or "source_data.csv"
    file_path = get_abs_file_path(source_file_path)
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    return df


def get_config() -> dict[str, Any]:
    config_path = get_target_file_path("config.toml")
    toml_config = load_toml(config_path)
    return toml_config


async def run():
    toml_config = get_config()
    source_data = get_source_data(toml_config.get("SOURCE_DATA_FILE_PATH"))
    ip = source_data["IP"].tolist()
    character = source_data["角色"].tolist()
    ip_role_pairs = [f"{i}-{j}" for i, j in zip(ip, character)]

    test_ip_role_pairs = ip_role_pairs[:2]
    ark_agent = SyncArkAgent()
    return await ark_agent.run(test_ip_role_pairs)
        
