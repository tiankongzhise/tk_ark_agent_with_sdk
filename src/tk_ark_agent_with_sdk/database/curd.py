
from tk_db_tool.curd import BaseCurd
from .models import IpInfoTable
from tk_db_tool import get_session
from typing import Type
from pydantic import BaseModel
from sqlalchemy import update
from ..message import message

class Curd(BaseCurd):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._init_query_mapping(IpInfoTable)
    
    def _format_data(self,data:dict|Type[IpInfoTable]|Type[BaseModel])->dict:
        if isinstance(data,IpInfoTable):
            if data.key_id:
                data.set_special_fields(['created_at','updated_at'])
            return data.to_dict()
        if isinstance(data,BaseModel):
            return data.model_dump()
        if isinstance(data,dict):
            return data
        raise TypeError('data must be dict or IpInfoTable or BaseModel')

    def _init_query_mapping(self,table:Type[IpInfoTable]):
        self.query_mapping = {}
        with get_session() as session:
            for item in session.query(table).all():
                unique_index = f"{item.source_ip_query}-{item.source_character_query}"
                self.query_mapping[unique_index] = {'key_id':item.key_id,'ai_rsp':item.ai_rsp}
    def add_or_update_table(self,table:Type[IpInfoTable],data:dict|Type[IpInfoTable]|Type[BaseModel]):
        try:
            with get_session() as session:
                temp_data = self._format_data(data)
                unique_index = f"{temp_data['source_ip_query']}-{temp_data['source_character_query']}"
                # 如果存在，则更新ai_rsp
                if self.query_mapping.get(unique_index,{}).get('ai_rsp'):
                    self.query_mapping[unique_index]['ai_rsp'].update(temp_data['ai_rsp'])
                    message.debug(f"self.query_mapping[{unique_index}]['ai_rsp']:{self.query_mapping[unique_index]['ai_rsp']}")
                    stmt = update(table).where(table.key_id==self.query_mapping[unique_index]['key_id']).values(ai_rsp=self.query_mapping[unique_index]['ai_rsp'])
                    session.execute(stmt)
                    return {'status':'success','operation':'update'}
                temp_table = table(**temp_data)
                session.add(temp_table)
                session.flush()
                self.query_mapping[unique_index] = {'key_id':temp_table.key_id,'ai_rsp':temp_table.ai_rsp}
                return {'status':'success','operation':'add'}
        except Exception as e:
            return {'status':'error','operation':'add','error':str(e)}



