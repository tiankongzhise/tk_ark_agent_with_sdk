
from typing import Any
from tk_base_utils import get_abs_file_path, load_toml, get_target_file_path
from tk_base_utils.file import get_abs_dir_path
from dotenv import load_dotenv

from ...core import AgentWithSdk
from ...database import Curd,IpInfoTable
from ...utils import MultiProcessingSave,fomart_agent_rsp
from ...file import write_fail_rsp, write_rsp


import pandas as pd
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

def init_agent(toml_config: dict) -> AgentWithSdk:
    agent = AgentWithSdk()
    agent.set_model_mapping(toml_config.get("AI_MODEL_MAPPING"))
    agent.set_stream(toml_config.get("STREAM"))
    agent.set_print_console(toml_config.get("PRINT_CONSOLE"))
    agent.set_system_content(toml_config.get("SYSTEM_CONTENT"))
    return agent

def create_prompt(prompt_template:str,ip_role_pairs:list)->str:
    result = prompt_template.replace(
            "{{IP_ROLE_PAIRS}}", "\n".join(ip_role_pairs)
        )
    return result

def get_ip_role_pairs(limit:int=None):
    toml_config = get_config()
    
    source_data = get_source_data(toml_config.get("SOURCE_DATA_FILE_PATH"))

    ip = source_data["IP"].tolist()
    character = source_data["角色"].tolist()
    ip_role_pairs = [f"{i}-{j}" for i, j in zip(ip, character)]
    
    if limit: 
        ip_role_pairs = ip_role_pairs[:limit]
    return ip_role_pairs
    
def run_with_ai_model(ai_model:str):
    toml_config = get_config()

    db_client = Curd()
    
    temp_rsp_dir_path = get_abs_dir_path(toml_config.get("TEMP_RSP_DIR_PATH"))
    fail_rsp_dir_path = get_abs_dir_path(toml_config.get("FAIL_RSP_DIR_PATH"))
    
    temp_rsp_file_name=toml_config.get("TEMP_RSP_FILE_NAME")
    fail_rsp_file_name=toml_config.get("FAIL_RSP_FILE_NAME")
    
    ai_models = list(toml_config.get("AI_MODEL_MAPPING").keys())
    
    bentch_size = toml_config.get("CHAT_BATCH_SIZE")
    
    agent = init_agent(toml_config)
    
    ip_role_pairs = get_ip_role_pairs(10)
    for i in range(0,len(ip_role_pairs),bentch_size):
        query_ip_role_pairs = ip_role_pairs[i:i+bentch_size]
        prompt = create_prompt(toml_config.get("PROMPT"),query_ip_role_pairs)
        agent.set_ai_model(ai_model)
        agent.set_prompt(prompt)
        rsp = agent.run()
        rsp_dict = json.loads(rsp)
        fomarted_rsp = fomart_agent_rsp(rsp_dict,ai_model)
        db_client.add_or_update_table_banch(IpInfoTable,fomarted_rsp)
    
    
        
        
