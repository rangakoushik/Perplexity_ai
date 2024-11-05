import os
import json
from serpapi import GoogleSearch
import openai
from typing import Dict, List
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
SERPER_API_KEY = "f134d52118858e8204d03407b0af2f679c2c966f770469f735c1b76cfd35cdab"  # Replace with your actual API key
OPENAI_API_KEY = ""  # Replace with your actual API key

openai.api_key = OPENAI_API_KEY

class MiniPerplexity:
    def __init__(self):
        self.search_params = {
            "engine": "google",
            "api_key": SERPER_API_KEY,
            "num": 5 
        }

    def search_google(self, query: str) -> List[Dict]:
        """
        Perform a Google search and return relevant results
        """
        try:
            self.search_params["q"] = query
            search = GoogleSearch(self.search_params)
            results = search.get_dict()
            
            if "organic_results" not in results:
                return []
            
            formatted_results = []
            for result in results["organic_results"][:5]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", "")
                })
                
            return formatted_results
        except Exception as e:
            print(f"Error in Google Search: {str(e)}")
            return []

    def analyze_with_gpt(self, query: str, search_results: List[Dict]) -> str:
        """
        Analyze search results using GPT-3.5 to generate a comprehensive response
        """
        context = "\n\n".join([
            f"Title: {result['title']}\nSummary: {result['snippet']}\nSource: {result['link']}"
            for result in search_results
        ])
        prompt = f"""Based on the following search results about "{query}", provide a comprehensive, accurate, and well-structured response. 
        Include relevant information from multiple sources and cite them when appropriate.

        Search Results:
        {context}

        Please provide a detailed analysis and answer."""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that provides comprehensive answers based on search results. Always cite sources when possible."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                stream=True
            )
            full_response = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        print(content, end='', flush=True)
            
            return full_response

        except Exception as e:
            print(f"Error in GPT Analysis: {str(e)}")
            return "I apologize, but I encountered an error while analyzing the search results."

    def answer_query(self, query: str) -> None:
        """
        Main method to process a query and provide a response
        """
        print(f"\nSearching for information about: {query}")
        print("\nFetching search results...")
        search_results = self.search_google(query)
        
        if not search_results:
            print("No search results found. Please try a different query.")
            return

        print("\nAnalyzing results with GPT-3.5...")
        print("\nResponse:")
        print("-" * 80 + "\n")
        self.analyze_with_gpt(query, search_results)
        
        print("\n" + "-" * 80)

def main():
    perplexity = MiniPerplexity()
    
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        perplexity.answer_query(query)

if __name__ == "__main__":
    main()
