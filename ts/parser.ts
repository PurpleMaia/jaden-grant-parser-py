import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { Document } from "langchain/document";

export async function parse(files: string | string[]): Promise<Document[]> {
  const fileList = Array.isArray(files) ? files : [files];
  const allPages: Document[] = [];
  for (const file of fileList) {
    const loader = new PDFLoader(file);
    const pages = await loader.load();
    allPages.push(...pages);
  }
  return allPages;
}
