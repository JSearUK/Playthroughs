# Ren-Py-Playthroughs-Save-System

## [ INTRODUCTION ]
- This package overrides the `save():` and `load():` screens, defining classes, functions, transitions, transforms and styling to support augmented functionality.
- The primary purpose is to provide an alternative, playthrough-style save/load system, whilst retaining access to the original system and files.

---
```scss
The aim is to create the system such that it can be safely dropped into any other project or distribution.

Current state: [Working] - not yet optimised for best practice, and may still contain bugs.
```
---
```yaml
License: This code will be free to use, but IS NOT YET PUBLICALLY RELEASED!
```
---
```php
Version 1.0

RenPy 7.4.11.2266 and newer; backwards compatibility is limited.

Windows: thorough testing, by myself.
Android, Linux, Macintosh: general testing, by others:
```
---

## [ CREDITS ]
*From the official Ren'Py Discord server:*

### Fen
- Provided code examples, and answered many, **many** questions!

### Jeevant
- Ran tests of the codebase on Android, and gave feedback on it.
- Contributed code.
- Introduced me to Wills747 🙂

### Jiao
- Confirmed viability of the codebase on a Macintosh. Thank you very much!

### OscarSix
- Showed an initial interest in the project, that helped me to stick with it 😅
- Provided a partial overhaul from which I learned many things - not least how to collaborate on GitHub!

### PastryIRL
- Provided code that showed me how to integrate the glyph icons more elegantly, as custom text tags - very much appreciated!

### Renpytom
- Provided code that solved a particularly intractable problem: scrolling text that did not display outside of a self-sized container. Many thanks! 🙏

### Wills747
- Ran tests of the codebase on Linux and Android, giving feedback.
- Contributed code.
- Suggested several ways in which I could abstract functionality, to reduce its impact on host projects 🙂

I selected a logo for myself, which is free to use and modify both personally and commercially, provided accreditation is given:
<a href="https://www.flaticon.com/free-icons/chimera" title="chimera icons">Chimera icons created by Freepik - Flaticon</a>

---

## [ USAGE ]
This package can most likely be used "as is"; just drop the files where they should go, and it should work correctly in the vast majority of cases. The following should be bourne in mind, though -
- Excessive font sizes produced via code, sliders and the Accessibilty screen can make the package hard to use. Nevertheless, the package does its best to make sure that all interactive elements are both accessible and stay where they should. Should you run into difficulties:
  - Note that hovering/long-pressing an element will provide details in the tooltip ribbon at the top of the area.
  - If further adjustment seems needed, first make sure the "Text Size Scaling" on the Accessibilty screen (Shift-A) is set to where you want it *for the host project* - as well as any text size sliders in **Preferences**, or in any other packages.
  - Finally, explicitly change the value of `textsize` in the `SetMetrics()` function.

Every effort has been made to not interfere with either the style or the functioning of the host project. Additionally, the code has been liberally sprinkled with commentary, usually explaining both what is happening and why; this has been left in to help developers track down and fix/report any issues that may occur.

---

## [ FILES ]
*.../game/Mods/Playthroughs/gui/NotoSansSymbols2-Regular.ttf*
- Glyph font provided, in order to utilise unicode text as symbols for icons. This permits the icons to support styling; notably scaling, colorisation and outlines. The font may be replaced, alternate glyphs selected, color changed, etc. Be aware that not all fonts have standard positioning; some manual adjustment may be necessary via the `glyphoffset` calibration variable.

*.../game/Mods/Playthroughs/gui/chimera.png*
- Personal logo, used in the Help Guide.

*.../game/Mods/Playthroughs/gui/slotforeground.png*\
*.../game/Mods/Playthroughs/gui/slotbackground.png*
- Default image files provided for save slot background and foreground. These may be replaced or edited as desired. By default, the foreground image is grayscale and tinted via code to match the color scheme of the GUI of the host project; this can be altered or disabled. By default, the background image is transparent.

*.../game/Mods/Playthroughs/overridescreens-saveload.rpy*
- The code file minimally disturbs pre-existing game code: the `save():` and `load():` screens are overridden, as are `config.after_load_transition` and `config.exit_transition`. The last two are used to reset the Playthroughs system when loading, or exiting the menus; if your code makes non-default use of these transitions already, please integrate the code found in the `ResetPtVars()` function into them.

