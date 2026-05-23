import re
from typing import Optional, List
from sqlalchemy.orm import Session
from loguru import logger

from app.models.campaign import Campaign


class CampaignMatcher:
    def match(self, comment_text: str, platform: str, db: Session) -> Optional[Campaign]:
        """
        Find the first active campaign matching the comment text.
        Returns the Campaign object or None.
        """
        campaigns: List[Campaign] = (
            db.query(Campaign)
            .filter(Campaign.platform == platform, Campaign.is_active == True)
            .all()
        )

        for campaign in campaigns:
            keyword_list = [k.strip() for k in campaign.keywords.split(",") if k.strip()]
            for keyword in keyword_list:
                if self._match_keyword(comment_text, keyword, campaign.match_type):
                    logger.info(f"Matched campaign '{campaign.name}' with keyword '{keyword}' (type={campaign.match_type})")
                    return campaign

        return None

    def _match_keyword(self, text: str, keyword: str, match_type: str) -> bool:
        if not keyword:
            return False

        if match_type == "exact":
            return text.strip().lower() == keyword.strip().lower()

        elif match_type == "regex":
            try:
                return bool(re.search(keyword, text, re.IGNORECASE))
            except re.error:
                logger.error(f"Invalid regex pattern: {keyword}")
                return False

        else:  # contains (default)
            return keyword.strip().lower() in text.lower()


campaign_matcher = CampaignMatcher()
