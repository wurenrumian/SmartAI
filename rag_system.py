import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

# 加载环境变量
load_dotenv()

# 初始化OpenAI embeddings
embeddings = OpenAIEmbeddings()

def create_vector_store(directory, output_file):
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在。请确保已创建该目录并包含相关文件。")
        return None

    # 检查向量存储是否已存在
    if os.path.exists(output_file):
        print(f"向量存储 {output_file} 已存在，直接加载。")
        return FAISS.load_local(output_file, embeddings, allow_dangerous_deserialization=True)
    
    # 加载文档
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt') or filename.endswith('.md'):
            file_path = os.path.join(directory, filename)
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
    
    if not documents:
        print(f"警告：目录 {directory} 中没有找到文档。")
        return None

    # 分割文本
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    
    # 创建向量存储
    vector_store = FAISS.from_documents(texts, embeddings)
    
    # 保存向量存储
    vector_store.save_local(output_file)
    
    print(f"向量存储已创建并保存到 {output_file}")
    return vector_store

# 创建原则向量存储
principles_store = create_vector_store("Data/Principles", "principles_vector_store")

# 创建案例向量存储
examples_store = create_vector_store("Data/Examples", "examples_vector_store")

def search_relevant_info(query, k=2):
    principles_results = principles_store.similarity_search(query, k=k)
    examples_results = examples_store.similarity_search(query, k=k)
    
    return {
        "principles": principles_results,
        "examples": examples_results
    }

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)[:1000]  # 限制长度为1000字符

# 添加新的函数来处理用户查询
def handle_user_query(query, context):
    # 搜索相关信息
    results = search_relevant_info(query)
    
    # 构建 prompt
    prompt = ChatPromptTemplate.from_template("""
你是一个专门解决人情世故问题的AI助手。你的任务是帮助用户解决送礼和社交场合中的各种难题。在回答用户问题时，请遵循以下指导：

1. 参考原则：参考遵守原则向量库中的内容。这些原则是处理人情世故问题的经验。
2. 案例参考：在给出建议时，你可以参考案例向量库中的相关内容。这些案例可以帮助你提供更具体、更贴近实际的建议。
3. 回答结构：简要重述问题，给出基于原则的建议，举例说明，最后总结。
4. 语气和风格：保持友好、耐心和体贴的语气，使用礼貌、得体的措辞。
5. 如果涉及未明确提到的情况，进行合理推断，但要明确指出。
6. 不要引用用户不知道的东西，直接输出建议和话术。

对方背景信息：
身份：{identity}
性别：{gender}
家庭背景：{family_background}
事前背景：{prior_context}

用户问题：{query}

相关原则：
{principles}

相关案例：
{examples}

请根据以上信息，提供你的建议：
""")
    
    # 初始化 LLM
    model = ChatOpenAI(temperature=0.7, max_tokens=1000)
    
    # 创建处理链
    chain = (
        {"query": RunnablePassthrough(), 
         "principles": lambda x: format_docs(results["principles"]),
         "examples": lambda x: format_docs(results["examples"]),
         "identity": lambda x: context['identity'],
         "gender": lambda x: context['gender'],
         "family_background": lambda x: context['familyBackground'],
         "prior_context": lambda x: context['priorContext']}
        | prompt
        | model
        | StrOutputParser()
    )
    
    # 运行 chain
    response = chain.invoke(query)
    
    return response

# 使用示例
if __name__ == "__main__":
    if principles_store is None or examples_store is None:
        print("无法创建向量存储。请检查数据目录和文件。")
    else:
        query = "如何在领导生日时送礼？"
        context = {
            "identity": "员工",
            "gender": "男",
            "familyBackground": "普通家庭",
            "priorContext": "无"
        }
        response = handle_user_query(query, context)
        print(response)