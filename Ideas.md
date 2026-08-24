RPG Bot Ideas

A running list of features, improvements, and automation ideas for the Eclipse RPG automation bot.

---

🎯 Training

- [ ] Battle until X level
  
  - Let the user enter a target level.
  - Automatically continue battling until the selected Pokémon reaches that level.
  - Display current level and target level while running.
  - Stop automatically when the target is reached.
  - Optional maximum-battle safety limit.
  - Return to the Training menu when complete.
  - Changes the fight difficulty to help ensure it gets as close to that level as possible.

<table cellpadding="3" cellspacing="2" width="100%">
  <tbody>
    <tr>
      <td class="tnav_battle_information" align="center" width="100%">
        Battle Difficulty
      </td>
    </tr>
    <tr>
      <td class="tnav_battle" align="center" width="100%" style="padding-top: 1px; padding-bottom: 1px;">
        Higher battle difficulty makes battles harder but increases EXP and Platinum Coins earned.
      </td>
    </tr>
    <tr>
      <td class="tnav_battle" align="center" width="100%" style="padding-top: 1px; padding-bottom: 1px;">
        <select name="B_Difficulty" class="formselect" onchange="if (!window.__cfRLUnblockHandlers) return false; battle_difficulty(this.value);">
          <option value="veryeasy">Very Easy Mode</option>
          <option value="easy">Easy Mode</option>
          <option value="normal">Normal Mode</option>
          <option value="hard">Hard Mode</option>
          <option value="veryhard" id="B_DifficultySelected" selected="">Very Hard Mode</option>
        </select>
        <b>
          <i>
            <span id="B_DifficultyNotification"></span>
          </i>
        </b>
      </td>
    </tr>
  </tbody>
</table>

- HTML Evidence — Active Battle Page
  
  <!-- Paste active battle HTML here -->

- HTML Evidence — Player Pokémon / Level
  
  <!-- Paste player Pokémon and level HTML here -->

- HTML Evidence — EXP
  
  <!-- Paste current EXP HTML here -->

- HTML Evidence — Battle Result
  
  <!-- Paste battle victory/result HTML here -->

- HTML Evidence — Continue / Next Battle
  
  <!-- Paste continue/next battle HTML here -->

- [ ] Battle for X battles.
  
  - Ask the user how many battles to complete.
  
  - Stop after the requested number of battles.
  
  - Display battles completed and remaining.
  
  - Return to the Training menu when complete.
  
  - HTML Evidence
    
    <!-- Paste relevant battle-count/continue HTML here -->

- [ ] Train until a specific amount of experience is gained.
  
  - Let the user enter an EXP target.
  
  - Track EXP gained during the session.
  
  - Stop when the target EXP has been reached.
  
  - HTML Evidence — EXP Display
    
    <!-- Paste EXP display HTML here -->
  
  - HTML Evidence — Battle EXP Reward
    
    <!-- Paste battle EXP reward HTML here -->

- [ ] Automatically choose the best training area.
  
  - Detect available training areas.
  
  - Compare expected EXP.
  
  - Compare battle difficulty.
  
  - Select the most efficient area.
  
  - Avoid areas that are too difficult for the current Pokémon.
  
  - HTML Evidence — Training Area List
    
    <!-- Paste training area selection HTML here -->
  
  - HTML Evidence — Training Area Information
    
    <!-- Paste training area information HTML here -->
  
  - HTML Evidence — Training Area Requirements
    
    <!-- Paste training area unlock/requirement HTML here -->

- [ ] Training progress statistics.

<table class="outcome">
  <tbody>
    <tr>
      <td class="left_s">
        <img src="/images/icons/ShinyGastly.png">
      </td>
      <td class="right_s"> </td>
    </tr>
    
    <tr>
      <td class="left_s">+<b>30</b> levels</td>
      <td class="right_s">Lv. 9,530</td>
    </tr>
    
    <tr>
      <td class="left_s">+<b>15381596</b> EXP</td>
      <td class="right_s">273,596/505,160</td>
    </tr>
    
    <tr>
      <td class="left_s">+<b>11</b> Happiness</td>
      <td class="right_s">3138</td>
    </tr>
  </tbody>
</table>

- Track battles completed.

- Track levels gained.

- Track EXP gained.

- Track Happiness gained.

- Track Platinum Coins earned.

- Display session runtime.

- Display average EXP per battle.

- Display average levels per battle.

- HTML Evidence — Platinum Coins
  
  <!-- Paste Platinum Coin HTML here -->

- HTML Evidence — Happiness
  
  <!-- Paste Happiness HTML here -->

- HTML Evidence — Complete Battle Rewards
  
  <!-- Paste complete battle reward HTML here -->

- [ ] Resume training after an interruption.
  
  - Detect the current page/state when restarting.
  
  - Determine whether the bot is currently in a battle, result screen, or training area.
  
  - Resume from the appropriate state.
  
  - HTML Evidence — Training Page URL
    
    <!-- Paste training/battle URLs here -->
  
  - HTML Evidence — Recovery State
    
    <!-- Paste HTML encountered after interruption/refresh here -->

