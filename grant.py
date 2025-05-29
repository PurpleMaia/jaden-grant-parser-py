'''
    main script that generates json of grant data
'''

from api_app import process_grant
import argparse
import json
import os
import re
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
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
    argparser.add_argument(
        "-m",
        "--model",
        help="Chat completion model name (overrides MODEL env variable)",
    )
    args = argparser.parse_args()

    if args.model:
        os.environ["MODEL"] = args.model

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

    print("Processing grant...")
    try:
        grant_json = process_grant(file_list, k=args.k, model=args.model)
    except Exception as e:
        joined = ", ".join(file_list)
        print(f"Failed to process PDF(s) '{joined}': {e}")
        return

    obj = json.dumps(grant_json, indent=4)
    model_name = os.getenv("MODEL", "model")
    if args.folder:
        base = os.path.basename(os.path.normpath(args.folder))
    else:
        # join pdf file names without extensions
        names = [os.path.splitext(os.path.basename(f))[0] for f in file_list]
        base = "_".join(names)
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base)
    filename = f"grant-{base}-{model_name}.json"
    with open(filename, "w") as outfile:
        outfile.write(obj)
    print("Finished writing to "+filename)


if __name__ == "__main__":
    main()