---

## [ FEATURES ]
### Behaviour
- The package is aware of when it in on a mobile device, and makes the following changes:
  - Input/confirmation boxes are moved to the top of the screen, to account for the space taken by an on-screen keyboard.
  - A minimum text/button size is applied, to avoid many elements becoming too small for use.
  - Vertical scrollbars are thickened for ease of use (this package makes no use of horizontal scrollbars).
- The package does its best to match the color scheme of the host project.\
  If needed, this can be tweaked at `[ INITIALISATION - UI ]`
- Basic behaviours can be disabled via code toggles in the `[ INITIALISATION - BEHAVIOUR TOGGLES ]` section:
```py
# NOTE: The 'enable_' defines below will still perform their default behaviour if set to 'False' - but the
#       player will either not see their effect, or not be able to alter it.
define enable_versioning = True
    # This simply warns the player if a *Playthrough* save is from an older version of the game, by
    # graying out the thumbnail and writing details over the top of it. If the save is from a newer
    # version of the game, it will show a disabled placeholder if True, or nothing at all if False.
    # This is to prevent failed loads or loss of data.
define enable_renaming = True
    # This enables the player to provide/edit a friendly name for any existing Playthrough save.
define enable_locking = True
    # This enables the player to lock/unlock any Playthrough save. Locked saves cannot be renamed, over-
    # written or deleted in-game.
    # NOTE: If there are locked files present when 'enable_locking' is False, those files can be renamed
    #       and/or deleted. The "LOCKED" flag is preserved. This behaviour is correct.
define enable_sorting = True
    # This enables the player to sort Playthrough slotlists on a specified key.
    # It ships with "lastmodified", "slotnumber", "lockedstatus" and "versionnumber" by default.
define enable_iconcolors = True
    # This enables some glyphs to be color-coded. If False, all glyphs will be `textcolor`.
define enable_settings = any([enable_renaming])
    # This enables visibility of the cog icon at the top-right, which in turn provides access to those
    # settings considered useful to players.
    # - Currently, it enables the Settings panel if any of its toggles' dependencies are True

```

### Interaction
*General*
- Almost everything presented to the user has its own tooltip information, which can be accessed by hovering over it with the mouse, navigating to it with the keyboard, or using long-press on it (if using a mobile device).
- Assuming standard keybindings: Right-clicking with the mouse, pressing ESC on the keyboard or clicking on **Cancel** should cancel out of any open input/confirmation box.

*Original interface*
- A floating icon to switch to Playthroughs mode is displayed when the original Save/Load screens are visible. This can be positioned anywhere on the screen via the `[ INITIALISATION - UI ]` section near the top of the file or, if you wish to embed the button directly into your own `fileslots(title):` screen, disabled entirely.

*Playthroughs interface*
- A tooltip ribbon across the top, displaying feedback about whatever currently has focus. It will also inform the user of how to create a new Playthrough, if there currently are none.
- A vertical panel showing the available Playthroughs -
  - A horizontal panel of 1-4 buttons:
    - Switch to Ren'Py Save/Load system. This will do just that, accessing either the Save screen or the Load screen as appropriate.
    - Show Autosaves. This appears if `config.has_autosave` is True, and will grant access to the saves on the Ren'Py Auto page - these are common to both systems.
    - Show Quicksaves. This appears if `config.has_quicksave` is True, and will grant access to the saves on the Ren'Py Quick page. As with Autosaves, these are common to both systems.
    - Start a New Playthrough. This appears on the Save screen only, and will open an input box where a new Playthrough name may be entered. There are restrictions in place:
      - The name may not be an integer, as these are reserved for the paging system of the Ren'Py saves.
      - The name may not exceed 70 characters, to minimize the chance of encountering an operating system filename-length error. The current character count and limit are shown in the box.
      - The name may not contain certain characters, or be empty, to avoid operating system filename-invalid errors. These characters are listed in the box.
      - The name must be unique.
      - These checks are made during input which, under certain circumstances, may lead to slowdown. Once a name is considered valid, the **Confirm** button will become available.
  - A list of Playthroughs, presented in order of most recently changed.
    - Focusing a Playthrough will change the text color to `hovercolor`, and begin scrolling the name horizontally to ensure that it is all visible.
    - Selecting a Playthrough will change the text color to `hovercolor`, the background color to `textcolor`, populate the Saves panel, and make 1-2 additional buttons available at the sides of the Playthrough name:
      - If `enable_renaming` is true, Rename Playthrough. Positioned on the left, this will open the same input box used for naming a new Playthrough, with the same restrictions. Once a valid name is accepted, the system will then rename all saves in that Playthrough via partial string replacement - unless that save is locked, in which case it is left alone.
      - Delete Playthrough. Positioned on the right, this will prompt a confirmation box. The box will inform you of the number of saves that are locked and/or from a different version of the host project. **Pressing Confirm here will *immediately and irreversibly* delete all saves in that Playthrough, from _both_ of the Ren'Py save locations!**
