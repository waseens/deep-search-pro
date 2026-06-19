# 导入依赖
from ragflow_sdk import RAGFlow #链接rag服务的客户端
from rawflow.rag_config import _load_ragflow_env


# 创建一个ragflow的客户端
api_key , base_url =_load_ragflow_env()
ragflow_client = RAGFlow(api_key=api_key,base_url=base_url)



# 1. 查询现在知识库中有哪些聊天助手和对应知识库的信息 （方便我们知道rag可以给我们提供哪些数据）
def get_assistant_list():
    # 1. 创建ragflow客户端
    # 2. ragflow客户端查询所有的聊天助手 page: int = 1, page_size: int = 30
    chat_list = ragflow_client.list_chats()
    # 3. 查询聊天助手的知识库信息
    count_chat_info = "" #存储所有会话信息
    for chat in chat_list:
        dataset_names = []
        dataset_list = chat.datasets #当前聊天助手关联的知识库
        if dataset_list and isinstance(dataset_list,list):
            # 知识库的name
            for dataset in dataset_list:
                print(dataset)
                dataset_names.append(dataset['name']) # 将一个助手的知识库的名字加入到列表中

        # 拼接下当前助手的信息 + 知识库信息
        # 法律资源小助手  xxxxxx  关联知识库：xx、xxx、xxx
        count_chat_info += f"助手名称:{chat.name};功能介绍：{chat.description}; 关联的知识库：{'、'.join(dataset_names)} \n"
    # 4. 拼接助手和知识库信息，返回供模型参考（lm知道你哪个助手干啥事，可以调用对应的助手）
    return count_chat_info

# 2. 对某个助手进行提问（创建会话 -》 提问 -》 删除会话）
def ask_question(chat_name,question):
    """
    向某个助手发起提问： 1. 创建一个会话 2.提问 3.关闭会话！
    :param chat_name: 助手的名字！上一个工具get_assistant_list告诉大模型的只有名字
    :param question: 本次提问的问题
    :return: 返回提问的结果
    """
    """
                                                ---> dataset 
       agent 我们 ----》 session  --》 chat(助手) ---> dataset 
                                                ---> dataset 
    """
    # 1. 创建ragflow客户端
    # 2. 查询对应name的chat
    chats = ragflow_client.list_chats(name=chat_name)
    use_chat = chats[0] #选中我们要使用的助手
    # 3. chat上创建一个会话
    session = use_chat.create_session(name="temp_session_ask")
    # 4. 使用会话进行提问
    # 返回的提问结果是流式
    response = session.ask(question = question,stream=True)
    # 接收总结果
    result = ""
    # 流的每一部分的对象 part
    for part in response:
        # 数据存在对象中content上！！
        print(part.content)
        result = part.content
    # 5. 关闭提问的会话
    # chat -> 关闭 -》  session
    use_chat.delete_sessions(ids=[session.id])
    # 6. 返回结果
    return result

if __name__ == '__main__':
    print(get_assistant_list())
    print(ask_question("法律援助助手", "我把人打残疾了怎么办！"))