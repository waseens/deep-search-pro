import os.path

# 导入依赖
from ragflow_sdk import RAGFlow #链接rag服务的客户端
from rawflow.rag_config import _load_ragflow_env


# 创建一个ragflow的客户端
api_key,base_url =_load_ragflow_env()
ragflow_client = RAGFlow(api_key=api_key,base_url=base_url)

# 代码创建知识库
def create_knowledge_base(knowledge_base_name, description):
    """
    创建知识库，有个名字和描述!
    名字和描述一定要准确的写！agent调用哪个聊天助手看聊天助手的描述和他对应知识库的描述！
    :param knowledge_base_name: 名字
    :param description: 描述
    :return:
    """
    ds = ragflow_client.create_dataset(name=knowledge_base_name, description=description,embedding_model="text-embedding-v3@Tongyi-Qianwen")
    print(f"创建知识库成功：{ds},{ds.id}")


if __name__ == '__main__':
    # 创建知识库
    create_knowledge_base("代码创建的知识库111", "今晚打老虎！！",)

# 使用上传文件到知识库
def upload_file_to_knowledge_base(kb_id, file_paths):
    """
    向知识库上传文件！ 文件可以是多个！！
    """
    # 1.链接ragflow的客户端
    # 2.获取传入文件的知识库对象
    datasets = ragflow_client.list_datasets(id=kb_id,page=1,page_size=10)
    dataset = datasets[0]
    # 3.文件包装成对应的上传dict格式
    document_list = [] # 存储上传文件的列表
    for file_path in file_paths:
        # file_path 文件的地址
        file_name = os.path.basename(file_path) # 获取文件名
        with open(file_path, 'rb') as f:
            blob = f.read()
            document_list.append({
                "display_name": file_name,
                "name": file_name,
                "blob": blob
            })
    # 4.进行文件上传了
    dataset.upload_documents(document_list)