- [ ] Configurable battle preferences.
  
  - Preferred battle difficulty.
  - Preferred training area.
  - Preferred Pokémon.
  - Maximum battles.
  - Maximum runtime.
  - Safety limits.

- [ ] Be able to battle a user based on an inputted ID/Username
  
  - Ask for the user's ID or username.
  
  - Locate the user.
  
  - Open the battle page.
  
  - Start the battle.
  
  - Handle battle results.
  
  - HTML Evidence — User Search
    
    <!-- Paste user search HTML here -->
  
  - HTML Evidence — User Battle
    
    <!-- Paste user battle HTML here -->

---

🔎 Searching

- [x] Normal map searching.
- [x] Exclusive Legendary Areas searching.
- [ ] Automatically detect newly unlocked exclusive maps.
- [ ] Search for a specific Pokémon across available maps.
- [ ] Search for a specific variant/form.
- [ ] Search statistics and history.
- [ ] Configurable search delays.
- [ ] Automatically continue after successful Pokémon captures.
- [ ] Better encounter recovery when a battle page changes.
- [ ] Track Pokémon encountered during searches.
- [ ] Track rare/special Pokémon encounters.

HTML Evidence — Normal Maps

<!-- Paste normal map listing HTML here -->

HTML Evidence — Exclusive Legendary Areas

<!-- Paste exclusive legendary area listing HTML here -->

HTML Evidence — Locked Exclusive Areas

<!-- Paste locked/unavailable exclusive area HTML here -->

HTML Evidence — Map Links / IDs

<!-- Paste map link HTML here -->

HTML Evidence — Search Progress

<!-- Paste map search progress HTML here -->

HTML Evidence — Search Button

<!-- Paste Search button HTML here -->

HTML Evidence — Map Pokémon

<!-- Paste map Pokémon HTML here -->

HTML Evidence — Special Pokémon

<!-- Paste special Pokémon HTML here -->

---

⚔️ Battle & Capture

- [ ] More robust battle-button detection ("Fight", "Attack", and page variations).
- [ ] Automatically select a preferred Poké Ball.
- [ ] Automatically fall back to another available Poké Ball.
- [ ] Continue capture attempts after failed captures.
- [ ] Detect when a Pokémon has been successfully caught.
- [ ] Automatically click the post-capture "Continue" button.
- [ ] Recover gracefully if the battle page changes.
- [ ] Configurable capture strategy.
- [ ] Capture statistics.

HTML Evidence — Encounter Battle

<!-- Paste encounter battle HTML here -->

HTML Evidence — Fight / Attack Button

<!-- Paste Fight/Attack button HTML here -->

HTML Evidence — Item Button

<!-- Paste Item button HTML here -->

HTML Evidence — Poké Ball Selection

<!-- Paste Poké Ball selection HTML here -->

HTML Evidence — Selected Poké Ball

<!-- Paste selected Poké Ball HTML here -->

HTML Evidence — Capture Result

<!-- Paste successful/failed capture result HTML here -->

HTML Evidence — Use Another

<!-- Paste Use Another HTML here -->

HTML Evidence — Post-Capture Continue

<!-- Paste post-capture Continue button HTML here -->

---

💬 Messages

- [x] Message inbox viewer.
- [x] Show unread message count.
- [x] Read messages from the terminal.
- [x] Delete individual messages.
- [x] Bulk-delete messages.
- [x] Delete messages across all pages.
- [x] Confirmation before bulk deletion.
- [ ] Optional automatic cleanup of old messages.
- [ ] Make the delete messages more "Human Like"


🛒 Shops

- [ ] Shop category menu.
- [ ] View available shops.
- [ ] View item quantities/prices.
- [ ] Buy items automatically.
- [ ] Configurable minimum item quantities.
- [ ] Moon Shop support.
- [ ] Legendary Area purchasing support.
- [ ] Shop purchase history/statistics.

HTML Evidence — Shop Menu

<!-- Paste shop menu HTML here -->

HTML Evidence — Shop Item

<!-- Paste shop item HTML here -->

HTML Evidence — Purchase Button

<!-- Paste purchase button HTML here -->

HTML Evidence — Moon Shop

<!-- Paste Moon Shop HTML here -->

HTML Evidence — Legendary Area Purchase

<!-- Paste Legendary Area purchase HTML here -->

---

⚙️ Settings

- [ ] Central settings menu.
- [ ] Search delay settings.
- [ ] Training settings.
- [ ] Capture settings.
- [ ] Preferred Poké Ball.
- [ ] Safety limits.
- [ ] Account settings.
- [ ] Save settings between runs.

HTML Evidence — Account Settings

<!-- Paste account settings HTML here -->

HTML Evidence — Battle Settings

<!-- Paste battle settings HTML here -->

HTML Evidence — Search Settings

