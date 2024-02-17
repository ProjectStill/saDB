from enum import Enum
from typing import List, Optional


class MobileType(Enum):
    UNKNOWN = 0
    PC_ONLY = 1
    MOBILE_ONLY = 2
    HYBRID = 3


class Pricing(Enum):
    UNKNOWN = 0
    FREE = 1
    FREE_WITH_ADS = 2
    FREE_WITH_IN_APP_PURCHASES = 3
    FREEMIUM = 4
    ONE_TIME = 5
    SUBSCRIPTION = 6
    EXTERNAL_SUBSCRIPTION = 7


class StillRating(Enum):
    UNKNOWN = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    FIVE_PLUS = 6


# To Comma Seperated List
def to_csl(csl: Optional[str]):
    if csl is None:
        return csl
    return csl.split(",")


# From Comma Seperated List
def from_csl(csl: Optional[List[str]]):
    if csl is None:
        return csl
    return ",".join(csl)


class App:
    keywords: List[str] = []
    mimetypes: List[str] = []
    app_license: str = "Proprietary"
    pricing: Pricing = Pricing.UNKNOWN
    mobile: MobileType = MobileType.UNKNOWN
    still_rating: StillRating = StillRating.UNKNOWN
    still_rating_notes: str = ""
    homepage: str = ""
    donate_url: str = ""
    screenshot_urls: List[str] = []
    demo_urls: List[str] = []
    addons: List[str] = []

    def __init__(
        self, app_id: str, name: str, primary_src: str, src_pkg_name: str,
        icon_url: str, author: str, summary: str, description: str,
        categories: List[str], keywords: Optional[List[str]],
        mimetypes: Optional[List[str]], app_license: Optional[str], pricing: Optional[str],
        mobile: Optional[str], still_rating: Optional[str], still_rating_notes: Optional[str],
        homepage: Optional[str], donate_url: Optional[str], screenshot_urls: Optional[List[str]],
        demo_url: Optional[str], addons: Optional[List[str]]
    ):
        self.app_id = app_id
        self.name = name
        self.primary_src = primary_src
        self.src_pkg_name = src_pkg_name
        self.icon_url = icon_url
        self.author = author
        self.summary = summary
        self.description = description
        self.categories = categories

        if keywords is not None:
            self.keywords = keywords

        if mimetypes is not None:
            self.mimetypes = mimetypes

        if app_license is not None:
            self.app_license = app_license

        if pricing is not None:
            self.pricing = Pricing[pricing]
        
        if mobile is not None:
            self.mobile = MobileType[mobile]
        
        if still_rating is not None:
            self.still_rating = StillRating[still_rating]

        if still_rating_notes is not None:
            self.still_rating_notes = still_rating_notes

        if homepage is not None:
            self.homepage = homepage

        if donate_url is not None:
            self.donate_url = donate_url

        if screenshot_urls is not None:
            self.screenshot_urls = screenshot_urls

        if demo_url is not None:
            self.demo_url = demo_url

        if addons is not None:
            self.addons = addons

