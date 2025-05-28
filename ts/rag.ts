import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { z } from "zod";
import * as dotenv from "dotenv";

export async function simSearch(query: string, k: number, vectorStore: MemoryVectorStore): Promise<string> {
  const docs = await vectorStore.similaritySearch(query, k);
  let context = "";
  for (const doc of docs) {
    context += doc.pageContent;
  }
  return context;
}

export async function retrieveDataFromLlm(question: string, context: string, schema: ReturnType<typeof determineSchema>): Promise<any> {
  dotenv.config();
  const llm = new ChatOpenAI({
    modelName: process.env.MODEL,
    temperature: 0,
    openAIApiKey: process.env.OPENAI_KEY,
    configuration: { baseURL: process.env.OPENAI_BASE_URL }
  });

  const parser = StructuredOutputParser.fromZodSchema(schema);

  const prompt = new PromptTemplate({
    template: `You are a professional analyst specializing in grants and legal funding information. Your job is to extract structured information from legal documents.

Use the context provided to answer the question. Format your output as **valid JSON** matching the structure described below.

\u203c\ufe0f Important instructions:
- ONLY report the variables stated in the format and NOTHING MORE. Do NOT report any other variables!
- Do NOT include explanations, comments, or text before or after the JSON curly braces like \`json ... \`.
- Return a valid JSON object only. Make sure it can be parsed with JSON.parse().
- If a value is not found, use an empty string or an empty list.

Context:
{context}

Question:
{question}

Format:
{format_instructions}`,
    inputVariables: ["context", "question"],
    partialVariables: { format_instructions: parser.getFormatInstructions() },
  });

  const chain = prompt.pipe(llm).pipe(parser);
  const response = await chain.invoke({ context, question });
  return response;
}

export const projectSchema = z.object({
  name: z.string().describe("Name or title of the project or program"),
  start_date: z.string().describe("Start date of the project in MM/DD/YYYY or YYYY-MM-DD format"),
  end_date: z.string().describe("End date of the project in MM/DD/YYYY or YYYY-MM-DD format"),
});

export const generalGrantInfoSchema = z.object({
  grant_name: z.string().describe("The official name or title of the grant"),
  projects: z.array(projectSchema).describe("List of projects funded by this grant, each with a name, start date, and end date"),
});

export const otherSchema = z.object({
  obj: z.string().describe("A specific object or item receiving funding under 'other' spending"),
  cost: z.number().describe("Cost amount allocated to this object in USD"),
});

export const spendingInfoSchema = z.object({
  total: z.number().describe("Total amount of grant funding in USD"),
  fringe: z.number().describe("Amount for fringe benefits such as insurance, retirement, etc."),
  indirect: z.number().describe("Amount for indirect costs like rent, administrative overhead, and utilities"),
  travel: z.number().describe("Amount allocated to travel-related expenses"),
  equipment: z.number().describe("Amount allocated to equipment purchases"),
  other: z.array(otherSchema).describe("List of other individual items or objects that received funding, with their respective cost"),
});

export function determineSchema(key: string) {
  if (key === "general") {
    return generalGrantInfoSchema;
  }
  if (key === "spending") {
    return spendingInfoSchema;
  }
  return z.object({});
}
