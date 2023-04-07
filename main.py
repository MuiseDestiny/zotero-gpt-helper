import os
import sys
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAIChat
from llama_index.indices.vector_store.base_query import GPTVectorStoreIndexQuery, QueryBundle
from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex, Document, ServiceContext, LLMPredictor, PromptHelper

app = Flask(__name__)

# 请手动创建下面打开的txt并填写你的密钥
with open("OPENAI_API_KEY.txt", "r", encoding="utf-8") as f:
  os.environ["OPENAI_API_KEY"] = f.read()

# 创建一个文件夹用于存放缓存，相对目录
cache = "cache"
if not os.path.exists(cache):
  os.mkdir(cache)

@app.route('/getRelatedText', methods=['POST'])
def getRelatedText():
  args = request.get_json()
  print("key", args["id"])
  print("queryText", args["queryText"])
  print("fullText", len(args["fullText"]), args["fullText"][:20])
  json_file = "{}/{}.json".format(cache, args["id"])
  max_input_size = 4000
  chunk_size_limit = 500
  max_chunk_overlap = 20
  num_output = 5
  if (not os.path.exists(json_file)):
    documents = [Document(text=args["fullText"])]
    # 按最大token数500来把原文档切分为多个小的chunk，每个chunk转为向量，并构建索引
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
          model_name="gpt-3.5-turbo-0301",
          openai_api_key=os.environ["OPENAI_API_KEY"]
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
  else:
    index = GPTSimpleVectorIndex.load_from_disk(json_file)

  llm_predictor = LLMPredictor(llm=OpenAIChat(
      temperature=0, model_name="gpt-3.5-turbo"))
  prompt_helper = PromptHelper(
      max_input_size=max_input_size, num_output=num_output, max_chunk_overlap=max_chunk_overlap, chunk_size_limit=chunk_size_limit)
  service_context = ServiceContext.from_defaults(
      llm_predictor=llm_predictor, prompt_helper=prompt_helper)
  query_object = GPTVectorStoreIndexQuery(index.index_struct, service_context=service_context,
                                          similarity_top_k=num_output, vector_store=index._vector_store, docstore=index._docstore)
  query_bundle = QueryBundle(args["queryText"])
  nodes = query_object.retrieve(query_bundle)
  print("return", len(nodes))
  return jsonify([n.node.text for n in nodes])

if __name__ == '__main__':
    app.run(debug=True)






