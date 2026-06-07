"""
RAG 模块 — 检索增强生成

负责：
1. 读取文件
2. 切分文本（chunking）
3. 向量化（embedding）
4. 存入向量数据库
5. 检索相关内容

原理：
  "向量"就是一组数字，用来表示文本的"含义"。
  意思相近的文本，向量也相近。
  所以找相关内容 = 找向量最相似的文本块。
"""

import os
from pathlib import Path

# sentence-transformers: 本地运行的 embedding 模型
# 第一次运行会下载模型（约 80MB），之后从缓存加载
from sentence_transformers import SentenceTransformer

# chromadb: 本地向量数据库，不需要启动服务器
import chromadb


# ============================================================
# 1. 文本切分 (Chunking)
# ============================================================

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    把长文本切成小块。

    为什么要切？
      - LLM 的 context window 有限，不能把整本书塞进去
      - 太长的文本 embedding 效果差
      - 切块后可以精确定位哪一段和问题相关

    参数:
        text: 原始文本
        chunk_size: 每块的目标字符数
        overlap: 块之间的重叠字符数（防止重要信息被切断）

    返回:
        文本块列表
    """
    # 按段落先拆分
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 如果当前块加上新段落不超过限制，就合并
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            # 当前块已满，保存它
            if current_chunk:
                chunks.append(current_chunk)
            # 新段落太长的话，直接作为一块（或进一步切分）
            if len(para) > chunk_size:
                # 按句子切分长段落
                sentences = para.replace("。", "。\n").replace(". ", ".\n").split("\n")
                temp = ""
                for sent in sentences:
                    if len(temp) + len(sent) < chunk_size:
                        temp += sent
                    else:
                        if temp:
                            chunks.append(temp)
                        temp = sent
                if temp:
                    current_chunk = temp
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================
# 2. 向量化 + 存储
# ============================================================

class VectorStore:
    """
    向量数据库封装。

    用 ChromaDB 存储文本块和它们的向量。
    提供"搜索相似文本"的功能。
    """

    def __init__(self, collection_name: str = "rag_docs"):
        # 加载 embedding 模型
        # all-MiniLM-L6-v2: 小巧、快速、效果不错
        # 第一次运行会自动下载
        print("正在加载 embedding 模型...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # 创建 ChromaDB 客户端（数据存在内存中）
        # 如果想持久化，改成: PersistentClient(path="./chroma_db")
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 用余弦相似度
        )
        print("向量数据库就绪。")

    def add_documents(self, chunks: list[str], source: str = "unknown"):
        """
        把文本块加入向量数据库。

        流程:
            文本块 → embedding 模型 → 向量 → 存入 ChromaDB
        """
        if not chunks:
            return

        # 生成向量
        embeddings = self.model.encode(chunks).tolist()

        # 生成 ID
        ids = [f"{source}_chunk_{i}" for i in range(len(chunks))]

        # 存入 ChromaDB
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=[{"source": source} for _ in chunks],
        )

        print(f"已添加 {len(chunks)} 个文本块（来源: {source}）")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        搜索和问题最相关的文本块。

        流程:
            问题 → embedding → 和数据库中的向量比较 → 返回最相似的 top_k 个

        返回:
            [{"text": "...", "source": "...", "score": 0.85}, ...]
        """
        # 把问题向量化
        query_embedding = self.model.encode([query]).tolist()

        # 在 ChromaDB 中搜索
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        # 整理结果
        found = []
        for i in range(len(results["documents"][0])):
            found.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })

        return found


# ============================================================
# 3. 文件加载
# ============================================================

def load_file(file_path: str) -> str:
    """读取文本文件内容"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_and_index(file_path: str, store: VectorStore) -> int:
    """
    加载文件 → 切块 → 存入向量数据库。

    返回:
        处理的块数
    """
    content = load_file(file_path)
    chunks = chunk_text(content)
    source = Path(file_path).name
    store.add_documents(chunks, source=source)
    return len(chunks)
