import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { Document } from "langchain/document";

export async function parse(file: string): Promise<Document[]> {
  const loader = new PDFLoader(file);
  const pages = await loader.load();
  return pages;
}
