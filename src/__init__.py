from enum import Enum
from typing import List, Optional


class MobileType(Enum):
    """
    Enum representing the type of mobile support for an app.

    Attributes:
        UNKNOWN (int): Unknown mobile support.
        PC_ONLY (int): App supports only PC.
        MOBILE_ONLY (int): App supports only mobile.
        HYBRID (int): App supports both PC and mobile.
    """
    UNKNOWN = 0
    PC_ONLY = 1
    MOBILE_ONLY = 2
    HYBRID = 3


class Pricing(Enum):
    """
    Enum representing the pricing model of an app.

    Attributes:
        UNKNOWN (int): Unknown pricing model.
        FREE (int): App is free.
        FREE_WITH_ADS (int): App is free with ads.
        FREE_WITH_IN_APP_PURCHASES (int): App is free with in-app purchases.
        FREEMIUM (int): App is freemium.
        ONE_TIME (int): App has a one-time purchase cost.
        SUBSCRIPTION (int): App has a subscription cost.
        EXTERNAL_SUBSCRIPTION (int): App has an external subscription cost.
    """
    UNKNOWN = 0
    FREE = 1
    FREE_WITH_ADS = 2
    FREE_WITH_IN_APP_PURCHASES = 3
    FREEMIUM = 4
    ONE_TIME = 5
    SUBSCRIPTION = 6
    EXTERNAL_SUBSCRIPTION = 7


class StillRating(Enum):
    """
    Enum representing the still rating of an app.

    Attributes:
        UNKNOWN (int): Unknown still rating.
        ONE (int): Still rating of 1.
        TWO (int): Still rating of 2.
        THREE (int): Still rating of 3.
        FOUR (int): Still rating of 4.
        FIVE (int): Still rating of 5.
        FIVE_PLUS (int): Still rating of 5+.
    """
    UNKNOWN = 0
    CAUTION = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    GOLD_PLUS = 5


def from_csl(csl: Optional[str]):
    """
    Converts a comma-separated string to a list.

    Parameters:
        csl (str): The comma-separated string.

    Returns:
        list: The list of strings.
    """
    if csl is None:
        return csl
    return csl.split(",")


def to_csl(csl: Optional[List[str]]):
    """
    Converts a list to a comma-separated string.

    Parameters:
        csl (list): The list of strings.

    Returns:
        str: The comma-separated string.
    """
    if csl is None:
        return csl
    return ",".join(csl)


class App:
    """
    A class used to represent an App.

    ...

    Attributes
    ----------
    app_id : str
        the id of the app
    name : str
        the name of the app
    primary_src : str
        the primary source of the app
    src_pkg_name : str
        the source package name of the app
    icon_url : str
        the icon url of the app
    author : str
        the author of the app
    summary : str
        the summary of the app
    description : str
        the description of the app
    categories : list
        the categories of the app
    keywords : list
        the keywords of the app
    mimetypes : list
        the mimetypes of the app
    app_license : str
        the license of the app
    pricing : Pricing
        the pricing of the app
    mobile : MobileType
        the mobile type of the app
    still_rating : StillRating
        the still rating of the app
    still_rating_notes : str
        the still rating notes of the app
    homepage : str
        the homepage of the app
    donate_url : str
        the donate url of the app
    screenshot_urls : list
        the screenshot urls of the app
    demo_url : str
        the demo url of the app
    addons : list
        the addons of the app
    """
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
    demo_url: str = ""
    addons: List[str] = []

    def __init__(
            self, app_id: str, name: str, primary_src: str, src_pkg_name: str,
            icon_url: str, author: str, summary: str, description: str,
            categories: List[str], keywords: Optional[List[str]],
            mimetypes: Optional[List[str]], app_license: Optional[str], pricing: Optional[Pricing],
            mobile: Optional[MobileType], still_rating: Optional[StillRating], still_rating_notes: Optional[str],
            homepage: Optional[str], donate_url: Optional[str], screenshot_urls: Optional[List[str]],
            demo_url: Optional[str], addons: Optional[List[str]]
    ):
        """
        Constructs a new App instance.

        Parameters:
            app_id (str): The id of the app.
            name (str): The name of the app.
            primary_src (str): The primary source of the app.
            src_pkg_name (str): The source package name of the app.
            icon_url (str): The icon url of the app.
            author (str): The author of the app.
            summary (str): The summary of the app.
            description (str): The description of the app.
            categories (list): The categories of the app.
            keywords (list, optional): The keywords of the app.
            mimetypes (list, optional): The mimetypes of the app.
            app_license (str, optional): The license of the app.
            pricing (Pricing, optional): The pricing of the app.
            mobile (MobileType, optional): The mobile type of the app.
            still_rating (StillRating, optional): The still rating of the app.
            still_rating_notes (str, optional): The still rating notes of the app.
            homepage (str, optional): The homepage of the app.
            donate_url (str, optional): The donate url of the app.
            screenshot_urls (list, optional): The screenshot urls of the app.
            demo_url (str, optional): The demo url of the app.
            addons (list, optional): The addons of the app.
        """
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
            self.pricing = pricing

        if mobile is not None:
            self.mobile = mobile

        if still_rating is not None:
            self.still_rating = still_rating

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


class InstalledApp(App):
    update_available: bool = False

    def __init__(
        self, update_available: bool,
        app_id: str, name: str, primary_src: str, src_pkg_name: str,
        icon_url: str, author: str, summary: str, description: str,
        categories: List[str], keywords: Optional[List[str]],
        mimetypes: Optional[List[str]], app_license: Optional[str], pricing: Optional[Pricing],
        mobile: Optional[MobileType], still_rating: Optional[StillRating], still_rating_notes: Optional[str],
        homepage: Optional[str], donate_url: Optional[str], screenshot_urls: Optional[List[str]],
        demo_url: Optional[str], addons: Optional[List[str]]
    ):
        super().__init__(
            app_id, name, primary_src, src_pkg_name, icon_url, author, summary, description, categories, keywords,
            mimetypes, app_license, pricing, mobile, still_rating, still_rating_notes, homepage, donate_url,
            screenshot_urls, demo_url, addons
        )
        self.update_available = update_available

    @classmethod
    def from_app(cls, app: App):
        return cls(
            False, app.app_id, app.name, app.primary_src, app.src_pkg_name, app.icon_url, app.author,
            app.summary, app.description, app.categories, app.keywords, app.mimetypes, app.app_license,
            app.pricing, app.mobile, app.still_rating, app.still_rating_notes, app.homepage, app.donate_url,
            app.screenshot_urls, app.demo_url, app.addons
        )

    # app_id: str, name: str, primary_src: str, src_pkg_name: str,
    #             icon_url: str, author: str, summary: str, description: str,
    #             categories: List[str], keywords: Optional[List[str]],
    #             mimetypes: Optional[List[str]], app_license: Optional[str], pricing: Optional[Pricing],
    #             mobile: Optional[MobileType], still_rating: Optional[StillRating], still_rating_notes: Optional[str],
    #             homepage: Optional[str], donate_url: Optional[str], screenshot_urls: Optional[List[str]],
    #             demo_url: Optional[str], addons: Optional[List[str]]
