import os

BASE_URL = "https://eclipserpg.com"
LOGIN_URL = f"{BASE_URL}/login"
MINES_URL = f"{BASE_URL}/mines"

MAX_BATTLES = 100
WAIT_SHORT = 3
WAIT_MEDIUM = 8
WAIT_LONG = 20
BATTLE_END_TIMEOUT = 120

PAGE_LOAD_WAIT = (1.5, 2.5)
CLICK_WAIT = (0.5, 1.2)
SEARCH_DELAY = (1.5, 2.5)
BETWEEN_BATTLES_WAIT = (2.0, 3.0)

KEYRING_SERVICE = "EclipseRPGAutomation"
ACCOUNT_FILE = os.path.join(os.path.expanduser("~"), ".eclipse_rpg_accounts")

MAPS = [
    "Jirachi's Park", "Entei's Tower", "Kyogre's Temple", "Groudon's Palace",
    "Mesprit's Lake", "Mewtwo's Cavern", "Manaphy's Haven", "Eternal Garden",
    "Heatran's Mountain", "Spear Pillar", "Regigigas' Domain", "Deep Mewtwo's Cave",
    "Moon Gaze Mountain", "Icebound Cave", "Sky Pillar", "Mirage Ruins",
    "Latias Heaven", "Ruins of Alph",
]

RESTART_STATES = {"restart battle", "fight again", "battle again", "restart"}
ATTACK_STATES = {"attack", "fight"}
