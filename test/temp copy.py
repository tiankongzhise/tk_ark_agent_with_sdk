import os
from volcenginesdkarkruntime import Ark
from  dotenv import load_dotenv
load_dotenv()
system_content = '''你是一个IP数据库专家，负责将用户提供的IP称呼与角色组合规范化为标准格式。'''

prompt = """
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

ip=["星穹铁道","盗墓笔记","约会大作战","苏丹的游戏","崩坏三","黑暗欺骗","崩坏星穹铁道","东京喰种","吊带袜天使","永劫无间"]
character=["银狼","张起灵余岁","五河琴里","鲁梅拉","侵蚀人律","阿加莎","知更鸟","金木研","Stocking","魏轻"]
ip_role_pairs = [f"{i}-{j}" for i,j in zip(ip,character)]
query_str = prompt.replace("{{IP_ROLE_PAIRS}}", "\n".join(ip_role_pairs))

al_model = 'DOUBAO-THINKING-PRO'
model_id = "ep-20250427171722-5fb9c"

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    ak=os.environ.get("VOLC_ACCESSKEY"),
    sk=os.environ.get("VOLC_SECRETKEY")
)
print(os.environ.get("VOLC_ACCESSKEY"))
print(os.environ.get("VOLC_SECRETKEY"))
# # Non-streaming:
# print("----- standard request -----")
# completion = client.chat.completions.create(
#    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
#     model=model_id,
#     messages=[
#         {"role": "system", "content": system_content},
#         {"role": "user", "content": query_str},
#     ],
#     # 免费开启推理会话应用层加密，访问 https://www.volcengine.com/docs/82379/1389905 了解更多
#     extra_headers={'x-is-encrypted': 'true'},
# )
# print(completion.choices[0].message.content)

# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model=model_id,
    messages=[
        {"role": "system", "content": system_content},
        {"role": "user", "content": query_str},
    ],
    # 免费开启推理会话应用层加密，访问 https://www.volcengine.com/docs/82379/1389905 了解更多
    # extra_headers={'x-is-encrypted': 'true'},
    # 响应内容是否流式返回
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    print(chunk.choices[0].delta.content, end="")
print()