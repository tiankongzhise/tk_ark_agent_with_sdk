
def fomart_agent_rsp(rsp:list[dict],ai_model:str)->list[dict]:
    return[
        {
            'source_ip_query':item['IP称呼'],
            'source_character_query':item['角色名称'],
            'ai_rsp':{ai_model:item['IP官方名称']}

        } for item in rsp
    ]