<!-- Paste search settings HTML here -->

---

📊 Statistics

- [ ] Search statistics.
- [ ] Battle statistics.
- [ ] Capture statistics.
- [ ] Pokémon caught during the current session.
- [ ] Training levels gained.
- [ ] Experience gained.
- [ ] Rare Pokémon encounter history.
- [ ] Session runtime.
- [ ] Export statistics to a file.

HTML Evidence — Search Statistics

<!-- Paste search statistics HTML here -->

HTML Evidence — Battle Statistics

<!-- Paste battle statistics HTML here -->

HTML Evidence — Capture Statistics

<!-- Paste capture statistics HTML here -->

HTML Evidence — Pokémon Statistics

<!-- Paste Pokémon statistics HTML here -->

---

🧹 Account Cleanup

- [ ] Message cleanup tool.
- [ ] Bulk cleanup with confirmation.
- [ ] Identify old/unwanted messages.
- [ ] Paginated cleanup for accounts with many message pages.
- [ ] Other safe account-maintenance tools.

HTML Evidence — Account Cleanup

<!-- Paste account cleanup HTML here -->

---

🗺️ Maps

- [ ] Display available normal maps.
- [ ] Display unlocked exclusive maps.
- [ ] Hide unavailable/locked exclusive maps.
- [ ] Show current search progress for each map.
- [ ] Show remaining searches.
- [ ] Show map Pokémon information.
- [ ] Map search history.
- [ ] Automatically detect map URLs/IDs instead of relying entirely on hard-coded names.

HTML Evidence — Normal Map

<!-- Paste normal map HTML here -->

HTML Evidence — Exclusive Map

<!-- Paste exclusive map HTML here -->

HTML Evidence — Locked Map

<!-- Paste locked map HTML here -->

HTML Evidence — Map URL / Area ID

<!-- Paste map URL and area_id HTML here -->

---

🧭 Main Menu

- [ ] Keep the categorized main-menu layout.
- [ ] Training submenu.
- [ ] Searching submenu.
- [ ] Battle/Capture submenu.
- [ ] Messages submenu.
- [ ] Shops submenu.
- [ ] Settings submenu.
- [ ] Statistics submenu.
- [ ] Account/Cleanup submenu.
- [ ] Display useful account information on startup.

---

🔐 Account Management

- [ ] Multiple saved accounts.
- [ ] Account selector.
- [ ] Saved credentials handling.
- [ ] Account-specific settings.
- [ ] Account-specific statistics.
- [ ] Safe logout/cleanup.

---

🛡️ Reliability

- [ ] Better handling of stale Selenium elements.
- [ ] Recover from unexpected page changes.
- [ ] Retry failed page actions safely.
- [ ] Detect Cloudflare/page-load interruptions.
- [ ] Prevent duplicate clicks.
- [ ] Prevent searches from stopping unnecessarily after recoverable encounter errors.
- [ ] Better logging and error messages.
- [ ] Session recovery.

HTML Evidence — Unexpected Page States

<!-- Paste unexpected/error page HTML here -->

HTML Evidence — Cloudflare / Loading

<!-- Paste Cloudflare/loading HTML here -->

HTML Evidence — Recovery Page

<!-- Paste recovery-related HTML here -->

---

💡 Future Ideas

- [ ] Command-line shortcuts for common actions.
- [ ] Configuration file for user preferences.
- [ ] Optional session logs.
- [ ] Export/import settings.
- [ ] Automated daily routines.
- [ ] Task queue for multiple automation jobs.
- [ ] Notification when a rare Pokémon is found.
- [ ] Notification when a training target is reached.
- [ ] Notification when an important task completes.
- [ ] Add a break mode. (Acts as if taking a break for x amount of time (minutes))

---

Priority

🔴 High Priority

- [ ] Battle until X level
- [ ] Reliable post-capture Continue handling
- [ ] Reliable Poké Ball selection/fallback
- [ ] Message bulk deletion
- [ ] Search recovery after encounter errors
- [ ] Central settings menu

🟡 Medium Priority

- [ ] Search statistics
- [ ] Battle/capture statistics
- [ ] Shop automation
- [ ] Pokémon-specific searching
- [ ] Better map discovery

🟢 Low Priority / Future

- [ ] Notifications
- [ ] Automated daily routines
- [ ] Task queue
- [ ] Export/import settings

---

📌 HTML Evidence Notes

When adding HTML evidence:

- Paste the raw HTML directly into the appropriate block.
- Keep important attributes such as "id", "class", "name", "href", "value", and "onclick".
- Keep surrounding "<table>", "<tr>", and "<td>" elements when possible.
- Include JavaScript such as "onclick" when it exists.
- If an element behaves differently depending on the page state, paste each version.
- If something fails, capture the HTML while it is failing.
- Screenshots can be included when useful, but raw HTML is preferred.
- Include the page URL when useful.
- Never include passwords, cookies, session tokens, or other private credentials.
