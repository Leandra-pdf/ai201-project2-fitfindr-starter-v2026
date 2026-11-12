
"""
Tests for FitFindr's listing search and weighted ranking.

These tests verify that title and style-tag matches contribute more
to a listing's relevance score than description matches.
"""

import unittest
from tools import _keywords, _listing_score
from unittest.mock import patch
import tools


class TestListingScore(unittest.TestCase):

    def test_title_match_gets_highest_weight(self):
        query = _keywords("graphic tee")

        listing = {
            "title": "Graphic Tee",
            "style_tags": [],
            "description": "",
        }

        self.assertEqual(_listing_score(query, listing), 6)

    def test_style_tag_match_gets_middle_weight(self):
        query = _keywords("graphic tee")

        listing = {
            "title": "",
            "style_tags": ["graphic tee"],
            "description": "",
        }

        self.assertEqual(_listing_score(query, listing), 4)

    def test_description_match_gets_lowest_weight(self):
        query = _keywords("graphic tee")

        listing = {
            "title": "",
            "style_tags": [],
            "description": "graphic tee",
        }

        self.assertEqual(_listing_score(query, listing), 2)

    def test_no_matches_returns_zero(self):
        query = _keywords("graphic tee")

        listing = {
            "title": "Blue Jeans",
            "style_tags": ["denim"],
            "description": "Vintage pants",
        }

        self.assertEqual(_listing_score(query, listing), 0)
        
    def test_search_returns_highest_scoring_listing_first(self):
        listings = [
            {
                "id": "description_match",
                "title": "Blue Shirt",
                "style_tags": [],
                "description": "graphic tee",
            },
            {
                "id": "style_match",
                "title": "Blue Shirt",
                "style_tags": ["graphic tee"],
                "description": "",
            },
            {
                "id": "title_match",
                "title": "Graphic Tee",
                "style_tags": [],
                "description": "",
            },
        ]

        with patch("tools.load_listings", return_value=listings):
            with patch("tools.config.SEARCH_RESULT_LIMIT", 10):
                results = tools.search_listings("graphic tee")

        result_ids = [listing["id"] for listing in results]

        self.assertEqual(
            result_ids,
            ["title_match", "style_match", "description_match"],
        )


if __name__ == "__main__":
    unittest.main()