- A vertical panel showing the Saves associated with the currently selected Playthrough -
  - If `enable_sorting` is true, a horizontal panel of 2+ buttons:
    - Sort by most recently changed.
    - Sort by slot number, highest first.
    - If `enable_locking` is true, Sort by locked status, locked first.
    - If `enable_versioning` is true, Sort by host project version number, lowest first.
  - A horizontal panel of 1+ buttons:
    - An icon that opens the Help Guide, which is an on-screen panel offering a brief guide on usage. Topics that have been disabled via Dev toggles are not referred to.
    - If `enable_settings` is true, an icon that opens the Settings Panel. This lets the player customise some behaviour according to personal preference.
  - If a Playthrough is selected, a list of save buttons, sorted by most recently changed (unless another sort key is selected). All interactive elements in these buttons will append the timestamp of the save to the tooltip. Each save button consists of:
    - A background image, found at *.../game/Mods/Playthroughs/gui/slotbackground.png*; this may instead be any displayable, or None.
    - A thumbnail image, showing the gameplay screen just prior to making the save, at the left and vertically centered. If the save is from an older version of the host project, and `enable_versioning` is true, the thumbnail will be dimmed and version information will be displayed over its center.
    - A vertical panel of 1-3 buttons at the right:
      - If `enable_renaming` is true and the save is not locked, Rename Save. This will open an input box similar to the one used for (re-)naming a Playthrough, except that numbers and duplicates are permitted.
      - If `enable_locking` is true, either Lock Save or Unlock Save, toggling locked status. Note that locked status merely prevents this package from making changes; nothing stops the operating system from doing so.
      - If the save is not locked, Delete Save. This will prompt a confirmation box. **Pressing Confirm here will *immediately and irreversibly* delete the save, from *both* of the Ren'Py save locations!**
    - The name of the save, centrally. When gaining focus, this will become `hovercolor` and begin scrolling vertically.
    - A foreground image, found at *.../game/Mods/Playthroughs/gui/slotforeground.png*; this may instead be any displayable, or None.
    - Certain special cases apply as follows:
      - If Quicksaves are selected, neither renaming nor locking are possible and sorting is disabled. They can be overwritten, however, if on the Save screen, loaded from if on the Load screen, and deleted from both.
      - If Autosaves are selected, neither renaming nor locking are possible, and both sorting and overwriting are disabled. They can be loaded if on the Load screen, and deleted from both.
      - If the save is from a version of the host project that appears to be greater than the current version (i.e. an earlier version was re-installed or rolled-back to), then loading will almost definitely fail and saving will almost definitely cause loss of progress. In this situation:
        - If `enable_versioning` is false, the save is not shown at all.
        - If `enable_versioning` is true, the save is displayed, but made insensitive. There is no thumbnail; the name and version are all that is shown, centrally, in `insensitivecolor`. 
      - If the save is actually a "**+ New Save +**" slot, it just displays that text in the center. On gaining focus it will change color and update the tooltip, but will not animate. When clicked, it will generate a save with a default name consisting of the Playthrough name followed by the highest slot number for this Playthrough +1 (this may take it over the character count limit).
        - However, if the saves are sorted by slot number, "**+ New Save +**" buttons will also be generated for every gap in the series; single-slot gaps will behave as above, but multi-slot gaps will require the user to specify which slot number they wish to save into. This will open an input box, which will accept any number in the valid range.
