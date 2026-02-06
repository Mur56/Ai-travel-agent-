import os
from utils.place_info_search import TavilyPlaceSearchTool, GeoapifyPlaceSearchTool
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv

class PlaceSearchTool:
    def __init__(self):
        load_dotenv()
        self.tavily_search = TavilyPlaceSearchTool()
        self.geoapify_search = GeoapifyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the place search tool"""
        @tool
        def search_attractions(place:str) -> str:
            """Search attractions of a place using Tavily"""
            try:
                attraction_result = self.tavily_search.tavily_search_attractions(place)
                return f"Attractions of {place}: {attraction_result}"
            except Exception as e:
                return f"Tavily cannot find the details due to {e}."
        
        @tool
        def search_restaurants(place:str) -> str:
            """Search restaurants of a place using Tavily"""
            try:
                restaurants_result = self.tavily_search.tavily_search_restaurants(place)
                return f"Restaurants of {place}: {restaurants_result}"
            except Exception as e:
                return f"Tavily cannot find the details due to {e}."
        
        @tool
        def search_activities(place:str) -> str:
            """Search activities of a place using Tavily"""
            try:
                activities_result = self.tavily_search.tavily_search_activity(place)
                return f"Activities in and around {place}: {activities_result}"
            except Exception as e:
                return f"Tavily cannot find the details due to {e}."
        
        @tool
        def search_transportation(place:str) -> str:
            """Search transportation of a place using Tavily"""
            try:
                transportation_result = self.tavily_search.tavily_search_transportation(place)
                return f"Modes of transportation in {place}: {transportation_result}"
            except Exception as e:
                return f"Tavily cannot find the details due to {e}."
        
        @tool
        def search_places_geoapify(query: str, lat: float, lon: float, radius: int = 5000, categories: str = "commercial.supermarket") -> str:
            """Search for places using Geoapify Places API. Provide query, latitude, longitude, radius (meters), and categories."""
            try:
                result = self.geoapify_search.geoapify_search_places(query, lat, lon, radius, categories)
                return str(result)
            except Exception as e:
                return f"Geoapify search failed: {e}"
        
        return [search_attractions, search_restaurants, search_activities, search_transportation, search_places_geoapify]