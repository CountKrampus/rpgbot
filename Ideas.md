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
- [ ] Be able to search for specific pokemon in your box.

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



🛒 Shops

- [ ] Shop category menu.
- [ ] View available shops.
- [ ] View item quantities/prices.
- [ ] Buy items automatically.
- [ ] Configurable minimum item quantities.
- [x] Moon Shop support.
- [ ] Legendary Area purchasing support.
- [ ] Shop purchase history/statistics.

HTML Evidence — Shop Menu

<a href="/item_shop" class="active">Item Shop</a>

HTML Evidence — Shop Item

<table class="tnav_border"><tbody><tr>

  <td class="tnav_left_information" width="10%">
  Image
  </td>
  <td class="tnav_left_information " width="45%">
  Item Name
  </td>
  <td class="tnav_left_information" align="center" width="30%">
    Price
    </td><td class="tnav_information" width="15%" style="min-width: 70px">
  Buy
  </td>

  </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/pokeball.png" title="PokeBall" alt="PokeBall"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber1">PokeBall</span></b><br><i>A Ball thrown to catch a wild Pokémon. It is designed in a capsule style.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$200</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1, 1)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/great_ball.png" title="Great Ball" alt="Great Ball"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber2">Great Ball</span></b><br><i>This device is used to capture Pokemon. It is more effective than a PokeBall.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$600</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2, 2)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/ultra_ball.png" title="Ultra Ball" alt="Ultra Ball"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber3">Ultra Ball</span></b><br><i>This device is used to capture Pokemon. It is more effective than a Great Ball.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$1,200</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(3, 3)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/potion.png" title="Potion" alt="Potion"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber4">Potion</span></b><br><i>This item can be used to restore 250 HP to a Pokemon in battle. (20 in Special Story Mode.)</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$150</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(4, 4)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/super_potion.png" title="Super Potion" alt="Super Potion"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber5">Super Potion</span></b><br><i>This item can be used to restore 1,000 HP to a Pokemon during battle. (50 in Special Story Mode.)</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$350</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(5, 5)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/hyper_potion.png" title="Hyper Potion" alt="Hyper Potion"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber6">Hyper Potion</span></b><br><i>This item can be used to restore 5,000 HP to a Pokemon while in battle. (200 in Special Story Mode.)</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$500</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(6, 6)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/max_potion.png" title="Max Potion" alt="Max Potion"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber7">Max Potion</span></b><br><i>This item can be used to restore 10,000 HP to a Pokemon while in battle. (400 in Special Story Mode.)</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$1,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(7, 7)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/mp_restore_lv1.png" title="MP Restore Lv 1" alt="MP Restore Lv 1"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber8">MP Restore Lv 1</span></b><br><i>A powdery stimulant that restores the MP of one Pokémon by 50 points, or 10 points in Special Story Mode.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$100</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(8, 8)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/mp_restore_lv2.png" title="MP Restore Lv 2" alt="MP Restore Lv 2"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber9">MP Restore Lv 2</span></b><br><i>A powdery stimulant that restores the MP of one Pokémon by 125 points, or 20 points in Special Story Mode.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$200</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(9, 9)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/mp_restore_lv3.png" title="MP Restore Lv 3" alt="MP Restore Lv 3"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber10">MP Restore Lv 3</span></b><br><i>A powdery stimulant that restores the MP of one Pokémon by 200 points, or 30 points in Special Story Mode.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$300</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(10, 10)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/focus_scarf.png" title="Focus Scarf" alt="Focus Scarf"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber11">Focus Scarf</span></b><br><i>Decreases the chance that the enemy will land a critical hit.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(197, 11)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/razor_claw.png" title="Razor Claw" alt="Razor Claw"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber12">Razor Claw</span></b><br><i>Increases the chance that you will land a critical hit on the enemy.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$7,500</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(198, 12)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/type_boost.png" title="Type Boost" alt="Type Boost"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber13">Type Boost</span></b><br><i>If the type of the move you used is equal to one of your types, damage increases.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$7,500</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(199, 13)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/soothe_bell.png" title="Soothe Bell" alt="Soothe Bell"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber14">Soothe Bell</span></b><br><i>Increases Happiness gained by winning battles.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$10,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(286, 14)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/venusaurite.png" title="Venusaurite" alt="Venusaurite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber15">Venusaurite</span></b><br><i>Unleashes the inner strength of Venusaur, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(290, 15)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/charizarditex.png" title="Charizardite X" alt="Charizardite X"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber16">Charizardite X</span></b><br><i>Unleashes the inner strength of Charizard, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(292, 16)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/charizarditey.png" title="Charizardite Y" alt="Charizardite Y"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber17">Charizardite Y</span></b><br><i>Unleashes the inner strength of MegaCharizardX, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(293, 17)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/blastoisinite.png" title="Blastoisinite" alt="Blastoisinite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber18">Blastoisinite</span></b><br><i>Unleashes the inner strength of Blastoise, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(294, 18)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/sceptilite.png" title="Sceptilite" alt="Sceptilite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber19">Sceptilite</span></b><br><i>Unleashes the inner strength of Sceptile, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(295, 19)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/blazikenite.png" title="Blazikenite" alt="Blazikenite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber20">Blazikenite</span></b><br><i>Unleashes the inner strength of Blaziken, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(296, 20)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/swampertite.png" title="Swampertite" alt="Swampertite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber21">Swampertite</span></b><br><i>Unleashes the inner strength of Swampert, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$5,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(297, 21)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/diancite.png" title="Diancite" alt="Diancite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber22">Diancite</span></b><br><i>Unleashes the inner strength of Diancie, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$100,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(312, 22)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/zygardite.png" title="Zygardite" alt="Zygardite"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber23">Zygardite</span></b><br><i>Unleashes the inner strength of Zygarde, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$100,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(313, 23)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0"><img src="/images/items/mewtwonitex.png" title="Mewtwonite X" alt="Mewtwonite X"></td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber24">Mewtwonite X</span></b><br><i>Unleashes the inner strength of Mewtwo, causing it to mega evolve.</i></td><td class="tnav_left"><img src="/images/pictures/platinum_coins.png"> <b>$100,000,000</b><br>
        <i>Platinum Coins</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(314, 24)">Buy</button>
      </td>

      </tr></tbody></table>

