from tk_base_utils import load_toml,get_current_dir_path


from ...core import SyncAgentWithSdk

from ...utils import fomart_rsp_str

from ...models import AgentSetting,Response,RspResult

from copy import deepcopy
import json
class SyncArkAgent(SyncAgentWithSdk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def set_agent_toml(self) -> dict:
        """
        从当前路径下的config.toml文件中获取agent的配置信息,
        并将配置信息保存到self.agent_toml中
        返回None
        """
        current_path = get_current_dir_path()
        toml_file_path = current_path / 'config.toml'
        self.agent_toml =  load_toml(toml_file_path)
    
    def set_agent_setting(self):
        self.set_agent_toml()
        agent_setting =  AgentSetting.toml_mapping(self.agent_toml)
        agent_setting = agent_setting.model_dump()
        for k,v in agent_setting.items():
            setattr(self,k,v)
    
    def set_prompt(self, ip_role_pairs):
        prompt_template = deepcopy(self.prompt_template)
        prompt_template = prompt_template.replace("{{IP_ROLE_PAIRS}}", "\n".join(ip_role_pairs))
        super().set_prompt(prompt_template)
    
    async def run(self,ip_role_pairs:list[str],ai_model:str|None = None) -> RspResult:
        self.set_agent_setting()
        if ai_model: 
            self.set_ai_model(ai_model)
        self.set_prompt(ip_role_pairs)
        rsp = await super().run()
        try:
            fomated_rsp_str = fomart_rsp_str(rsp)
            rsp_dict = json.loads(fomated_rsp_str)
            if isinstance(rsp_dict,list):
                response = [Response(**{**item,'ai_model':self.ai_model}) for item in rsp_dict]
            elif isinstance(rsp_dict,dict):
                response = [Response(**{**rsp_dict,'ai_model':self.ai_model})]
            else:
                raise ValueError(f"rsp_dict is not a list or dict:{rsp_dict}") 
            return RspResult(data=response,message="success",status="success")
        except Exception as e:
            return RspResult(fail_data=rsp+f'_@#ai_model={ai_model}',message=str(e),status="fail")
