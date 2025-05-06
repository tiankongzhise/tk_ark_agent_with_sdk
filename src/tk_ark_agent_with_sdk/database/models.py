from tk_db_tool import SqlAlChemyBase
from tk_db_tool.models import MixIn
from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import String,JSON,DateTime,func,UniqueConstraint
from datetime import datetime

class IpInfoTable(SqlAlChemyBase,MixIn):
    __tablename__ = 'ip_info'
    __table_args__ = (
        UniqueConstraint('source_ip_query','source_character_query', name='unique_ip_character'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_0900_ai_ci',
            'schema': 'test_db'
        }
    )

    key_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,comment='主键ID')
    source_ip_query: Mapped[str] = mapped_column(String(50),comment='查询的IP名称')
    source_character_query: Mapped[str] = mapped_column(String(50),comment='查询的角色名称')
    
    ai_rsp: Mapped[dict] = mapped_column(JSON,comment='AI的回复,由AI的模型和AI的回复组成')
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime,onupdate=func.now(),nullable=True,comment='更新时间')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_special_fields(['created_at','updated_at','key_id'])

class IpInfoDeepseekV3(SqlAlChemyBase,MixIn):
    __tablename__ = 'ip_info_deepseek_v3'
    __table_args__ = (
        UniqueConstraint('source_ip_query','source_character_query', name='unique_ip_character'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_0900_ai_ci',
            'schema': 'test_db'
        }
    )

    key_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,comment='主键ID')
    source_ip_query: Mapped[str] = mapped_column(String(50),comment='查询的IP名称')
    source_character_query: Mapped[str] = mapped_column(String(50),comment='查询的角色名称')
    ai_rsp: Mapped[str] = mapped_column(String(50),comment='AI的回复')
    ai_model: Mapped[str] = mapped_column(String(50),comment='AI的模型名称')
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime,onupdate=func.now(),nullable=True,comment='更新时间')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_special_fields(['created_at','updated_at','key_id'])

class IpInfoDeepseekR1(SqlAlChemyBase,MixIn):
    __tablename__ = 'ip_info_deepseek_r1'
    __table_args__ = (
        UniqueConstraint('source_ip_query','source_character_query', name='unique_ip_character'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_0900_ai_ci',
            'schema': 'test_db'
        }
    )

    key_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,comment='主键ID')
    source_ip_query: Mapped[str] = mapped_column(String(50),comment='查询的IP名称')
    source_character_query: Mapped[str] = mapped_column(String(50),comment='查询的角色名称')
    ai_rsp: Mapped[str] = mapped_column(String(50),comment='AI的回复')
    ai_model: Mapped[str] = mapped_column(String(50),comment='AI的模型名称')
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime,onupdate=func.now(),nullable=True,comment='更新时间')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_special_fields(['created_at','updated_at','key_id'])

class IpInfoDoubaoThinkPro(SqlAlChemyBase,MixIn):
    __tablename__ = 'ip_info_doubao_think_pro'
    __table_args__ = (
        UniqueConstraint('source_ip_query','source_character_query', name='unique_ip_character'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_0900_ai_ci',
            'schema': 'test_db'
        }
    )

    key_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,comment='主键ID')
    source_ip_query: Mapped[str] = mapped_column(String(50),comment='查询的IP名称')
    source_character_query: Mapped[str] = mapped_column(String(50),comment='查询的角色名称')
    ai_rsp: Mapped[str] = mapped_column(String(50),comment='AI的回复')
    ai_model: Mapped[str] = mapped_column(String(50),comment='AI的模型名称')
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime,onupdate=func.now(),nullable=True,comment='更新时间')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_special_fields(['created_at','updated_at','key_id'])

class IpInfoDoubaoVersionPro(SqlAlChemyBase,MixIn):
    __tablename__ = 'ip_info_doubao_version_pro'
    __table_args__ = (
        UniqueConstraint('source_ip_query','source_character_query', name='unique_ip_character'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_0900_ai_ci',
            'schema': 'test_db'
        }
    )

    key_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,comment='主键ID')
    source_ip_query: Mapped[str] = mapped_column(String(50),comment='查询的IP名称')
    source_character_query: Mapped[str] = mapped_column(String(50),comment='查询的角色名称')
    ai_rsp: Mapped[str] = mapped_column(String(50),comment='AI的回复')
    ai_model: Mapped[str] = mapped_column(String(50),comment='AI的模型名称')
    created_at: Mapped[datetime] = mapped_column(DateTime,default=func.now(),comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime,onupdate=func.now(),nullable=True,comment='更新时间')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_special_fields(['created_at','updated_at','key_id'])
