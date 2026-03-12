# PlateUp Multiworld Setup Guide

## Quick Start (Returning Players)

1. Fill in your config file at `%appdata%\..\LocalLow\It's Happening\PlateUp\PlateUpAPConfig` with your server, slot name, and password.
2. Launch PlateUp — the mod will **autoconnect** when you enter the lobby from the main menu, as long as a valid room is available.
3. Alternatively, connect manually via **Options → PreferenceSystem → PlateupAP → Connect** from either the main menu or the lobby.
4. Start a new run and select a dish — checks will begin sending automatically.

---

## Required Software

- [Latest Archipelago Version](https://github.com/ArchipelagoMW/Archipelago/releases/latest)
- [PlateUp!](https://store.steampowered.com/app/1599600/PlateUp/) on Steam
- [PlateUp Archipelago Mod](https://steamcommunity.com/sharedfiles/filedetails/?id=3484431423) — install via Steam Workshop (recommended) or manually from the GitHub releases page

For more information about yaml options and mod mechanics, refer to the full guide:
[PlateUp! Archipelago Mod Options & Features Guide](https://docs.google.com/document/d/1H_T82UsZbHI4CbvfHWnud8xZqhXH5XWc_sZkax1I8YY/edit?tab=t.0)

## Installation
[Video Guide](https://youtu.be/W5X0hPBpipE)

### Steam Workshop (Recommended)

1. Subscribe to the mod on the [Steam Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3484431423).
2. Subscribe to all required dependencies listed below — the Workshop page links to them.
3. Launch PlateUp. The config file will be generated automatically on first launch into the lobby (HQ).
4. Fill in your Archipelago server details in the config file located at:
   `%appdata%\..\LocalLow\It's Happening\PlateUp\PlateUpAPConfig`
   > **Tip:** You can paste this path directly into Windows Explorer's address bar to open the folder quickly.
5. The mod will autoconnect the next time you enter the lobby from the main menu, provided a valid room is available. You can also connect manually at any time via **Options → PreferenceSystem → PlateupAP → Connect**.

### Manual Installation

1. Download the latest release from the [mod repository](https://github.com/CazIsABoi/PlateUpAPMod/releases).
2. Extract the files into your PlateUp Mods folder:
   `Program Files (x86)\Steam\steamapps\common\PlateUp\PlateUp\Mods`
   > **Note:** This path may differ if Steam is installed in a non-default location. To find the correct path, right-click PlateUp in Steam → **Manage → Browse local files**, then navigate to the `Mods` folder.
3. Launch PlateUp. The config file will be generated automatically on first launch into the lobby (HQ).
4. Fill in your Archipelago server details in the config file located at:
   `%appdata%\..\LocalLow\It's Happening\PlateUp\PlateUpAPConfig`
   > **Tip:** You can paste this path directly into Windows Explorer's address bar to open the folder quickly.
5. The mod will autoconnect the next time you enter the lobby from the main menu, provided a valid room is available. You can also connect manually at any time via **Options → PreferenceSystem → PlateupAP → Connect**.

### Required Dependencies

The following mods must be installed alongside the Archipelago mod. If using the Steam Workshop, these are linked from the mod page. If installing manually, download each from the Workshop or their respective sources.

- PreferenceSystem
- PlatePatch
- KitchenLib
- HarmonyX

## Create a Config (.yaml) File

### What is a config file and why do I need one?

Your config file contains a set of options that tell the Archipelago generator how to set up your game. Each player in a multiworld provides their own config file, so everyone can have a different experience in the same seed.

### Where do I get a config file?

The [player settings page](../player-settings) on the Archipelago website lets you configure your options and export a config file. You can also use the default template yaml from the PlateUp apworld as a starting point and edit it manually.

### Verifying Your Config File

You can validate your config file on the [YAML Validator page](https://archipelago.gg/check) before using it in a multiworld to make sure there are no errors.

## Generating and Hosting the Multiworld

Generating a game and hosting an Archipelago server is explained in the [Archipelago Setup Guide](https://archipelago.gg/tutorial/Archipelago/setup/en). Once your world is generated you can host it on the Archipelago website or locally.

## Connecting to a MultiWorld

1. Open PlateUp with the Archipelago mod installed.
2. Open the config file at `%appdata%\..\LocalLow\It's Happening\PlateUp\PlateUpAPConfig` and fill in:
   - **Server**: Your Archipelago server address and port, for example `archipelago.gg:12345`
   - **SlotName**: The player name you used when creating your config file
   - **Password**: Your room password, or leave blank if there isn't one
3. Save the config file. No restart is needed.
4. **Recommended:** Return to (or launch into) the main menu and enter the lobby — the mod will **autoconnect automatically** if a valid room is available.
   - Alternatively, connect manually via **Options → PreferenceSystem → PlateupAP → Connect** from the main menu or the lobby.
5. Start a new run and select a dish — checks will begin sending automatically.

> **Note on dish locking:** Dish locking works correctly when connecting via the main menu or autoconnect. If you connect manually while already in the lobby, dish locking may not activate for that session. If this happens, start a run with any dish and lose, abandon, or return to the main menu — dish locking will work correctly from then on. Connecting via the main menu or autoconnect is always recommended.

## Multiplayer

PlateUp Archipelago supports a limited form of multiplayer. Only one player needs to have the mod installed:

- The player with the mod installed connects to the Archipelago server and acts as the host.
- Additional players join through PlateUp's standard multiplayer without the mod installed.

This is not fully verified and may vary between setups. If you find a more reliable method, please share it in the community.

## How Long Does a Run Take?

A single 15-day PlateUp run typically takes **20–40 minutes**, depending on whether the booking desk is used and how efficiently the restaurant runs.

Total playtime varies significantly based on your goal setting:

| Goal | Description | Estimated Length |
|---|---|---|
| `franchise_x_times` | Franchise your restaurant a set number of times | Longest — multiple full runs required |
| `complete_x_days` | Survive a set number of days across runs | Medium — depends on day count |
| `complete_x_days_with_dishes` | Reach a target day with a minimum number of active dishes | Variable — can be shorter or longer than franchising depending on settings |

For shorter seeds, consider a lower franchise count or a modest day target. For longer seeds, increase the goal requirements or pair them with higher dish counts.

## Options

Configure your PlateUp randomizer experience on your [player settings page](../player-settings). Key options include:

- **Goal**: Choose between franchising X times, completing X days, or reaching a target day with a minimum number of dishes active.
- **Dish Count**: How many dishes get dedicated checks and unlock items.
- **Free Starter Dishes**: How many dishes start already unlocked at the beginning of a run.
- **Day Leases**: Toggle day lease progression gates on or off, and set the interval between each required lease.
- **Money Cap**: Set a gold cap that only increases as you find Money Cap Increase items.
- **Starting Group Size**: Start your run with a larger customer group size for added difficulty.
- **Global Patience**: Add patience upgrade progression gates spread across the run.
- **Achievement Checks**: Enable in-game achievements as location checks.
- **Trap Cards**: Enable negative trap items such as patience decreases and extra customers.
- **Speed Upgrades**: Configure how many player and appliance speed upgrades are included.
- **Starting Cards**: Start your run with a set number of difficult customer cards already active.

For a full breakdown of every option, see the [Options & Features Guide](https://docs.google.com/document/d/1H_T82UsZbHI4CbvfHWnud8xZqhXH5XWc_sZkax1I8YY/edit?tab=t.0).

## Troubleshooting

**Config file not generating**
The config file is only created after entering the lobby (HQ) for the first time, not from the main menu alone. Make sure you have fully loaded into the lobby at least once.

**Mod not appearing in Options**
Verify that all required dependencies (PreferenceSystem, PlatePatch, KitchenLib, HarmonyX) are installed. Also check that you do not have both the Workshop and manual versions active at the same time.

**Dish locking not working after connecting in the lobby**
If you connected manually while already in the lobby, dish locking may not activate. Start a run with any dish and lose, abandon, or return to the main menu. Dish locking will work correctly from that point. To avoid this, always connect via the main menu or let autoconnect handle it.

**No dish unlock checks generated**
Re-enter the game, reconnect as usual, and make sure to select a new dish on your first run.

**Checks not sending / goal instantly completing**
Your yaml is likely out of date. A sign of an outdated yaml is if the goal option still shows `franchise_once`, `franchise_twice`, or `franchise_thrice`. Download the latest yaml template and update your options.

**Both Workshop and manual versions installed**
Only one version of the mod should be active at a time. Having both installed will cause conflicts. Use the Workshop version unless you have a specific reason to install manually.

**PlateUp update prompt blocking progression**
Press O, P, K, or L to bypass the prompt.

**Connected but no items are being received**
This may be a desync. Disconnect and reconnect from the main menu or via autoconnect, then continue your run.

---

**Still having issues?** Post in the thread or send a message to **cazisaboi** on Discord.
When reporting a problem, please **include your `Player.log`** file, found at:
`%appdata%\..\LocalLow\It's Happening\PlateUp\`
> **Tip:** You can paste this path directly into Windows Explorer's address bar to open the folder.