HTML Evidence — Purchase Button

<button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1, 1)">Buy</button>

moon shop link: <a href="/moon_shop" class="active">Moon Shop</a>
moon shop buy: <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1450, 1)">Buy</button>

HTML Evidence — Moon Shop

<table class="tnav_border"><tbody><tr>

  <td class="tnav_left_information" width="10%">
  Image
  </td>
  <td class="tnav_left_information " width="45%">
  Item Name
  </td>
  <td class="tnav_left_information" align="center" width="30%">
    Price
    </td><td class="tnav_information" width="15%" style="min-width: 70px">
  Buy
  </td>

  </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisAbsol">
            <img src="/images/pokemon/GenesisAbsol.png?91193" style="; max-width: 120px; height: auto" alt="Genesis Absol" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber1">GenesisAbsol</span></b><div><small>1/100 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RetroAbsol&amp;color=Legacy">LegacyRetroAbsol</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1450, 1)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroWooper">
            <img src="/images/pokemon/RetroWooper.png?91193" style="; max-width: 120px; height: auto" alt="Retro Wooper" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber2">RetroWooper</span></b><div><small>1/250 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperWooper&amp;color=Shiny">ShinyHyperWooper</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>200</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1305, 2)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Torkoal">
            <img src="/images/pokemon/SilverTorkoal.png?91193" style="; max-width: 120px; height: auto" alt="Silver Torkoal" width="85" height="85">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber3">SilverTorkoal</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>350</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1069, 3)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisWooper">
            <img src="/images/pokemon/SapphireGenesisWooper.png?91193" style="; max-width: 120px; height: auto" alt="Sapphire Genesis Wooper" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber4">SapphireGenesisWooper</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>450</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1070, 4)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperSkitty">
            <img src="/images/pokemon/RubyHyperSkitty.png?91193" style="; max-width: 120px; height: auto" alt="Ruby Hyper Skitty" width="59" height="55">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber5">RubyHyperSkitty</span></b><div><small>1/50 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxySkitty&amp;color=Ruby">RubyHyperGalaxySkitty</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>650</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1072, 5)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicMankey">
            <img src="/images/pokemon/EmeraldRelicMankey.png?91193" style="; max-width: 120px; height: auto" alt="Emerald Relic Mankey" width="56" height="56">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber6">EmeraldRelicMankey</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>750</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1073, 6)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyJoltik">
            <img src="/images/pokemon/HyperGalaxyJoltik.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Galaxy Joltik" width="57" height="41">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber7">HyperGalaxyJoltik</span></b><div><small>1/75 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyJoltik&amp;color=Normal">GalaxyJoltik</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1076, 7)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicNidoranF">
            <img src="/images/pokemon/RelicNidoranF.png?91193" style="; max-width: 120px; height: auto" alt="Relic Nidoran F" width="56" height="56">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber8">RelicNidoranF</span></b><div><small>1/50 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RelicNidoranF&amp;color=Shiny">ShinyRelicNidoranF</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1075, 8)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicNidoranM">
            <img src="/images/pokemon/RelicNidoranM.png?91193" style="; max-width: 120px; height: auto" alt="Relic Nidoran M" width="56" height="56">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber9">RelicNidoranM</span></b><div><small>1/50 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RelicNidoranM&amp;color=Shiny">ShinyRelicNidoranM</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1074, 9)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperVanillite">
            <img src="/images/pokemon/HyperVanillite.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Vanillite" width="49" height="63">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber10">HyperVanillite</span></b><div><small>1/75 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperVanillite&amp;color=Shiny">ShinyHyperVanillite</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,500</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1077, 10)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Spearow">
            <img src="/images/pokemon/AstralSpearow.png?91193" style="; max-width: 120px; height: auto" alt="Astral Spearow" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber11">AstralSpearow</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RelicCyndaquil&amp;color=Emerald">EmeraldRelicCyndaquil</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>2,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2025, 11)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Cosmee">
            <img src="/images/pokemon/DarkCosmee.png?91193" style="; max-width: 120px; height: auto" alt="Dark Cosmee" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber12">DarkCosmee</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>2,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1078, 12)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicCleffa">
            <img src="/images/pokemon/RelicCleffa.png?91193" style="; max-width: 120px; height: auto" alt="Relic Cleffa" width="56" height="56">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber13">RelicCleffa</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RelicCleffa&amp;color=Sapphire">SapphireRelicCleffa</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>3,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1509, 13)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Popplio">
            <img src="/images/pokemon/CrystalPopplio.png?91193" style="; max-width: 120px; height: auto" alt="Crystal Popplio" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber14">CrystalPopplio</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Popplio&amp;color=Shadow">ShadowPopplio</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1289, 14)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperHoundour">
            <img src="/images/pokemon/HyperHoundour.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Houndour" width="36" height="59">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber15">HyperHoundour</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyHoundour&amp;color=Pearl">PearlGalaxyHoundour</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1455, 15)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=BadEgg">
            <img src="/images/pokemon/PearlBadEgg.png?91193" style="; max-width: 120px; height: auto" alt="Pearl Bad Egg" width="85" height="85">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber16">PearlBadEgg</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyTogepi&amp;color=Shadow">ShadowGalaxyTogepi</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1082, 16)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=ButtStallion">
            <img src="/images/pokemon/RainbowButtStallion.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Butt Stallion" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber17">RainbowButtStallion</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1079, 17)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyRalts">
            <img src="/images/pokemon/RainbowGalaxyRalts.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Galaxy Ralts" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber18">RainbowGalaxyRalts</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(890, 18)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisMiltank">
            <img src="/images/pokemon/RainbowGenesisMiltank.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Genesis Miltank" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber19">RainbowGenesisMiltank</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1081, 19)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroLapras">
            <img src="/images/pokemon/RetroLapras.png?91193" style="; max-width: 120px; height: auto" alt="Retro Lapras" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber20">RetroLapras</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RetroLapras&amp;color=Legacy">LegacyRetroLapras</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>5,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1080, 20)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyGrowlithe">
            <img src="/images/pokemon/HyperGalaxyGrowlithe.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Galaxy Growlithe" width="55" height="67">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber21">HyperGalaxyGrowlithe</span></b><div><small>1/50 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RetroGrowlithe&amp;color=Legacy">LegacyRetroGrowlithe</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>6,500</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1083, 21)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroDratini">
            <img src="/images/pokemon/GoldenRetroDratini.png?91193" style="; max-width: 120px; height: auto" alt="Golden Retro Dratini" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber22">GoldenRetroDratini</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>8,500</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1084, 22)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicSandshrew">
            <img src="/images/pokemon/LegacyRelicSandshrew.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Relic Sandshrew" width="66" height="66">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber23">LegacyRelicSandshrew</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>10,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1085, 23)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperBidoof">
            <img src="/images/pokemon/PearlHyperBidoof.png?91193" style="; max-width: 120px; height: auto" alt="Pearl Hyper Bidoof" width="52" height="46">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber24">PearlHyperBidoof</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Bidoof&amp;color=Pearl">PearlBidoof</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>10,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1086, 24)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroNidoranM">
            <img src="/images/pokemon/RainbowRetroNidoranM.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Retro Nidoran M" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber25">RainbowRetroNidoranM</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>10,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1148, 25)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroElectrike">
            <img src="/images/pokemon/RetroElectrike.png?91193" style="; max-width: 120px; height: auto" alt="Retro Electrike" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber26">RetroElectrike</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RetroElectrike&amp;color=Shiny">ShinyRetroElectrike</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>12,500</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1087, 26)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroSeviper">
            <img src="/images/pokemon/LegacyRetroSeviper.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Retro Seviper" width="80" height="82">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber27">LegacyRetroSeviper</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>15,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1089, 27)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroZangoose">
            <img src="/images/pokemon/LegacyRetroZangoose.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Retro Zangoose" width="74" height="74">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber28">LegacyRetroZangoose</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>15,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1088, 28)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Mareep">
            <img src="/images/pokemon/AstralMareep.png?91193" style="; max-width: 120px; height: auto" alt="Astral Mareep" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber29">AstralMareep</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1093, 29)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperRalts">
            <img src="/images/pokemon/DarkHyperRalts.png?91193" style="; max-width: 120px; height: auto" alt="Dark Hyper Ralts" width="32" height="52">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber30">DarkHyperRalts</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1091, 30)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyFennekin">
            <img src="/images/pokemon/HyperGalaxyFennekin.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Galaxy Fennekin" width="61" height="69">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber31">HyperGalaxyFennekin</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1090, 31)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperToxel">
            <img src="/images/pokemon/HyperToxel.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Toxel" width="49" height="57">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber32">HyperToxel</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1094, 32)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperTurtwig">
            <img src="/images/pokemon/LightHyperTurtwig.png?91193" style="; max-width: 120px; height: auto" alt="Light Hyper Turtwig" width="45" height="59">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber33">LightHyperTurtwig</span></b><div><small>1/5 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyTurtwig&amp;color=Normal">GalaxyTurtwig</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1092, 33)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Weedle">
            <img src="/images/pokemon/RainbowWeedle.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Weedle" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber34">RainbowWeedle</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1096, 34)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyArticuno">
            <img src="/images/pokemon/RubyGalaxyArticuno.png?91193" style="; max-width: 120px; height: auto" alt="Ruby Galaxy Articuno" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber35">RubyGalaxyArticuno</span></b><div><small>1/12 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=RetroEkans&amp;color=Golden">GoldenRetroEkans</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1717, 35)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Joltik">
            <img src="/images/pokemon/SapphireJoltik.png?91193" style="; max-width: 120px; height: auto" alt="Sapphire Joltik" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber36">SapphireJoltik</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1253, 36)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Grookey">
            <img src="/images/pokemon/SilverGrookey.png?91193" style="; max-width: 120px; height: auto" alt="Silver Grookey" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber37">SilverGrookey</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>25,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1095, 37)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperCetoddle">
            <img src="/images/pokemon/HyperCetoddle.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Cetoddle" width="98" height="65">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber38">HyperCetoddle</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperCetoddle&amp;color=Ruby">RubyHyperCetoddle</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>30,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1503, 38)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperTandemaus">
            <img src="/images/pokemon/HyperTandemaus.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Tandemaus" width="99" height="53">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber39">HyperTandemaus</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperTandemaus&amp;color=Golden">GoldenHyperTandemaus</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>30,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1502, 39)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroHoundour">
            <img src="/images/pokemon/GoldenRetroHoundour.png?91193" style="; max-width: 120px; height: auto" alt="Golden Retro Houndour" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber40">GoldenRetroHoundour</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1601, 40)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroWurmple">
            <img src="/images/pokemon/LegacyRetroWurmple.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Retro Wurmple" width="74" height="74">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber41">LegacyRetroWurmple</span></b><div><small>1/5 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyWurmple&amp;color=Normal">GalaxyWurmple</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1698, 41)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxySnubbull">
            <img src="/images/pokemon/ShadowGalaxySnubbull.png?91193" style="; max-width: 120px; height: auto" alt="Shadow Galaxy Snubbull" width="80" height="80">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber42">ShadowGalaxySnubbull</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1500, 42)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisMudkip">
            <img src="/images/pokemon/ShadowGenesisMudkip.png?91193" style="; max-width: 120px; height: auto" alt="Shadow Genesis Mudkip" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber43">ShadowGenesisMudkip</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1099, 43)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisTreecko">
            <img src="/images/pokemon/ShadowGenesisTreecko.png?91193" style="; max-width: 120px; height: auto" alt="Shadow Genesis Treecko" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber44">ShadowGenesisTreecko</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1098, 44)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperSpinda">
            <img src="/images/pokemon/ShadowHyperSpinda.png?91193" style="; max-width: 120px; height: auto" alt="Shadow Hyper Spinda" width="61" height="69">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber45">ShadowHyperSpinda</span></b><div><small>1/25 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxySpinda&amp;color=Shadow">ShadowHyperGalaxySpinda</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1292, 45)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperSeedot">
            <img src="/images/pokemon/ShinyHyperSeedot.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Hyper Seedot" width="37" height="46">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber46">ShinyHyperSeedot</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1100, 46)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroHoundour">
            <img src="/images/pokemon/ShinyRetroHoundour.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Retro Houndour" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber47">ShinyRetroHoundour</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>50,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1097, 47)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyBagon">
            <img src="/images/pokemon/EmeraldGalaxyBagon.png?91193" style="; max-width: 120px; height: auto" alt="Emerald Galaxy Bagon" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber48">EmeraldGalaxyBagon</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>60,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(891, 48)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyPoochyena">
            <img src="/images/pokemon/SapphireHyperGalaxyPoochyena.png?91193" style="; max-width: 120px; height: auto" alt="Sapphire Hyper Galaxy Poochyena" width="62" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber49">SapphireHyperGalaxyPoochyena</span></b><div><small>1/9 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyPoochyena&amp;color=Sapphire">SapphireGalaxyPoochyena</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>90,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1744, 49)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyGible">
            <img src="/images/pokemon/CrystalGalaxyGible.png?91193" style="; max-width: 120px; height: auto" alt="Crystal Galaxy Gible" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber50">CrystalGalaxyGible</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1602, 50)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyPichu">
            <img src="/images/pokemon/DarkHyperGalaxyPichu.png?91193" style="; max-width: 120px; height: auto" alt="Dark Hyper Galaxy Pichu" width="61" height="62">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber51">DarkHyperGalaxyPichu</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2026, 51)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperHoundour">
            <img src="/images/pokemon/DarkHyperHoundour.png?91193" style="; max-width: 120px; height: auto" alt="Dark Hyper Houndour" width="36" height="59">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber52">DarkHyperHoundour</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1738, 52)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Marshadow">
            <img src="/images/pokemon/DarkMarshadow.png?91193" style="; max-width: 120px; height: auto" alt="Dark Marshadow" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber53">DarkMarshadow</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1101, 53)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Shroomish">
            <img src="/images/pokemon/RainbowShroomish.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Shroomish" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber54">RainbowShroomish</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1452, 54)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=TypeNull">
            <img src="/images/pokemon/ShinyTypeNull.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Type Null" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber55">ShinyTypeNull</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>100,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1102, 55)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=VirusPorygon">
            <img src="/images/pokemon/DarkVirusPorygon.png?91193" style="; max-width: 120px; height: auto" alt="Dark Virus Porygon" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber56">DarkVirusPorygon</span></b><div><small>1/12 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Porygon&amp;color=Dark">DarkPorygon</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>137,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1567, 56)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyMareep">
            <img src="/images/pokemon/HyperGalaxyMareep.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Galaxy Mareep" width="62" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber57">HyperGalaxyMareep</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>150,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1665, 57)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperSpectrier">
            <img src="/images/pokemon/HyperSpectrier.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Spectrier" width="72" height="108">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber58">HyperSpectrier</span></b><div><small>1/5 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Spectrier&amp;color=Astral">AstralSpectrier</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>150,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1104, 58)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyRegidrago">
            <img src="/images/pokemon/ShinyHyperGalaxyRegidrago.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Hyper Galaxy Regidrago" width="129" height="130">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber59">ShinyHyperGalaxyRegidrago</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>150,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1103, 59)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RetroTrapinch">
            <img src="/images/pokemon/SilverRetroTrapinch.png?91193" style="; max-width: 120px; height: auto" alt="Silver Retro Trapinch" width="64" height="64">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber60">SilverRetroTrapinch</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>150,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1673, 60)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyScymew">
            <img src="/images/pokemon/GalaxyScymew.png?91193" style="; max-width: 120px; height: auto" alt="Galaxy Scymew" width="85" height="85">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber61">GalaxyScymew</span></b><div><small>1/5 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Scymew&amp;color=Rainbow">RainbowScymew</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>200,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1105, 61)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Celesteela">
            <img src="/images/pokemon/ShinyCelesteela.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Celesteela" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber62">ShinyCelesteela</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>200,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1339, 62)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxySans">
            <img src="/images/pokemon/DarkGalaxySans.png?91193" style="; max-width: 120px; height: auto" alt="Dark Galaxy Sans" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber63">DarkGalaxySans</span></b><div><small>1/10 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=GalaxySans&amp;color=Light">LightGalaxySans</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>250,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1668, 63)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisGalaxyIgglybuff">
            <img src="/images/pokemon/GenesisGalaxyIgglybuff.png?91193" style="; max-width: 120px; height: auto" alt="Genesis Galaxy Igglybuff" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber64">GenesisGalaxyIgglybuff</span></b><br><i>Available until December 31</i><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>250,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1716, 64)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperToedscool">
            <img src="/images/pokemon/GoldenHyperToedscool.png?91193" style="; max-width: 120px; height: auto" alt="Golden Hyper Toedscool" width="31" height="63">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber65">GoldenHyperToedscool</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>300,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1480, 65)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyLunala">
            <img src="/images/pokemon/HyperGalaxyLunala.png?91193" style="; max-width: 120px; height: auto" alt="Hyper Galaxy Lunala" width="138" height="111">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber66">HyperGalaxyLunala</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>300,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1107, 66)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=RelicSuicune">
            <img src="/images/pokemon/LegacyRelicSuicune.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Relic Suicune" width="66" height="66">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber67">LegacyRelicSuicune</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>300,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1108, 67)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperStakataka">
            <img src="/images/pokemon/PearlHyperStakataka.png?91193" style="; max-width: 120px; height: auto" alt="Pearl Hyper Stakataka" width="150" height="150">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber68">PearlHyperStakataka</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>300,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1419, 68)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Tatsugiri">
            <img src="/images/pokemon/LegacyTatsugiri.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Tatsugiri" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber69">LegacyTatsugiri</span></b><br><i>Available until October 10</i><div><small>1/22 odds of 
          <a target="_blank" href="/amount_viewer?pokemon=Dondozo&amp;color=Legacy">LegacyDondozo</a>
          </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>333,333</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1718, 69)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalarianZapdos">
            <img src="/images/pokemon/SapphireGalarianZapdos.png?91193" style="; max-width: 120px; height: auto" alt="Sapphire Galarian Zapdos" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber70">SapphireGalarianZapdos</span></b><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>500,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1689, 70)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyMeloetta">
            <img src="/images/pokemon/RainbowGalaxyMeloetta.png?91193" class="rainbow-sprite" style="; max-width: 120px; height: auto" alt="Rainbow Galaxy Meloetta" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber71">RainbowGalaxyMeloetta</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>750,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(1692, 71)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyOriginGiratina">
            <img src="/images/pokemon/AstralHyperGalaxyOriginGiratina.png?91193" style="; max-width: 120px; height: auto" alt="Astral Hyper Galaxy Origin Giratina" width="166" height="164">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber72">AstralHyperGalaxyOriginGiratina</span></b><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>850,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2049, 72)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GalaxyBetaTrifox">
            <img src="/images/pokemon/DarkGalaxyBetaTrifox.png?91193" style="; max-width: 120px; height: auto" alt="Dark Galaxy Beta Trifox" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber73">DarkGalaxyBetaTrifox</span></b><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,000,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2075, 73)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=GenesisGalaxyLatias">
            <img src="/images/pokemon/AstralGenesisGalaxyLatias.png?91193" style="; max-width: 120px; height: auto" alt="Astral Genesis Galaxy Latias" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber74">AstralGenesisGalaxyLatias</span></b><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,500,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2077, 74)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=Lunaleo">
            <img src="/images/pokemon/DarkLunaleo.png?91193" style="; max-width: 120px; height: auto" alt="Dark Lunaleo" width="96" height="96">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber75">DarkLunaleo</span></b><br><i>Available until September 23</i><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>1,500,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2019, 75)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyHo-oh">
            <img src="/images/pokemon/GoldenHyperGalaxyHo-oh.png?91193" style="; max-width: 120px; height: auto" alt="Golden Hyper Galaxy Ho-oh" width="167" height="154">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber76">GoldenHyperGalaxyHo-oh</span></b><br><i>Available until February 1, 2027</i><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>2,000,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2079, 76)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperGalaxyAzelf">
            <img src="/images/pokemon/LegacyHyperGalaxyAzelf.png?91193" style="; max-width: 120px; height: auto" alt="Legacy Hyper Galaxy Azelf" width="103" height="106">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber77">LegacyHyperGalaxyAzelf</span></b></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>2,000,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2028, 77)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=HyperRoaringMoon">
            <img src="/images/pokemon/ShadowHyperRoaringMoon.png?91193" style="; max-width: 120px; height: auto" alt="Shadow Hyper Roaring Moon" width="155" height="163">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber78">ShadowHyperRoaringMoon</span></b><br><i>Available until January 1, 2027</i></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>2,000,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2078, 78)">Buy</button>
      </td>

      </tr><tr>

      <td class="tnav_left" style="line-height: 0">
        <div class="sprite-container image-link tooltip tooltipstered" style="align-items: flex-end">
          <a target="_blank" href="/amount_viewer?pokemon=NobleShaymin">
            <img src="/images/pokemon/ShinyNobleShaymin.png?91193" style="; max-width: 120px; height: auto" alt="Shiny Noble Shaymin" width="36" height="36">
          </a>
        </div>
        </td>
      <td class="tnav_left  ">
      <b><span id="S_ItemNumber79">ShinyNobleShaymin</span></b><br><i>Available until April 20, 2027</i><div><small>One per player </small></div></td><td class="tnav_left"><img src="/images/pictures/moon_points.png"> <b>4,000,000</b><br>
        <i>Moon Points</i>
        </td><td class="tnav">
      <button class="inputsubmit" onclick="if (!window.__cfRLUnblockHandlers) return false; shop_purchase(2029, 79)">Buy</button>
      </td>

      </tr></tbody></table>

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
