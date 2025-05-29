'''
    main script that generates json of grant data
'''

from parser import parse
from rag import sim_search, determine_pyobj, retrieve_data_from_llm
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import argparse
import json
import os
import re


def main() -> None:
    argparser = argparse.ArgumentParser(description="Parse grant PDF files")
    argparser.add_argument(
        "files",
        nargs="*",
        help="Path(s) to one or more PDF files for the same grant",
    )
    argparser.add_argument(
        "-k",
        type=int,
        default=4,
        help="# nearest neighbors to retrieve for similarity search",
    )
    argparser.add_argument(
        "-f",
        "--folder",
        help="Folder to recursively search for PDF files",
    )
    args = argparser.parse_args()

    file_list = []
    if args.folder:
        if not os.path.isdir(args.folder):
            argparser.error(f"Folder '{args.folder}' does not exist")
        for root, _, files in os.walk(args.folder):
            for fname in files:
                if fname.lower().endswith(".pdf"):
                    file_list.append(os.path.join(root, fname))
    if not file_list and args.files:
        file_list = args.files
    if not file_list:
        argparser.error("Please specify a folder or one or more PDF files")

    print("Loading PDF(s)...")
    print(file_list)
    try:
        pages = parse(file_list)
    except Exception as e:
        joined = ", ".join(file_list)
        print(f"Failed to load PDF(s) '{joined}': {e}")
        return

    print("Starting embedding")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_store = InMemoryVectorStore.from_documents(pages, embeddings)

    llm_queries = {
        "general": (
            "What is the full name of the grant? List all projects or programs stated, including each project's name, start date, and end date."
        ),
        "spending": (
            "What is the total grant amount? Break down the spending into: salary, fringe/payroll benefits, indirect costs, travel, equipment, and other. For “other,” provide a list of items with their names and cost. Return only valid JSON."
        ),
    }
    vec_queries = {
        "general": (
            "Information about the grant's official name, and the names, start and end dates of any funded projects or programs."
        ),
        "spending": (
            "Details about total funding, and how the grant money is allocated — including salary, fringe/payroll benefits, indirect costs, travel, equipment, and other types of spending."
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
    model_name = os.getenv("MODEL", "model")
    if args.folder:
        base = os.path.basename(os.path.normpath(args.folder))
    else:
        # join pdf file names without extensions
        names = [os.path.splitext(os.path.basename(f))[0] for f in file_list]
        base = "_".join(names)
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base)
    filename = f"grant-{model_name}-{base}.json"
    with open(filename, "w") as outfile:
        outfile.write(obj)
    print("Finished writing to "+filename)


if __name__ == "__main__":
    main()
