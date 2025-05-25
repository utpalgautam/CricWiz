from searching import search
import trafilatura
import requests
import os
from config import logger , GEMINI_MODEL

class websearch:
    def __init__(self):
        self.question = ""
        self.query_gen = """You are a specialized search query generator focused exclusively on the field of cricket. Your task is to produce a precise Google search query to retrieve accurate, authoritative, and up-to-date information about cricket in response to a user question. Only generate queries relevant to cricket, cricket players, matches, statistics, fantasy cricket, and related topics. Optimize the query for specificity and recency, ensuring it effectively filters out irrelevant results and targets high-quality cricket sources. Consider synonyms and contextual nuances within cricket to craft a balanced query that maximizes both precision and breadth. Your output must be exclusively the query string—no additional text or commentary.
            user question:{}
            output format:
            [query]
        """

        self.sel_url = """
            You are an expert research assistant specializing in cricket. You are given URLs, each with a title and description. Evaluate the titles and descriptions to select the URLs that are most relevant and authoritative for answering the user's cricket-related question. Only consider cricket-related content, such as player stats. Output only the final answer along with the two selected URLs, with no extra commentary.
            user question:{}
            urls and tiltle , description:
            {}
            output format:
            selected_url1
            selected_url2
            """

        self.answer_gen = """
            You are a sophisticated AI language model trained to generate detailed, accurate, and comprehensive answers to complex cricket questions. IMPORTANT: You must ONLY use the information provided in the context below. Do not use any external knowledge or information not present in the given context. If the context does not contain sufficient information to answer the question, explicitly state that the available information is insufficient.
            
            Given the context and the user question, craft a detailed, accurate, and comprehensive answer focused only on cricket using ONLY the data and information provided in the context. Your answer should be informative, well-structured, and tailored to the user's cricket-related question. Base your response strictly on the context provided - do not add any information from your training data or external knowledge.
            
            If the context lacks relevant information, respond with: "Based on the available information in the context, I cannot provide a complete answer to your question. The context does not contain sufficient details about [topic]."
            
            Your output must be exclusively the answer text based on the context—no additional text or commentary. Make sure the answer is precise and detailed using only the contextual information provided.
            
            user question:{}
            context:
            {}
            output format:
            [answer]
            """
        logger.info("Websearch instance created.")

    def call_gemini(self, prompt):
        GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return ""

    def get_result(self):
        self.question = self.question + " cricket"
        logger.info(f"Getting search results for question: {self.question}")
        try:
            p = search(self.question, sleep_interval=5, num_results=5, advanced=True, timeframe="1 year")
            data = []
            for i in p:
                tmp = {
                    "url": i.url,
                    "title": i.title,
                    "description": i.description
                }
                data.append(tmp)
            promp = self.sel_url.format(self.question, data)
            logger.info("Generated url:",promp)  # Log a snippet of the prompt
            urls_text = self.call_gemini(promp)
            # Split on newlines, flatten, and filter valid URLs
            urls = []
            for line in urls_text.split('\n'):
                for part in line.split():
                    part = part.strip()
                    if part.startswith("http"):
                        urls.append(part)
            logger.info(f"Selected URLs: {urls}")
            return urls
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def get_content(self):
        aggregated_content = []
        urls_to_process = self.get_result()

        if not urls_to_process:
            logger.info("No URLs found to process for content.")
            return ""

        for url in urls_to_process:
            try:
                logger.info(f"Attempting to get content from URL: {url}")
                # Use requests to fetch the page content for more reliability
                response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code == 200:
                    downloaded = response.text
                    result = trafilatura.extract(downloaded)
                    if result:
                        logger.info(f"Successfully extracted content from {url}.")
                        aggregated_content.append(result)
                        return aggregated_content
                    else:
                        logger.warning(f"Could not extract content from {url} (trafilatura returned None/empty).")
                else:
                    logger.warning(f"Failed to fetch content from {url} (status code: {response.status_code}).")
            except Exception as e:
                logger.error(f"Error processing URL {url} for content: {e}")
                # Continue to next URL even if one fails

        if not aggregated_content:
            logger.warning("No content could be aggregated from any of the URLs.")
            return ""

        return "\n\n---\n\n".join(aggregated_content) # Join content with a clear separator

    def get_answer(self, question):
        self.question = question
        try:
            context = self.get_content()
            logger.debug(f"Generated context for question '{self.question}': {context[:500]}...") # Log snippet of context
            promp = self.answer_gen.format(self.question, context)
            answer = self.call_gemini(promp)
            logger.info("Answer generated successfully.")
            return answer
        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            return "An error occurred while generating the answer."
    
    def get_prompt(self, question):
        self.question = question
        try:
            context = self.get_content()
            logger.info("Content extracted for prompt generation.")
            print("generated the prompt")
            return self.answer_gen.format(self.question, context)
        except Exception as e:
            logger.error(f"Error during prompt generation: {e}")
            return ""

if __name__ == "__main__":
    searcher = websearch()
    # question = input("Enter your question: ")
    question = "How does Fantasy League scoring work?"
    answer = searcher.get_answer(question)
    print(answer)