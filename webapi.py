import requests
import re
from config import logger  # Add shared logger

class CricketAPI:
    BASE_URL = "https://api.cricapi.com/v1/"
    API_KEY = "1ca2fe5a-cb65-4ceb-ab4d-a4d85a4015cd"  # You may want to move this to .env

    def get_current_matches(self):
        url = f"{self.BASE_URL}currentMatches?apikey={self.API_KEY}&offset=0"
        return self._get_json(url)

    def get_ecricscore(self):
        url = f"{self.BASE_URL}cricscore?apikey={self.API_KEY}&offset=0"
        return self._get_json(url)

    def series_search(self, search_term):
        url = f"{self.BASE_URL}series_search?apikey={self.API_KEY}&search={search_term}"
        return self._get_json(url)

    def get_series_list(self):
        url = f"{self.BASE_URL}series?apikey={self.API_KEY}&offset=0"
        return self._get_json(url)

    def get_matches_list(self, series_id=None):
        if series_id:
            url = f"{self.BASE_URL}matches?apikey={self.API_KEY}&seriesId={series_id}"
        else:
            url = f"{self.BASE_URL}matches?apikey={self.API_KEY}&offset=0"
        return self._get_json(url)

    def get_players_list(self):
        url = f"{self.BASE_URL}players?apikey={self.API_KEY}&offset=0"
        return self._get_json(url)

    def players_search(self, search_term):
        url = f"{self.BASE_URL}players_search?apikey={self.API_KEY}&search={search_term}"
        return self._get_json(url)

    def get_series_info(self, series_id):
        url = f"{self.BASE_URL}series_info?apikey={self.API_KEY}&id={series_id}"
        return self._get_json(url)

    def get_match_info(self, match_id):
        url = f"{self.BASE_URL}match_info?apikey={self.API_KEY}&id={match_id}"
        return self._get_json(url)

    def get_player_info(self, player_id):
        url = f"{self.BASE_URL}player_info?apikey={self.API_KEY}&id={player_id}"
        return self._get_json(url)

    def get_fantasy_squad(self, match_id):
        url = f"{self.BASE_URL}fantasy_squad?apikey={self.API_KEY}&matchId={match_id}"
        return self._get_json(url)

    def get_series_squads(self, series_id):
        url = f"{self.BASE_URL}series_squads?apikey={self.API_KEY}&seriesId={series_id}"
        return self._get_json(url)

    def get_fantasy_scorecard(self, match_id):
        url = f"{self.BASE_URL}fantasy_scorecard?apikey={self.API_KEY}&matchId={match_id}"
        return self._get_json(url)

    def get_fantasy_match_points(self, match_id):
        url = f"{self.BASE_URL}fantasy_match_points?apikey={self.API_KEY}&matchId={match_id}"
        return self._get_json(url)

    def _get_json(self, url):
        try:
            logger.info(f"Calling API: {url.split('?')[0]}")
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Error calling API: {e}")
            return {"error": str(e)}

    def analyze_and_route(self, question):
        # Simple keyword-based routing. Expand with NLP for more accuracy.
        q = question.lower()
        # eCricScore
        if any(word in q for word in ["ecricscore", "ecscore", "cric score"]):
            return self.get_ecricscore()
        # Series Search
        m = re.search(r"series search (.+)", q)
        if m:
            return self.series_search(m.group(1).strip())
        # Series List
        if any(word in q for word in ["series list", "tournament list"]):
            return self.get_series_list()
        # Matches List
        m = re.search(r"matches list(?: for (\w+))?", q)
        if m:
            series_id = m.group(1)
            return self.get_matches_list(series_id) if series_id else self.get_matches_list()
        # Players List
        if any(word in q for word in ["player list", "players list"]):
            return self.get_players_list()
        # Players Search
        m = re.search(r"players search (.+)", q)
        if m:
            return self.players_search(m.group(1).strip())
        # Series Info
        m = re.search(r"series info (\w+)", q)
        if m:
            return self.get_series_info(m.group(1))
        # Match Info
        m = re.search(r"match info (\w+)", q)
        if m:
            return self.get_match_info(m.group(1))
        # Player Info
        m = re.search(r"player info (\w+)", q)
        if m:
            return self.get_player_info(m.group(1))
        # Fantasy Squad
        m = re.search(r"fantasy squad (\w+)", q)
        if m:
            return self.get_fantasy_squad(m.group(1))
        # Series Squads
        m = re.search(r"series squads (\w+)", q)
        if m:
            return self.get_series_squads(m.group(1))
        # Fantasy Scorecard
        m = re.search(r"fantasy scorecard (\w+)", q)
        if m:
            return self.get_fantasy_scorecard(m.group(1))
        # Fantasy Match Points
        m = re.search(r"fantasy match points (\w+)", q)
        if m:
            return self.get_fantasy_match_points(m.group(1))
        # Series Point Table
        m = re.search(r"series point table (\w+)", q)
        if m:
            return self.get_series_point_table(m.group(1))
        # Default fallback
        return None