import os
import json
from langchain_tavily import TavilySearch
from langchain_google_community import GooglePlacesTool, GooglePlacesAPIWrapper 
import requests

# --- BEGIN COMMENTED BLOCK ---
# GooglePlaceSearchTool provides methods to search for places using the Google Places API via LangChain wrappers.
# class GooglePlaceSearchTool:
#     def __init__(self, api_key: str):
#         # Initialize the GooglePlacesAPIWrapper with the provided API key
#         self.places_wrapper = GooglePlacesAPIWrapper(gplaces_api_key=api_key)
#         # Create a GooglePlacesTool instance using the API wrapper
#         self.places_tool = GooglePlacesTool(api_wrapper=self.places_wrapper)
#     
#     def google_search_attractions(self, place: str) -> dict:
#         """
#         Searches for attractions in the specified place using GooglePlaces API.
#         Args:
#             place (str): The name of the place to search attractions for.
#         Returns:
#             dict: The API response containing attractions data.
#         """
#         # Run a query for top attractions in the given place
#         return self.places_tool.run(f"top attractive places in and around {place}")
#     
#     def google_search_restaurants(self, place: str) -> dict:
#         """
#         Searches for available restaurants in the specified place using GooglePlaces API.
#         Args:
#             place (str): The name of the place to search restaurants for.
#         Returns:
#             dict: The API response containing restaurant data.
#         """
#         # Run a query for top restaurants in the given place
#         return self.places_tool.run(f"what are the top 10 restaurants and eateries in and around {place}?")
#     
#     def google_search_activity(self, place: str) -> dict:
#         """
#         Searches for popular activities in the specified place using GooglePlaces API.
#         Args:
#             place (str): The name of the place to search activities for.
#         Returns:
#             dict: The API response containing activities data.
#         """
#         # Run a query for activities in the given place
#         return self.places_tool.run(f"Activities in and around {place}")
#
#     def google_search_transportation(self, place: str) -> dict:
#         """
#         Searches for available modes of transportation in the specified place using GooglePlaces API.
#         Args:
#             place (str): The name of the place to search transportation options for.
#         Returns:
#             dict: The API response containing transportation data.
#         """
#         # Run a query for transportation options in the given place
#         return self.places_tool.run(f"What are the different modes of transportations available in {place}") ##
# --- END COMMENTED BLOCK ---

class TavilyPlaceSearchTool:
    def __init__(self):
        pass

    def tavily_search_attractions(self, place: str) -> dict:
        """
        Searches for attractions in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"top attractive places in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result
    
    def tavily_search_restaurants(self, place: str) -> dict:
        """
        Searches for available restaurants in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"what are the top 10 restaurants and eateries in and around {place}."})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result
    
    def tavily_search_activity(self, place: str) -> dict:
        """
        Searches for popular activities in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"activities in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_transportation(self, place: str) -> dict:
        """
        Searches for available modes of transportation in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"What are the different modes of transportations available in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

class GeoapifyPlaceSearchTool:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEOAPIFY_API_KEY")
        if not self.api_key:
            raise ValueError("Geoapify API key must be provided via argument or GEOAPIFY_API_KEY env variable.")

    def geoapify_search_places(self, query: str, lat: float, lon: float, radius: int = 5000, categories: str = "commercial.supermarket") -> dict:
        """
        Search for places using the Geoapify Places API.
        Args:
            query (str): Free text search query (e.g., 'supermarket').
            lat (float): Latitude of the center point.
            lon (float): Longitude of the center point.
            radius (int): Search radius in meters.
            categories (str): Geoapify categories (default: 'commercial.supermarket').
        Returns:
            dict: JSON response from Geoapify API.
        """
        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": categories,
            "filter": f"circle:{lon},{lat},{radius}",
            "text": query,
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()