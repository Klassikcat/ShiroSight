import asyncio


class ShiroSightAnalyzer:
    def __init__(self, profile_name: str, openai_api_key: str):
        self.profile_name = profile_name