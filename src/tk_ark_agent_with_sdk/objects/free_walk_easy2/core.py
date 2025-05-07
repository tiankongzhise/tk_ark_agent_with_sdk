import multiprocessing.process
from ...core import SyncAgentWithSdk
from ...database import (IpInfoDeepseekR1,
                         IpInfoDoubaoThinkPro,
                         IpInfoDeepseekV3,
                         IpInfoDoubaoVersionPro,
                         Curd

)
from ...utils import fomart_rsp

from tk_base_utils.file import get_abs_file_path
from tk_db_tool import get_session,init_db
from copy import deepcopy

import pandas as pd
import asyncio
import multiprocessing
import json

model_orm_mapping={
    'DOUBAO-THINKING-PRO': IpInfoDoubaoThinkPro,
    'DEEPSEEK-V3' : IpInfoDeepseekV3,
    'DEEPSEEK-R1' : IpInfoDeepseekR1,
    'DOUBAO-VISION-PRO' : IpInfoDoubaoVersionPro
}

class Run(SyncAgentWithSdk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=save,args=(self.ai_model,self.queue), daemon=True)
        self.process.start()
        init_db()
    
    
    model_id_mapping = {'DOUBAO-THINKING-PRO': 'ep-20250427171722-5fb9c',
        'DEEPSEEK-V3' : 'ep-20250427171507-l9cgg',
        'DEEPSEEK-R1' : 'ep-20250427171252-8kdjr',
        'DOUBAO-VISION-PRO' : 'ep-20250427172000-zbqrb'}

    SYSTEM_CONTENT = """
    你是一个IP数据库专家，负责将用户提供的IP称呼与角色组合规范化为标准格式。
    """

    PROMPT = """
    请按以下规则处理输入数据：  

    <输入格式说明>  
    输入数据为多行文本，每行格式为：  
    "IP称呼-角色名称"  
    示例输入：  
    孙悟空-齐天大圣  
    灭霸-萨诺斯  
    </输入格式说明>  

    <处理规则>  
    1. **官方名称优先**：若IP存在官方注册名称(如版权方公布名称)，必须使用该名称  
    2. **民间称呼判定**：若无官方名称，采用符合以下标准的民间称呼：  
    - 百度/谷歌搜索前3结果中出现频率最高  
    - 中文维基百科/萌娘百科等权威平台使用名称  
    - 相关贴吧/微博话题常用称呼  
    3. **无效输入处理**：若出现以下情况，在"IP官方名称"字段填"未知"：  
    - 格式不符合"IP称呼-角色名称"结构  
    - IP称呼存在拼写错误无法识别  
    - 经查证无任何可信来源支持  

    <输出要求>  
    生成包含所有有效条目的JSON数组，每个对象包含：  
    {  
    "IP称呼": "原始输入IP称呼",  
    "角色名称": "原始输入角色名称",  
    "IP官方名称": "规范后的标准名称/未知"  
    }  
    </输出要求>  

    <执行步骤>  
    1. 逐行解析输入，按"-"分割为IP称呼和角色名称  
    2. 对每个IP称呼执行以下操作：  
    a. 检查国家知识产权局商标数据库(模拟)  
    b. 查询版权方官网/官方公告(模拟)  
    c. 若未找到官方记录，检索主流平台的高频称呼  
    3. 生成最终JSON时：  
    - 保留原始输入的大小写格式  
    - 空值字段用null表示  
    - 数组按输入顺序排列  

    <示例>  
    输入：  
    皮卡丘-电气鼠  
    黑暗骑士-小丑  

    输出：  
    [  
    {  
        "IP称呼": "皮卡丘",  
        "角色名称": "电气鼠",  
        "IP官方名称": "宝可梦"  
    },  
    {  
        "IP称呼": "黑暗骑士",  
        "角色名称": "小丑",  
        "IP官方名称": "蝙蝠侠"  
    }  
    ]  
    </示例>  

    现在开始处理以下输入数据：  
    <输入数据>  
    {{IP_ROLE_PAIRS}}  
    </输入数据>  

    请确保：  
    - 不添加解释性文字  
    - 不使用Markdown格式  
    - JSON严格符合语法规范  
    - 数组元素顺序与输入顺序完全一致  
    """

    source_data_file_path = '$/src/tk_ark_agent_with_sdk/data/成都世界线自由行数据.xlsx'
    data_chunk_size = 100
    TERMINATION_SENTINEL = None
    def get_ip_role_pairs(self,limit:int|None = None) -> list[str]:
        """获取源数据"""
        file_path = get_abs_file_path(self.source_data_file_path)
        df = pd.read_excel(file_path, sheet_name="Sheet1")
        
        ip = df["IP"].tolist()
        character = df["角色"].tolist()
        ip_role_pairs = [f"{i}-{j}" for i, j in zip(ip, character)]
        if limit is not None:
            ip_role_pairs = ip_role_pairs[:limit]
        return ip_role_pairs
    
    def init_agent(self)->SyncAgentWithSdk:
        sync_agent = SyncAgentWithSdk()
        sync_agent.set_model_mapping(self.model_id_mapping)
        sync_agent.set_stream(False)
        sync_agent.set_system_content(self.SYSTEM_CONTENT)
        sync_agent.set_ai_model(self.ai_model)
        return sync_agent
    
    def get_db_data(self,table) -> list:
        self.query_mapping = {}
        with get_session() as session:
            for item in session.query(table.source_ip_query,table.source_character_query,table.key_id).all():
                unique_index = f"{item.source_ip_query}-{item.source_character_query}"
                self.query_mapping[unique_index] = item.key_id
    def filter_new_ip_role_pairs(self,ip_role_pairs:list) -> list:
        return [ip_role_pair for ip_role_pair in ip_role_pairs if ip_role_pair not in list(self.query_mapping.keys())]
    def create_prompt(self,ip_role_pairs:list)->str:
        prompt_template = deepcopy(self.PROMPT)
        result = prompt_template.replace(
            "{{IP_ROLE_PAIRS}}", "\n".join(ip_role_pairs)
        )
        
        return result
    async def run(self) -> None:
        ip_role_pairs = self.get_ip_role_pairs()
        table = model_orm_mapping.get(self.ai_model)
        self.get_db_data(table)
        new_ip_role_pairs = self.filter_new_ip_role_pairs(ip_role_pairs[:10])
        sync_agent = self.init_agent()
        tasks=[]
        for i in range(0,len(new_ip_role_pairs),self.data_chunk_size):
            query_ip_role_pairs = new_ip_role_pairs[i:i+self.data_chunk_size]
            prompt = self.create_prompt(query_ip_role_pairs)
            sync_agent.set_prompt(prompt)
            tasks.append(sync_agent.run())
        for complete_task in asyncio.as_completed(tasks):
            rsp = await complete_task
            try:
                print(f'rsp:{rsp}')
                rsp_json = json.loads(rsp)
                fomated_rsp = fomart_rsp(rsp_json,self.ai_model)
            except Exception as e:
                print(e)
                continue
            print(f'{self.ai_model} get rsp,{fomated_rsp}')
            self.queue.put(fomated_rsp)
        self.queue.put(self.TERMINATION_SENTINEL)
        self.process.join()
        
        
def save(ai_model,queue):
    db_client = Curd()
    table = model_orm_mapping[ai_model]
    while True:
        rsp = queue.get()
        if rsp is None:
            break
        db_client.bulk_insert_ignore_in_chunks(table,rsp)
        print(f"{ai_model} save {len(rsp)} rsp")
