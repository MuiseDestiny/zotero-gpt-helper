"""
温馨提示：
若你的代理仅支持`/v1/embeddings`和`v1/chat/completion`，需要进行如下设置：

`site-packages\openai\api_resources\abstract\engine_api_resource.py` L151 后添加

  url = "/v1/embeddings"
  params["model"] = "text-embedding-ada-002"
  del params["encoding_format"]
  
"""

import os
import re
import sys
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAIChat
from llama_index.indices.vector_store.base_query import GPTVectorStoreIndexQuery, QueryBundle
from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, Document, ServiceContext, LLMPredictor, PromptHelper
from llama_index.node_parser import SimpleNodeParser
import openai
parser = SimpleNodeParser()
app = Flask(__name__)

# 创建一个文件夹用于存放缓存，相对目录
cache = "cache"
if not os.path.exists(cache): os.mkdir(cache)
# 密钥前后显示字符个数

def hideText(s, n=6): 
  return s[:n] + (len(s) - n * 2) * "*" + s[-n:]

# 分隔符
sep = "##########################################"

# 设置
max_input_size = 4096
chunk_size_limit = 500
max_chunk_overlap = 20
num_output = 256

@app.route('/getRelatedText', methods=['POST'])
def getRelatedText():
  args = request.get_json()
  # 密钥
  secretKey = args["secretKey"]
  # 可以是代理
  api = args["api"]
  key = args["key"]
  queryText = args["queryText"]
  if not queryText: return jsonify(['You should input the question first!'])
  fullText = args["fullText"]
  paragraphs = fullText.split("\n\n")
  lines = f"""
    {sep}
    api: {api}
    secretKey: {hideText(secretKey)}
    key: {key}
    queryText: {queryText}
    fullText: total {len(paragraphs)} paragraphs, total length {len(fullText)}
    {sep}
  """
  print(
    "\n" + "\n".join([line.strip() for line in lines.split("\n") if len(line)]) + "\n"
  )
  os.environ["OPENAI_API_KEY"] = secretKey
  os.environ["OPENAI_API_BASE"] = api
  openai.api_base = api
  openai.api_key = secretKey
  json_file = "{}/{}.json".format(cache, key)
  if (not os.path.exists(json_file)):
    documents = [Document(text) for text in args["fullText"].split("\n\n")]
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
          temperature=0,
          model_name="text-embedding-ada-002",
          openai_api_key=secretKey,
          max_tokens=512
        )
    )
    prompt_helper = PromptHelper(max_input_size=max_input_size, num_output=num_output, max_chunk_overlap=max_chunk_overlap,
                                 chunk_size_limit=chunk_size_limit, separator=" ")

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper, chunk_size_limit=chunk_size_limit
    )
    index = GPTSimpleVectorIndex.from_documents(
        documents, service_context=service_context
    )
    # 保存索引
    index.save_to_disk(json_file)
    # 保存的PDF全文用于开发者测试使用，你可以注释这段
    with open(json_file.replace(".json", ".txt"), "w", encoding="utf-8") as f:
      f.write(args["fullText"])
  else:
    index = GPTSimpleVectorIndex.load_from_disk(json_file)

  llm_predictor = LLMPredictor(llm=OpenAIChat(
      temperature=0, 
      model_name="text-embedding-ada-002"),
  )
  prompt_helper = PromptHelper(
      max_input_size=max_input_size, num_output=num_output, max_chunk_overlap=max_chunk_overlap, chunk_size_limit=chunk_size_limit)
  service_context = ServiceContext.from_defaults(
      llm_predictor=llm_predictor, prompt_helper=prompt_helper)
  query_object = GPTVectorStoreIndexQuery(index.index_struct, service_context=service_context,
                                          similarity_top_k=20, vector_store=index._vector_store, docstore=index._docstore)
  query_bundle = QueryBundle(args["queryText"])
  nodes = query_object.retrieve(query_bundle)
  print("return nodes", len(nodes))
  texts = sorted([n.node.text for n in nodes], key=lambda x: len(x), reverse=True)
  response = jsonify(texts[:5])
  print(response)
  return response

if __name__ == '__main__':
    app.run(debug=False, port=5000)






