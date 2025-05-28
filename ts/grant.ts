import { parse } from "./parser";
import { simSearch, retrieveDataFromLlm, determineSchema } from "./rag";
import { OllamaEmbeddings } from "@langchain/community/embeddings/ollama";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import * as fs from "fs";

const args = process.argv.slice(2);
if (args.length < 2) {
  console.log("Usage: ts-node grant.ts <path to pdf> <k-value>");
  process.exit(1);
}

const filepath = args[0];
const k = parseInt(args[1], 10);

(async () => {
  console.log("Loading PDF...");
  const pages = await parse(filepath);

  const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
  const vectorStore = await MemoryVectorStore.fromDocuments(pages, embeddings);

  const llmQueries: Record<string, string> = {
    general: "What is the full name of the grant? List all projects or programs stated, including each project's name, start date, and end date.",
    spending: "What is the total grant amount? Break down the spending into: fringe benefits, indirect costs, travel, equipment, and other. For \u201cother,\u201d provide a list of items with their names and cost. Return only valid JSON."
  };

  const vecQueries: Record<string, string> = {
    general: "Information about the grant's official name, and the names, start and end dates of any funded projects or programs.",
    spending: "Details about total funding, and how the grant money is allocated \u2014 including fringe benefits, indirect costs, travel, equipment, and other types of spending."
  };

  let grant: any = {};

  for (const key of Object.keys(llmQueries)) {
    console.log("Similar searching...");
    const vecQuestion = vecQueries[key];
    console.log("Q:", vecQuestion);
    const context = await simSearch(vecQuestion, k, vectorStore);
    const schema = determineSchema(key);
    console.log("Got context");

    console.log("Asking LLM...");
    const llmQuestion = llmQueries[key];
    console.log("Q:", llmQuestion);
    const response = await retrieveDataFromLlm(llmQuestion, context, schema);
    console.log("response:", response);

    console.log("Updating grant json...");
    grant = { ...grant, ...response };
    console.log(JSON.stringify(grant));
  }

  await fs.promises.writeFile("grant.json", JSON.stringify(grant, null, 4));
})();
