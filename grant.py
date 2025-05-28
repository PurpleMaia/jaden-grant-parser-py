'''
    main script that generates json of grant data
'''

from parser import parse
from rag import *
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import argparse
import json


def main() -> None:
    argparser = argparse.ArgumentParser(description="Parse a grant file (.pdf)")
    argparser.add_argument("filepath", type=str, help="Path to the grant pdf file")
    argparser.add_argument("k", type=int, help="# nearest neighbors to retrieve for similarity search")
    args = argparser.parse_args()

    print("Loading PDF...")
    pages = parse(args.filepath)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = InMemoryVectorStore.from_documents(pages, embeddings)

    llm_queries = {
        "general": (
            "What is the full name of the grant? List all projects or programs stated, including each project's name, start date, and end date."
        ),
        "spending": (
            "What is the total grant amount? Break down the spending into: fringe benefits, indirect costs, travel, equipment, and other. For “other,” provide a list of items with their names and cost. Return only valid JSON."
        ),
    }
    vec_queries = {
        "general": (
            "Information about the grant's official name, and the names, start and end dates of any funded projects or programs."
        ),
        "spending": (
            "Details about total funding, and how the grant money is allocated — including fringe benefits, indirect costs, travel, equipment, and other types of spending."
        ),
    }

    grant_json: dict[str, object] = {}

    # go through each batch of queries to efficiently/accurately get the proper data from pdf
    for query in llm_queries:
        print("Similar searching...")
        vec_question = vec_queries[query]
        print("Q: ", vec_question)
        context = sim_search(vec_question, args.k, vector_store)
        py_obj = determine_pyobj(query)
        print("Got context")

        print("Asking LLM...")
        llm_question = llm_queries[query]
        print("Q: ", llm_question)
        response = retrieve_data_from_llm(llm_question, context, py_obj)
        print("response: ", response)

        print("Updating grant json...")
        x = json.loads(json.dumps(grant_json))
        x.update(response)
        print(json.dumps(x))
        grant_json = x

    # write to json file
    obj = json.dumps(grant_json, indent=4)
    with open("grant.json", "w") as outfile:
        outfile.write(obj)


if __name__ == "__main__":
    main()
