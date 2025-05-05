from typing import Any

from dotenv import load_dotenv
from tk_base_utils import get_abs_file_path, load_toml, get_target_file_path
from tk_base_utils.file import get_abs_dir_path


from ...core import SyncAgentWithSdk
from ...message import message
from ...database import Curd,IpInfoTable
from ...utils import MultiProcessingSave
from ...file import write_fail_rsp, write_rsp

import pandas as pd


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


def init_agent(toml_config: dict) -> SyncAgentWithSdk:
    sync_agent = SyncAgentWithSdk()
    sync_agent.set_model_mapping(toml_config.get("AI_MODEL_MAPPING"))
    sync_agent.set_stream(toml_config.get("STREAM"))
    sync_agent.set_print_console(toml_config.get("PRINT_CONSOLE"))
    sync_agent.set_system_content(toml_config.get("SYSTEM_CONTENT"))
    return sync_agent


async def run():
    toml_config = get_config()

    db_client = Curd()
    
    temp_rsp_save_dir = get_abs_dir_path(toml_config.get("TEMP_RSP_SAVE_DIR"))
    fail_rsp_save_dir = get_abs_dir_path(toml_config.get("FAIL_RSP_SAVE_DIR"))

    mt_process = MultiProcessingSave(
        temp_rsp_save_func=write_rsp,
        fail_rsp_save_func=write_fail_rsp,
        db_save_func=db_client.add_or_update_table_banch,
        temp_rsp_save_dir=temp_rsp_save_dir,
        temp_rsp_save_file_name=toml_config.get("TEMP_RSP_SAVE_FILE_NAME"),
        fail_rsp_save_dir=fail_rsp_save_dir,
        fail_rsp_save_file_name=toml_config.get("FAIL_RSP_SAVE_FILE_NAME"),
        db_model=IpInfoTable,
        runtime=toml_config.get("RUNTIME"),
    )
    
    ai_models = list(toml_config.get("AI_MODEL_MAPPING").keys())

    chat_batch_size = toml_config.get("CHAT_BATCH_SIZE")
    
    source_data = get_source_data(toml_config.get("SOURCE_DATA_FILE_PATH"))

    ip = source_data["IP"].tolist()
    character = source_data["角色"].tolist()
    ip_role_pairs = [f"{i}-{j}" for i, j in zip(ip, character)]

    test_ip_role_pairs = ip_role_pairs[:10]

    sync_agent = init_agent(toml_config)

    tasks = []
    mt_process.process_start()
    
    for i in range(0,len(test_ip_role_pairs),chat_batch_size):
        query_ip_role_pairs = test_ip_role_pairs[i:i+chat_batch_size]
        prompt = toml_config.get("PROMPT").replace(
        "{{IP_ROLE_PAIRS}}", "\n".join(query_ip_role_pairs)
    )
        for ai_model in ai_models:
            sync_agent.set_ai_model(ai_model)
            sync_agent.set_prompt(prompt)
            task = sync_agent.run()
            tasks.append(task)
            
            
        
    message.info(rsp)
