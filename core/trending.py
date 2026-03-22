"""Fetch trending topics from Google Trends via trendspy."""

from trendspy import Trends

_tr = None

_PERIOD_HOURS = {
    "today": 24,
    "week": 168,
    "month": 720,
    "year": 8760,
}

VALID_PERIODS = list(_PERIOD_HOURS.keys())

# Categories returned by Google Trends (used for the preset selector)
CATEGORIES = [
    "All",
    "Entertainment",
    "Sports",
    "Technology",
    "Business and Finance",
    "Science",
    "Health",
    "Politics",
    "Law and Government",
    "Climate",
    "Games",
    "Food and Drink",
    "Beauty and Fashion",
    "Hobbies and Leisure",
    "Travel and Transportation",
    "Autos and Vehicles",
    "Jobs and Education",
    "Pets and Animals",
    "Shopping",
]


def _client() -> Trends:
    global _tr
    if _tr is None:
        _tr = Trends()
    return _tr


def get_trending(
    period: str = "today",
    count: int = 5,
    geo: str = "US",
    category: str = "All",
) -> list[dict]:
    """Get top trending topics, optionally filtered by category.

    Args:
        period: One of "today", "week", "month", "year".
        count: Number of topics to return.
        geo: Country code (default "US").
        category: Category name to filter by, or "All" for everything.
                  Can also be a custom string to fuzzy-match against topic names.

    Returns list of dicts with keys: keyword, volume, categories.
    """
    if period not in _PERIOD_HOURS:
        raise ValueError(f"Invalid period '{period}'. Use one of: {VALID_PERIODS}")

    hours = _PERIOD_HOURS[period]
    results = _client().trending_now(geo=geo, hours=hours)

    # Filter by category if specified
    if category and category != "All":
        cat_lower = category.lower()
        results = [
            r for r in results
            if any(cat_lower in t.lower() for t in (r.topic_names or []))
        ]

    # Sort by search volume, highest first
    sorted_results = sorted(results, key=lambda r: r.volume or 0, reverse=True)

    topics = []
    for r in sorted_results[:count]:
        topics.append({
            "keyword": r.keyword,
            "volume": f"{r.volume:,}" if r.volume else "N/A",
            "categories": r.topic_names or [],
        })

    return topics
