from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://eclipserpg.com/legendary_areas?info_id=2"


def main():

    print("=" * 60)
    print("2 — SPECIAL POKÉMON CHECK")
    print("=" * 60)

    options = Options()
    options.add_experimental_option(
        "detach",
        True
    )

    driver = webdriver.Chrome(
        options=options
    )

    print()
    print("Opening 2...")

    try:
        driver.get(URL)

    except Exception as e:
        print(f"Page load warning: {e}")

    print()
    print("Current URL:")
    print(driver.current_url)

    print()
    print("Page title:")
    print(driver.title)

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    if "login" in driver.current_url.lower():

        print()
        print("=" * 60)
        print("LOGIN REQUIRED")
        print("=" * 60)
        print()
        print(
            "Log into Eclipse RPG in the Chrome window."
        )
        print(
            "Once you are completely logged in, "
            "return here and press ENTER."
        )

        input()

        print()
        print("Loading Kyogre's Temple again...")

        try:
            driver.get(URL)

        except Exception:
            pass

    # --------------------------------------------------------
    # Wait for page
    # --------------------------------------------------------

    try:

        WebDriverWait(
            driver,
            15
        ).until(
            lambda d:
            "Kyogre's Temple"
            in d.page_source
        )

    except Exception:

        print()
        print(
            "⚠ Timed out waiting for Kyogre's Temple."
        )

        print(
            "Checking the page anyway..."
        )

    print()
    print(
        f"Current URL: {driver.current_url}"
    )

    # --------------------------------------------------------
    # Save HTML for debugging
    # --------------------------------------------------------

    html = driver.page_source

    with open(
        "kyogre_debug.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print()
    print(
        f"✓ Saved HTML "
        f"({len(html):,} characters)"
    )

    # --------------------------------------------------------
    # Find "Special Pokémon" section
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("SEARCHING FOR SPECIAL POKÉMON")
    print("=" * 60)

    special_header = None

    try:

        elements = driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(.), "
            "'Special Pokémon')]"
        )

        for element in elements:

            text = element.text.strip()

            if text == "Special Pokémon":

                special_header = element
                break

    except Exception as e:

        print(
            f"⚠ Error locating section: {e}"
        )

    if special_header is None:

        print()
        print(
            "✗ Could not find the "
            "'Special Pokémon' section."
        )

        print()
        print(
            "The HTML has been saved to:"
        )

        print(
            "  kyogre_debug.html"
        )

        input(
            "\nPress Enter to close..."
        )

        return

    print()
    print(
        "✓ Special Pokémon section found."
    )

    # --------------------------------------------------------
    # Find the table containing Special Pokémon.
    #
    # The HTML we found looks like:
    #
    # <td class="tnav_information">
    #     Special Pokémon
    # </td>
    #
    # followed by a table containing the
    # Pokémon images.
    # --------------------------------------------------------

    special_table = None

    try:

        special_table = special_header.find_element(
            By.XPATH,
            "./ancestor::table[1]/following-sibling::table[1]"
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # Collect Pokémon from the special section.
    # --------------------------------------------------------

    pokemon = []

    if special_table is not None:

        try:

            images = special_table.find_elements(
                By.CSS_SELECTOR,
                "img"
            )

            for img in images:

                name = (
                    img.get_attribute("alt")
                    or ""
                ).strip()

                src = (
                    img.get_attribute("src")
                    or ""
                ).strip()

                if not name:
                    continue

                if name not in [
                    p["name"]
                    for p in pokemon
                ]:

                    pokemon.append(
                        {
                            "name": name,
                            "src": src
                        }
                    )

        except Exception as e:

            print(
                f"⚠ Error reading Pokémon: {e}"
            )

    # --------------------------------------------------------
    # Fallback:
    #
    # If the table relationship above doesn't work,
    # locate all images whose source is a Pokémon image
    # and use the surrounding HTML.
    # --------------------------------------------------------

    if not pokemon:

        print()
        print(
            "⚠ Primary parser found no Pokémon."
        )

        print(
            "Trying fallback parser..."
        )

        try:

            images = driver.find_elements(
                By.CSS_SELECTOR,
                "img[src*='/images/pokemon/']"
            )

            for img in images:

                name = (
                    img.get_attribute("alt")
                    or ""
                ).strip()

                src = (
                    img.get_attribute("src")
                    or ""
                ).strip()

                if not name:
                    continue

                # Only Pokémon appearing after the
                # Special Pokémon header are considered.
                try:

                    header_position = driver.execute_script(
                        """
                        const h = arguments[0];
                        const img = arguments[1];

                        return h.compareDocumentPosition(img);
                        """,
                        special_header,
                        img
                    )

                    # 4 = following
                    if not (
                        header_position
                        & 4
                    ):

                        continue

                except Exception:
                    pass

                if name not in [
                    p["name"]
                    for p in pokemon
                ]:

                    pokemon.append(
                        {
                            "name": name,
                            "src": src
                        }
                    )

        except Exception as e:

            print(
                f"⚠ Fallback parser error: {e}"
            )

    # --------------------------------------------------------
    # Display Pokémon
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RARE / SPECIAL POKÉMON FOUND")
    print("=" * 60)

    if not pokemon:

        print()
        print(
            "✗ No Special Pokémon were detected."
        )

        print()
        print(
            "Check kyogre_debug.html for the raw page."
        )

        input(
            "\nPress Enter to close..."
        )

        return

    for index, entry in enumerate(
        pokemon,
        1
    ):

        print()
        print(
            f"[{index}] ★ {entry['name']}"
        )

        print(
            f"    Image: {entry['src']}"
        )

    # --------------------------------------------------------
    # Current Chances
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("CURRENT CHANCES")
    print("=" * 60)

    chances = []

    try:

        chance_elements = driver.find_elements(
            By.XPATH,
            "//*[contains("
            "translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'current chances')]"
        )

        for element in chance_elements:

            text = element.text.strip()

            if "Current Chances" not in text:
                continue

            try:

                parent = element.find_element(
                    By.XPATH,
                    "./ancestor::tr[1]"
                )

                row_text = parent.text.strip()

                if row_text:

                    chances.append(
                        row_text
                    )

            except Exception:

                pass

    except Exception as e:

        print(
            f"⚠ Could not read chances: {e}"
        )

    print()

    if chances:

        for chance in chances:

            print(
                f"  {chance}"
            )

    else:

        print(
            "⚠ Current Chances could not be read."
        )

    # --------------------------------------------------------
    # Show useful raw HTML around Special Pokémon.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("SPECIAL POKÉMON HTML")
    print("=" * 60)

    try:

        html_section = driver.execute_script(
            """
            const header = arguments[0];

            const table =
                header.closest('table');

            if (!table) {
                return '';
            }

            let output = table.outerHTML;

            const next =
                table.nextElementSibling;

            if (next) {
                output += '\\n' + next.outerHTML;
            }

            return output;
            """,
            special_header
        )

        print(
            html_section[:10000]
        )

    except Exception as e:

        print(
            f"Could not extract section HTML: {e}"
        )

    print()
    print("=" * 60)
    print("CHECK COMPLETE")
    print("=" * 60)

    input(
        "\nPress Enter to close..."
    )


if __name__ == "__main__":
    main()