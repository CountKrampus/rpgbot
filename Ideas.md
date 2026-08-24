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
  - Changes the fight difficulty to help ensure it gets as close to that level as possible (<table cellpadding="3" cellspacing="2" width="100%"><tbody><tr><td class="tnav_battle_information" align="center" width="100%">Battle Difficulty</td></tr><tr><td class="tnav_battle" align="center" width="100%" style="padding-top: 1px; padding-bottom: 1px;">Higher battle difficulty makes battles harder but increases EXP and Platinum Coins earned.</td></tr><tr><td class="tnav_battle" align="center" width="100%" style="padding-top: 1px; padding-bottom: 1px;"><select name="B_Difficulty" class="formselect" onchange="if (!window.__cfRLUnblockHandlers) return false; battle_difficulty(this.value);"><option value="veryeasy">Very Easy Mode</option><option value="easy">Easy Mode</option><option value="normal">Normal Mode</option><option value="hard">Hard Mode</option><option value="veryhard" id="B_DifficultySelected" selected="">Very Hard Mode</option></select><b><i><span id="B_DifficultyNotification"></span></i></b></td></tr></tbody></table>)

- [ ] Battle for X battles.

- [ ] Train until a specific amount of experience is gained.

- [ ] Automatically choose the best training area.

- [ ] Training progress statistics.
(<table class="outcome">
  <tbody><tr><td class="left_s"><img src="/images/icons/ShinyGastly.png"></td><td class="right_s"> </td></tr>
  
    <tr><td class="left_s">+<b>30</b> levels</td><td class="right_s">Lv. 9,530</td></tr>
  <tr><td class="left_s">+<b>15381596</b> EXP</td><td class="right_s">273,596/505,160</td></tr><tr><td class="left_s">+<b>11</b> Happiness</td><td class="right_s">3138</td></tr>
  
  </tbody></table>)
      

- [ ] Resume training after an interruption.

- [ ] Configurable battle preferences.
- [ ] Be able to battle a user based on an inputted ID/Username

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

💬 Messages

- [ ] Message inbox viewer.
- [ ] Show unread message count.
- [ ] Read messages from the terminal.
- [ ] Delete individual messages.
- [ ] Bulk-delete messages.
- [ ] Delete messages across all pages.
- [ ] Confirmation before bulk deletion.
- [ ] Optional automatic cleanup of old messages.

🛒 Shops

- [ ] Shop category menu.
- [ ] View available shops.
- [ ] View item quantities/prices.
- [ ] Buy items automatically.
- [ ] Configurable minimum item quantities.
- [ ] Moon Shop support.
- [ ] Legendary Area purchasing support.
- [ ] Shop purchase history/statistics.

⚙️ Settings

- [ ] Central settings menu.
- [ ] Search delay settings.
- [ ] Training settings.
- [ ] Capture settings.
- [ ] Preferred Poké Ball.
- [ ] Safety limits.
- [ ] Account settings.
- [ ] Save settings between runs.

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

🧹 Account Cleanup

- [ ] Message cleanup tool.
- [ ] Bulk cleanup with confirmation.
- [ ] Identify old/unwanted messages.
- [ ] Paginated cleanup for accounts with many message pages.
- [ ] Other safe account-maintenance tools.

🗺️ Maps

- [ ] Display available normal maps.
- [ ] Display unlocked exclusive maps.
- [ ] Hide unavailable/locked exclusive maps.
- [ ] Show current search progress for each map.
- [ ] Show remaining searches.
- [ ] Show map Pokémon information.
- [ ] Map search history.
- [ ] Automatically detect map URLs/IDs instead of relying entirely on hard-coded names.

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

🔐 Account Management

- [ ] Multiple saved accounts.
- [ ] Account selector.
- [ ] Saved credentials handling.
- [ ] Account-specific settings.
- [ ] Account-specific statistics.
- [ ] Safe logout/cleanup.

🛡️ Reliability

- [ ] Better handling of stale Selenium elements.
- [ ] Recover from unexpected page changes.
- [ ] Retry failed page actions safely.
- [ ] Detect Cloudflare/page-load interruptions.
- [ ] Prevent duplicate clicks.
- [ ] Prevent searches from stopping unnecessarily after recoverable encounter errors.
- [ ] Better logging and error messages.
- [ ] Session recovery.

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
