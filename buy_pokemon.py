"""
buy_pokemon.py

Eclipse RPG - Buy Pokémon support.

Handles:
    - Pokémon name filtering
    - Pokémon type/variant filtering
    - Result parsing
    - Price parsing
    - Dynamic Buy button IDs
    - Pagination
    - Purchase requests

This module is intentionally separate from capture.py/search.py so
the battle/capture loop is not affected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from typing import Optional
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://eclipserpg.com"
BUY_POKEMON_URL = f"{BASE_URL}/buy_pokemon"


POKEMON_TYPES = (
    "Normal",
    "Shiny",
    "Dark",
    "Silver",
    "Golden",
    "Crystal",
    "Ruby",
    "Sapphire",
    "Emerald",
    "Shadow",
    "Light",
    "Legacy",
    "Pearl",
    "Astral",
    "Rainbow",
)


@dataclass
class PokemonListing:
    """
    One Pokémon listing returned by /buy_pokemon.
    """

    pokemon_name: str
    pokemon_type: str
    price: Optional[int]
    price_text: str
    buy_id: Optional[int]
    status_id: Optional[int]
    details: str = ""
    raw_html: str = ""

    @property
    def can_buy(self) -> bool:
        return self.buy_id is not None


class PokemonShop:
    def __init__(
        self,
        session: requests.Session,
        base_url: str = BASE_URL,
    ):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/buy_pokemon"

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        pokemon_name: str = "",
        pokemon_type: str = "",
        page: int = 1,
    ) -> list[PokemonListing]:
        """
        Search the Pokémon marketplace.

        The actual site uses:
            BP_PokemonName
            BP_PokemonType

        Pagination uses:
            ?page=3
        """

        params = {}

        if pokemon_name:
            params["BP_PokemonName"] = pokemon_name

        if pokemon_type:
            if pokemon_type not in POKEMON_TYPES:
                raise ValueError(
                    f"Invalid Pokémon type: {pokemon_type}"
                )

            params["BP_PokemonType"] = pokemon_type

        if page > 1:
            params["page"] = page

        response = self.session.get(
            self.url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return self.parse_results(response.text)

    # ---------------------------------------------------------
    # PARSER
    # ---------------------------------------------------------

    def parse_results(self, html: str) -> list[PokemonListing]:
        """
        Parse the Pokémon marketplace HTML.

        Expected table headings include:

            Pokemon Details
            Price
            Buy
        """

        soup = BeautifulSoup(html, "html.parser")

        listings: list[PokemonListing] = []

        # Buy buttons identify the individual listing.
        buy_buttons = soup.select(
            'button[id^="BP_Buy"]'
        )

        for button in buy_buttons:
            button_id = button.get("id", "")

            match = re.match(
                r"BP_Buy(\d+)",
                button_id,
            )

            if not match:
                continue

            buy_id = int(match.group(1))

            # Find the containing table row.
            row = button.find_parent("tr")

            if row is None:
                continue

            raw_html = str(row)

            # -------------------------------------------------
            # STATUS ID
            # -------------------------------------------------

            status_id = None

            status = row.select_one(
                f'[id="BP_Status{buy_id}"]'
            )

            if status:
                status_id = buy_id

            # -------------------------------------------------
            # POKÉMON DETAILS
            # -------------------------------------------------

            pokemon_name = ""
            pokemon_type = ""
            details = ""

            # Look for the details column.
            cells = row.find_all("td")

            if len(cells) >= 3:

                # Usually the Pokémon information is the
                # second table cell.
                details_cell = cells[1]

                details = details_cell.get_text(
                    " ",
                    strip=True,
                )

                # Prefer the span containing the Pokémon name.
                name_span = details_cell.select_one(
                    '[id^="BP_Pokemon"]'
                )

                if name_span:
                    pokemon_name = name_span.get_text(
                        " ",
                        strip=True,
                    )

                if not pokemon_name:
                    # Fall back to the first bold element.
                    bold = details_cell.find("b")

                    if bold:
                        pokemon_name = bold.get_text(
                            " ",
                            strip=True,
                        )

                # Attempt to determine variant/type from
                # visible text.
                pokemon_type = self.detect_type(
                    pokemon_name,
                    details,
                )

            # -------------------------------------------------
            # PRICE
            # -------------------------------------------------

            price = None
            price_text = ""

            if len(cells) >= 3:
                # Price is normally the third cell.
                price_cell = cells[2]

                price_text = price_cell.get_text(
                    " ",
                    strip=True,
                )

                price = self.extract_price(
                    price_text
                )

            listings.append(
                PokemonListing(
                    pokemon_name=pokemon_name,
                    pokemon_type=pokemon_type,
                    price=price,
                    price_text=price_text,
                    buy_id=buy_id,
                    status_id=status_id,
                    details=details,
                    raw_html=raw_html,
                )
            )

        return listings

    # ---------------------------------------------------------
    # PRICE
    # ---------------------------------------------------------

    @staticmethod
    def extract_price(text: str) -> Optional[int]:
        """
        Extract numeric price.

        Examples:

            "$200"
            "$1,200"
            "$5,000,000"
            "$100,000,000"
        """

        if not text:
            return None

        match = re.search(
            r"\$?\s*([\d,]+)",
            text,
        )

        if not match:
            return None

        try:
            return int(
                match.group(1).replace(",", "")
            )
        except ValueError:
            return None

    # ---------------------------------------------------------
    # TYPE DETECTION
    # ---------------------------------------------------------

    @staticmethod
    def detect_type(
        pokemon_name: str,
        details: str,
    ) -> str:
        """
        Attempt to determine the Pokémon variant.

        The site exposes the variant through the selected
        Pokémon and/or its displayed name.

        This is intentionally conservative.
        """

        text = f"{pokemon_name} {details}".lower()

        # Check longest/specific variant names first.
        for pokemon_type in sorted(
            POKEMON_TYPES,
            key=len,
            reverse=True,
        ):
            if pokemon_type.lower() in text:
                return pokemon_type

        return ""

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def get_page_count(self, html: str) -> int:
        """
        Determine the highest visible page number.
        """

        soup = BeautifulSoup(html, "html.parser")

        pages = []

        for link in soup.select(
            "a.page-number-link"
        ):
            href = link.get("href", "")

            match = re.search(
                r"[?&]page=(\d+)",
                href,
            )

            if match:
                pages.append(
                    int(match.group(1))
                )

        return max(pages, default=1)

    # ---------------------------------------------------------
    # PURCHASE
    # ---------------------------------------------------------

    def buy(
        self,
        listing: PokemonListing,
    ) -> requests.Response:
        """
        Purchase a Pokémon using its dynamic listing ID.

        IMPORTANT:
        The ID comes from the page:

            BP_Buy33827978

        We therefore never hard-code it.
        """

        if listing.buy_id is None:
            raise ValueError(
                "This Pokémon listing does not have "
                "a valid Buy ID."
            )

        return self._purchase_by_id(
            listing.buy_id
        )

    def _purchase_by_id(
        self,
        buy_id: int,
    ) -> requests.Response:
        """
        Perform the purchase request.

        The exact POST/AJAX endpoint and payload should
        be matched to the site's JavaScript handler once
        the buy_pokemon page's JS is available.

        For safety, this currently raises rather than
        guessing the site's purchase endpoint.
        """

        raise NotImplementedError(
            "The Buy button's JavaScript request still "
            "needs to be captured from buy_pokemon. "
            "Do not guess the purchase endpoint."
        )


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def format_listing(
    listing: PokemonListing,
) -> str:
    """
    Format one listing for the menu.
    """

    name = (
        listing.pokemon_name
        or "Unknown Pokémon"
    )

    variant = (
        f" [{listing.pokemon_type}]"
        if listing.pokemon_type
        else ""
    )

    if listing.price is not None:
        price = f"${listing.price:,}"
    else:
        price = listing.price_text or "Unknown"

    buy_id = (
        str(listing.buy_id)
        if listing.buy_id is not None
        else "N/A"
    )

    return (
        f"{name}{variant} | "
        f"{price} | "
        f"Buy ID: {buy_id}"
    )


def search_pokemon(
    session: requests.Session,
    pokemon_name: str = "",
    pokemon_type: str = "",
    page: int = 1,
) -> list[PokemonListing]:
    """
    Convenience wrapper.
    """

    shop = PokemonShop(session)

    return shop.search(
        pokemon_name=pokemon_name,
        pokemon_type=pokemon_type,
        page=page,
    )
