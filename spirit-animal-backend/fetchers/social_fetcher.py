"""
Social media data fetchers for Spirit Animal app.

Each fetcher retrieves public data from a social platform.
For production, you'll need to set up API keys for each platform.
"""

import os
from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class SocialData:
    """Container for social media data from a platform."""
    platform: str
    bio: str
    posts: list[str]


async def fetch_twitter(handle: str) -> Optional[SocialData]:
    """
    Fetch public tweets from Twitter/X.

    Requires TWITTER_BEARER_TOKEN environment variable.
    Get one at https://developer.twitter.com/
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("Warning: TWITTER_BEARER_TOKEN not set, skipping Twitter")
        return None

    # Clean handle
    handle = handle.lstrip("@").strip()

    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {bearer_token}"}

            # Get user info
            user_resp = await client.get(
                f"https://api.twitter.com/2/users/by/username/{handle}",
                headers=headers,
                params={"user.fields": "description"}
            )
            user_data = user_resp.json().get("data", {})

            if not user_data:
                return None

            user_id = user_data.get("id")
            bio = user_data.get("description", "")

            # Get recent tweets
            tweets_resp = await client.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                headers=headers,
                params={"max_results": 20, "tweet.fields": "text"}
            )
            posts = [t["text"] for t in tweets_resp.json().get("data", [])]

            return SocialData(platform="twitter", bio=bio, posts=posts)
    except Exception as e:
        print(f"Twitter fetch error: {e}")
        return None


async def fetch_reddit(username: str) -> Optional[SocialData]:
    """
    Fetch public Reddit comments and posts.

    Reddit's public JSON API doesn't require authentication for public data.
    """
    # Clean username
    username = username.replace("u/", "").replace("/u/", "").strip()

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://www.reddit.com/user/{username}.json",
                headers={"User-Agent": "SpiritAnimalApp/1.0"},
                follow_redirects=True
            )

            if resp.status_code != 200:
                return None

            data = resp.json().get("data", {}).get("children", [])

            posts = []
            for item in data[:20]:
                item_data = item.get("data", {})
                # Get comment body or post title+selftext
                if item_data.get("body"):
                    posts.append(item_data["body"])
                elif item_data.get("title"):
                    text = item_data["title"]
                    if item_data.get("selftext"):
                        text += "\n" + item_data["selftext"]
                    posts.append(text)

            return SocialData(platform="reddit", bio="", posts=posts)
    except Exception as e:
        print(f"Reddit fetch error: {e}")
        return None


async def fetch_bluesky(handle: str) -> Optional[SocialData]:
    """
    Fetch public Bluesky posts.

    Uses the public Bluesky API (no auth required for public profiles).
    """
    # Clean handle
    handle = handle.lstrip("@").strip()
    if not handle.endswith(".bsky.social") and "." not in handle:
        handle = f"{handle}.bsky.social"

    try:
        async with httpx.AsyncClient() as client:
            # Get profile
            profile_resp = await client.get(
                f"https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile",
                params={"actor": handle}
            )

            if profile_resp.status_code != 200:
                return None

            profile = profile_resp.json()
            bio = profile.get("description", "")

            # Get posts
            feed_resp = await client.get(
                f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed",
                params={"actor": handle, "limit": 20}
            )

            posts = []
            if feed_resp.status_code == 200:
                feed_data = feed_resp.json().get("feed", [])
                for item in feed_data:
                    post_record = item.get("post", {}).get("record", {})
                    if post_record.get("text"):
                        posts.append(post_record["text"])

            return SocialData(platform="bluesky", bio=bio, posts=posts)
    except Exception as e:
        print(f"Bluesky fetch error: {e}")
        return None


async def fetch_linkedin(profile_url: str) -> Optional[SocialData]:
    """
    LinkedIn doesn't allow public API access without OAuth.

    For a PoC, you could:
    1. Ask user to paste their LinkedIn summary manually
    2. Use a service like Proxycurl (paid)
    3. Skip LinkedIn for now
    """
    # Placeholder - LinkedIn requires OAuth or paid APIs
    print("LinkedIn fetching not implemented (requires OAuth)")
    return None


async def fetch_instagram(handle: str) -> Optional[SocialData]:
    """
    Instagram requires Facebook Graph API access.

    For a PoC, you could:
    1. Ask user to paste their bio manually
    2. Use Instagram Basic Display API with user auth
    """
    # Placeholder - Instagram requires OAuth
    print("Instagram fetching not implemented (requires OAuth)")
    return None


async def fetch_tiktok(handle: str) -> Optional[SocialData]:
    """
    TikTok requires official API access.

    For PoC, would need TikTok for Developers access.
    """
    # Placeholder
    print("TikTok fetching not implemented (requires API access)")
    return None


# Map platform names to fetcher functions
FETCHERS = {
    "twitter": fetch_twitter,
    "reddit": fetch_reddit,
    "bluesky": fetch_bluesky,
    "linkedin": fetch_linkedin,
    "instagram": fetch_instagram,
    "tiktok": fetch_tiktok,
}


async def fetch_all(handles: list[dict]) -> list[SocialData]:
    """
    Fetch data from all provided social platforms in parallel.

    Args:
        handles: List of dicts with 'platform' and 'handle' keys

    Returns:
        List of SocialData objects (only successful fetches)
    """
    import asyncio

    tasks = []
    for h in handles:
        platform = h.get("platform", "").lower()
        handle = h.get("handle", "").strip()

        if not handle:
            continue

        fetcher = FETCHERS.get(platform)
        if fetcher:
            tasks.append(fetcher(handle))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failures and exceptions
    return [r for r in results if isinstance(r, SocialData)]
