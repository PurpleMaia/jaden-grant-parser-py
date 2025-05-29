# import asyncio # async functionality in python (dynamic loading)
from typing import Iterable, List, Union
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def parse(files: Union[str, Iterable[str]]) -> List[Document]:
    """Load pages from one or more PDF files.

    Parameters
    ----------
    files
        A single file path or an iterable of file paths.

    Returns
    -------
    List[Document]
        All pages from the provided PDFs in the order they were loaded.
    """

    if isinstance(files, (str, bytes)):
        file_list = [files]
    else:
        file_list = list(files)

    pages = []
    for file in file_list:
        loader = PyPDFLoader(file)
        for page in loader.lazy_load():
            pages.append(page)

    return pages

if __name__=="__main__":
    import sys
    pages = parse(sys.argv[1:])
    if pages:
        print(f"{pages[0].metadata}\n")
        print(pages[0].page_content)
