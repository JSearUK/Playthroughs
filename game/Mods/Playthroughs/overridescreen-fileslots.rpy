# [ DEBUG TOGGLES - REMOVE ALL CODE REFERENCING THESE BINDINGS ]
define config.developer = True
define testplaythroughlistsize = False
    # TODO: The more buttons (and viewports?) onscreen, the more sluggish the UI gets. Attempt to optimise (especially for phones?)
        # NOTE: Removing the viewports from the Playthrough list didn't improve anything. It has to be the buttons... although: try turning prediction off for this screen?
        # NOTE: It could also be us dipping in and out of AwaitUserInput() at 300+Hz, although I doubt it. Worth checking... somehow


# [ NEXT TASKS ]
# - BUG: When a versioned (old) slot has focus:
#   - Tooltip says overwrite (no warning)
#   - Clicking attempts an overwrite with no warning, produces a new save with the same name
#   - Second attempt will produce a warning (not tested further to avoid obliterating test file)
# - Investigate how to play nicely with the Accessibilty screen, or people adjusting text size via Preferences
#   - [EDIT:] These are actual Preferences variables, and thus checkable
# - Refactor slot numbers so that they may be infinite. At the same time, fix the bug that occurs if the dev has a "-" in the version number.
# - Consider Slotbutton redesign to accomodate mobile devices more easily NOTE: This is becoming more and more of a priority.
#   - [EDIT:] This may fix the Roald Dahl bug. Remember to simplify, and to use 'side "":'
#   - [EDIT:] Check that the vscrollbar in the name viewport has no right-hand spacing if it's up against the edge of the slot
# - Streamline and triple-check styles are behaving correctly
# - Investigate and solve the '.isdecimal()' issue noted when dropping the package into older games - [EDIT:] Oscar seemd to solve this by testing against 'not'
# - Get all mod variables into its own named store
# - Adapt all user-viewable strings to support translation
# - Write and test package against the feature list on GitHub


# [ INITIALISATION - CORE - BEST TO LEAVE ALONE ]
# When exiting the game menu, or after loading, clear the variables that store the details of the playthrough being viewed. Do this by re-assigning a custom transition to those events
# - NOTE: The specified duration needs to be greater than zero for the function to be called. Any transition where a function can be specified may be used
# - NOTE: These lines redefine existing defines. This is not best practice, but it does mean that we can keep all of the changes of this mod to one file, and avoid altering further screens
# - NOTE: If this behaviour is not desired, simply comment out the two lines below
define config.after_load_transition = Dissolve(1, time_warp=ResetPtVars)
define config.exit_transition = Dissolve(1, time_warp=ResetPtVars)
define pathoffset = "Mods/Playthroughs/"
default persistent.save_system = "original"
default persistent.sortby = "lastmodified"
default persistent.playthroughslist = []
    # TODO: Does this need to be persistent? This might be causing the cpickle fail after package deletion. We can always repopulate on run, which is probably safer anyway...
default viewingptname = ""
default viewingpt = []
default userinput = ""
default targetaction = ""
default slotdetails = []


# [ INITIALISATION - BEHAVIOUR TOGGLES ]
# NOTE: The four 'enable_' defines below will still perform their default behaviour if set to 'False' - but the player will either not see their effect, or not be able to alter it
define enable_versioning = True
    # This simply warns the player if a *Playthrough* save is from an older version of the game, by graying out the thumbnail and writing details over the top of it
    # If the save is from a newer version of the game, it will show: a disabled placeholder if True, or nothing at all if False. This is to prevent failed loads or loss of data
define enable_renaming = True
    # This enables the player to provide/edit a friendly name for any existing Playthrough save
    # TODO: For Ren'Py saves (excluding Auto/Quick), it shows an overlay/button on the slot that can be clicked on to provide a name for the new/overwritten slot
    # - [EDIT:] This is on hold, for now
define enable_locking = True
    # This enables the player to lock/unlock any Playthrough save. Locked saves cannot be renamed, overwritten or deleted in-game
    # - NOTE: If there are locked files present when 'enable_locking' is False, those files can be renamed and/or deleted. The "LOCKED" flag is preserved. This behaviour is correct.
define enable_sorting = True
    # This enables the player to sort Playthrough slotlists on a specified key. It ships with "lastmodified", "slotnumber", "versionnumber" and "lockedstatus" by default
define enable_iconcolors = True
    # This enables some glyphs to be color-coded. If False, all glyphs will be `textcolor`
        # TODO: This may be better as a persistent toggle, possibly changed by this packages' Preferences screen


# [ INITIALISATION - CONVENIENCE ]
define config.has_autosave = True
define config.has_quicksave = True
    # These override existing config settings. They are here purely for dev convenience, and can be commented out if they are interfering with existing code


# [ INITIALISATION - UI ]
define layoutseparator = 5
    # The spacing between UI elements of the Playthrough save screen
define smallscreentextsize = 52
    # Hardcoded minimum text size for small screen devices such as smartphones
define slotheight = config.thumbnail_height
    # TODO: Test what happens to the layout if slotheight is greater or less than the thumbnail height
        # [EDIT:] As expected. Fix this; center the thumbnail if too big, compress it if it's too small.
define textcolor = gui.text_color
define hovercolor = gui.hover_color
define focuscolor = "#FFF"
define insensitivecolor = gui.insensitive_color
define interfacecolor = gui.interface_text_color
    # Optional overrides for certain gui elements


# [ UI CALIBRATION/DISPLAYABLES ]
init python:
    textsize = max(min(gui.text_size, 80), 20)
        # Clamp text size to sensible values
        # - TODO: Some games permit the player to change 'gui.text_size' via the Preferences screen, or via the Accessibility screen. Recalculate this if needed - probably inside a screen
    if renpy.variant("mobile") and textsize < smallscreentextsize:
        textsize = smallscreentextsize
        # Enlarge text size if player is using a small screen
    iconsize = (textsize, textsize)
        # This matches the icon sizes to the text size
            # TODO: This is likely obsolete - clean up
    yvalue = int(textsize * 1.5)
        # yvalue is used to line up the edges of various UI elements, primarily buttons which need extra space around the text to look good
    try:
        ColorizeMatrix
        # Test for the existence of 'ColorizeMatrix', without running it
    except NameError:
        slotforeground = renpy.displayable(Frame(pathoffset + "gui/emptyframe.png"))
        # ColorizeMatrix is not available. Use another form of focus highlighting e.g. Solid("#FFFFFF1F"), im. functions, etc. In this case, a white border
    else:
        slotforeground = renpy.displayable(Frame(Transform(pathoffset + "gui/emptyframe.png", matrixcolor = ColorizeMatrix(Color("#000"), Color(textcolor))))) # Match the UI color
        # This is what is shown over the top of the hovered/selected  slot, and can be any Displayable or None. Either hard-code it, or use a binding defined at a lower init level
        # - NOTE: Displayables are usually defined within a Frame in order to be scaled correctly, e.g. Frame("gui/nvl.png"). There are exceptions, such as Color() or Solid()
    symboltext = pathoffset + "gui/NotoSansSymbols2-Regular.ttf"
        # Locates a font file containing the glyphs we will use instead of image-based icons, below
            # To view glyphs: 1) Install the font (probably right-click the .ttf file -> Install), then 2) Visit https://fonts.google.com/noto/specimen/Noto+Sans+Symbols+2
    icon_viewplaythroughs = "{color=" + focuscolor + "}𝌮{/color}" if enable_iconcolors else "𝌮" # 𝌮
    icon_viewrenpypages   = "{color=" + focuscolor + "}𝌅{/color}" if enable_iconcolors else "𝌅" # 𝌅
    icon_newplaythrough   = "{color=" + "#00FF00" + "}🞤{/color}" if enable_iconcolors else "🞤" # 🞤
    icon_rename           = "{color=" + interfacecolor + "}🪶{/color}" if enable_iconcolors else "🪶" # 🪶
    icon_delete           = "{color=" + "#FF0000" + "}🞫{/color}" if enable_iconcolors else "🞫" # 🞫
    icon_locked           = "{color=" + "#FF0000" + "}🔒{/color}" if enable_iconcolors else "🔒" # ⚿
    icon_unlocked         = "{color=" + textcolor + "}🔓{/color}" if enable_iconcolors else "🔓" # ⚿
    icon_sortbyrecent     = "⭫"     # Alternates: ⏱ 🗓 🕰 ⌚ ⭫
    icon_sortbynumber     = "#"     # Alternates: 𝍸 #
    icon_sortbylocked     = "🔒"    # Alternates: 🔒
    icon_sortbyversion    = "⚠"     # Alternates: ⭭ 🗓 ⚠
default slotbackground = None
    # This is what is shown behind each slot, can be a Displayable (e.g. Frame("gui/nvl.png"), or Solid("000000CF")). Could be changed by ater code e.g. per screen
    # - NOTE: None is the default, removing the background, resulting in total transparency


# [ STYLING ]
    # TODO: Probably needs streamlining/cleanup after the change to glyphs from images - [EDIT:] *definitely* needs...
style fileslots:
    padding (0, 0)
    margin (0, 0)
style fileslots_text:
    outlines [(absolute(1), "#000", 0, 0)]
    size textsize
style fileslots_focus is fileslots_text:
    color focuscolor
style fileslots_button is fileslots:
    xminimum yvalue
    ysize yvalue
style selection_button is fileslots_button:
    selected_background textcolor
style icon_button is fileslots_button:
    hover_background textcolor
style fileslots_button_text is fileslots_text:
    insensitive_color insensitivecolor
    selected_color hovercolor
    hover_color hovercolor
    align (0.5, 0.5)
style selection_button_text is fileslots_button_text
style icon_text is fileslots_text:
    font symboltext
    align (0.5, 0.5)
    line_leading int(yvalue / 5)    # This line calibrates for this particular glyph font, and will likely need altering if another is used
style fileslots_frame is fileslots:
    xfill True
style fileslots_viewport is fileslots:
    xfill True
style fileslots_vscrollbar:
    unscrollable "hide"


# [ TRANSFORMS ]
transform marquee(t=10.0):
    subpixel True
    xanchor 0.0 xpos 1.0
    linear t xanchor 1.0 xpos 0.0
    repeat

transform hovermarquee(t=2.5, xpos=0.5, xanchor=0.5):
    on hover:
        xpos xpos xanchor xanchor
        linear t xanchor 1.0 xpos 0.0
        xanchor 0.0 xpos 1.0
        linear t xpos xpos xanchor xanchor
        repeat
    on idle:
        xanchor xanchor xpos xpos
        #linear t/5 xpos xpos xanchor xanchor


# [ CLASSES ]
# TODO: These will need docstrings, apparently?
init python:
    # Reference: (https://www.renpy.org/doc/html/save_load_rollback.html#save-functions-and-variables)
    class Playthrough:
        def __init__(self, name=None):
            # Constructor - defines and initialises the new object properly
            # - WARNING: New instances of this object are created frequently, albeit assigned to the same variable. I'm going to assume the garbage collector frees up previously allocated memory
            # NOTE: I may need to find a way to determine if this is happening correctly. Failing that, I expect that there is a way to explicitly release the previous object
                # [EDIT:] I read this (https://stackify.com/python-garbage-collection/). This suggests I don't need to worry about it, and provides a profiler should I feel the need to check
            if name == None:
                raise Exception("Invalid argument - object '{self}' of class 'Playthrough': __init__([required] name=string)")
            self.name = name
            self.slots = self.GetSlots()
            self.lockcount = [slot[5] for slot in self.slots].count("LOCKED")
            self.higherversioncount = [True if slot[3].lower() > config.version.lower() else False for slot in self.slots].count(True)
            self.SortSlots()

        def GetSlots(self):
            # This needs to return a list of lists, where each sublist contains all the data about the slot except the thumbnail. This is so that we can use both indices and list comprehension
            # Populate the slotslist by using a 'regex'. 'Regex' is short for "regular expression". It defines rules for extracting wanted data out of a pile of it
            # - This particular regex says that we want matches that: "^"(begins with) + (self.name(the name field of this object) + "-"(to avoid unwanted partial matches))
            files, slots = renpy.list_saved_games("^" + self.name + "-", fast=True), []
            # - We need a slot structure:
            #   - Filename          : Full string as used by Ren'Py file functions
            #   - Last modified     : UNIX epoch offset     - WARNING: Ren'Py file renaming preserves the OS timestamp on Windows. It may not on other systems
            #   - Slot number       : 1-99999, zero-padded 5-character string. If this slot number is exceeded, the "+ New Save +" button is not shown
                                    # [REOPENED] Perhaps set this as a dev-controlled magnitude option? They may want to limit it to 10, 100, 1000, etc.
                                    #  - [EDIT:] If desired, they can handle it
                                            # TODO: Or I could stop being lazy and rewrite this so that: zero-padding is not a thing; slots are infinite; max() and .SortSlots() use ints, not strings
            #   - Version number    : The version number of the game when the file was last properly saved (as opposed to renamed)
            #   - Editable name     : What the player sees. It defaults to Playthrough Name + Slot Number
            #   - Locked status     : A string. Code currently assigns meaning to "LOCKED" or "", nothing else
            # - With this in place, our code references the list (with the exception of the thumbnail). Every change to filename subdata must be reflected to the disk file immediately
            for file in files:
                subdata = file.split("-")
                if (self.name == "auto" or self.name == "quick"):
                    slots.append([file, renpy.slot_mtime(file), subdata[1], "", FileSaveName(file, empty="", slot=True), ""])
                else:
                    slots.append([file, renpy.slot_mtime(file)] + subdata[1:])
            # Pass the data back to the calling expression
            return slots

        def SortSlots(self, reverse=True):
            # Strip any existing slots that have a filename that is "+ New Save +", because we cannot assume that we're dealing with a slotslist that has not already been sorted
            # - NOTE: This doesn't appear to be necessary. I don't know why? - [EDIT:] There is other code that shouldn't work, and does. I think it's just the way Ren'Py handles stuff internally
            # Sort the slots in (reverse) order according to the value of 'persistent.sortby':
            # - NOTE: The '.sort()' method mutates the original list, making changes in place
            slotkeys = ["filename", "lastmodified", "slotnumber", "versionnumber", "editablename", "lockedstatus"]
            # ... Since "auto"/"quick" saves are performed cyclically, sorting by "lastmodified" is the same as sorting by "slotnumber" would be for Playthrough slotlists
            sortby = "lastmodified" if (self.name == "auto" or self.name == "quick") else persistent.sortby
            # ... Default to "lastmodified" if the requested 'sortby' cannot be found in 'slotkeys[]', and store the index of the required key
            sortkey = slotkeys.index(sortby) if sortby in slotkeys else slotkeys.index("lastmodified")
            # ... Perform the sort. The '.sort()' method uses a lambda to find the key data to sort against for each item(list of slot details) in the iterable(list of slots)
            # - NOTE: lambdas are disposable anonymous functions that use (an) input(s) to derive a required output. More here: (https://www.w3schools.com/python/python_lambda.asp)
            if sortby in ("versionnumber","lockedstatus"):
                reverse = False
                # TODO: Fix kludgey override above and make the button call the function with parameters - [EDIT:] "Function(viewingpt.SortSlots, reverse=False)" not working
            self.slots.sort(reverse=reverse, key=lambda x: x[sortkey])
            # If appropriate, add slots that define "+ New Save +" slots by position. Since "auto"/"quick" are hard-sorted by "lastmodified", this will not affect those 'playthrough's
            i = slotkeys.index("slotnumber")
            if sortby == "slotnumber" and len(self.slots) > 1:
                # We've already sorted the list, so run through it backwards and insert "+ New Save +" slots where needed
                # - NOTE: Going backwards preserves the indices of yet-to-be-checked slots, because any newly-inserted slots are increasing the length of the list even as we step through it
                span = len(self.slots) - 1
                for slot in range(span, 0, -1):
                    lower, upper = self.slots[slot][i], self.slots[slot - 1][i]
                    # Dodge 'int()' crashing over a non-decimal string (including an empty one)
                    if not lower.isdecimal() or not upper.isdecimal():
                        raise Exception("'lower' or 'upper' was not decimal ({} or {}) while inserting intermediate \"+ New Save +\" slot(s) in {}.SortSlots()".format(lower, upper, self.name))
                    lower, upper = int(lower), int(upper)
                    if upper-lower == 2:
                        # There is a single-slot gap here
                        # - NOTE: Since this field may be checked by 'max()' later, we need the string in the same zero-padded, five-wide format that all the of the other slotnumbers are in
                            # TODO: Fix this as specified in 'Playthrough.GetSlots()', above
                        self.slots.insert(slot, ["+ New Save +", "", "{:05}".format(lower + 1), "", "", ""])
                    elif upper-lower > 2:
                        # There is a multi-slot gap here; store the range (as integers) in the 'lastmodified' and 'versionnumber' fields
                        self.slots.insert(slot, ["+ New Save +", lower + 1, "", upper - 1, "", ""])
            # Finally, insert a "+ New Save +" slot at the beginning of the list - unless we're in "auto"/"quick", or the new slot number would be 10000+
            if self.name != "auto" and self.name != "quick":
                # Find the highest slotnumber there currently is, and add 1. Insert this "+ New Save +" slot at the beginning of the list
                slotnumbers = [slot[i] for slot in self.slots]
                # Dodge 'max()' crashing over an empty list...
                slotnumber = max(slotnumbers) if slotnumbers != [] else "0"
                # Dodge 'int()' crashing over a non-decimal or empty string...
                # TODO: Since this type of check gets performed a lot, consider writing a multipurpose safety-check function for type conversions
                if not slotnumber.isdecimal():
                    raise Exception("'slotnumber' was not decimal ({}) while inserting topmost \"+ New Save +\" slot in {}.SortSlots()".format(slotnumber, self.name))
                slotnumber = int(slotnumber) + 1
                # Dodge slot numbers requiring more than five characters...
                    # TODO: This check will become obsolete once we've done away with the five-character-width requirement. Get rid of it, once that is done
                if slotnumber < 10000:
                    self.slots.insert(0, ["+ New Save +", "", "{:05}".format(slotnumber), "", "", ""])


# [ FUNCTIONS ]
init -1 python:
    def ResetPtVars(timeline=1.0):
        # This is a dummy transition timeline function that instantly returns as complete. The entire purpose is to reset the playthrough variables
        # TODO: This should be altered so that it still performs the function of whatever transition was in place before we hijacked it - learn how
        global viewingptname, viewingpt
        userinput, targetaction, viewingptname, viewingpt, slotdetails = "", "", "", [], []
        return 1.0

    def MakePtLast():
        # Check there is only one copy of 'viewingptname' in the persistent list. If so, delete it and append a new version to the end of the list. If not, throw a bug-checking exception
        # - NOTE: Don't bother if we are viewing "auto" or "quick"
        global viewingptname
        if viewingptname != "auto" and viewingptname != "quick":
            if persistent.playthroughslist.count(viewingptname) != 1:
                raise Exception("Error: {} one copy of playthrough \"{}\" in the persistent list".format("Less than" if persistent.playthroughslist.count(viewingptname) < 1 else "More than", viewingptname))
            persistent.playthroughslist.remove(viewingptname)
            persistent.playthroughslist.append(viewingptname)

    def ReflectSlotChanges():
        # This accesses 'slotdetails' as a list of slot details, then checks that the original file exists; if so, it builds a new filename, renames it, then updates the data in 'viewingpt'
        # - [EDIT:] No need to update the data in 'viewingpt', nor to reload it. Apparently, even this data is adjusted through the magic of Ren'Py's python abstraction /shrug Cheers, PyTom!
        global slotdetails, viewingptname
        if renpy.can_load(slotdetails[0]) == False:
            raise Exception("Error: File \"{}\" does not exist".format(slotdetails[0]))
        newfilename = viewingptname
        for subdata in slotdetails[1:]:
            if subdata: newfilename += "-" + subdata
        if slotdetails[0] != newfilename:
            renpy.rename_save(slotdetails[0], newfilename)
        slotdetails = []

    def DeletePlaythrough():
        # This deletes all of the files in 'viewingpt', then removes 'viewingptname' from 'persistent.playthroughslist', then calls 'ResetPtVars()' to clear the current viewing details
        global viewingptname, viewingpt
        # Reload the playthrough, to be sure of having current and unmodified information
        viewingpt.slots = viewingpt.GetSlots()
        for slot in viewingpt.slots:
            if renpy.can_load(slot[0]) == False:
                raise Exception("Error: File \"{}\" does not exist".format(slot[0]))
            renpy.unlink_save(slot[0])
        if persistent.playthroughslist.count(viewingptname) != 1:
            raise Exception("Error: {} one copy of Playthrough \"{}\" in the persistent list".format("Less than" if persistent.playthroughslist.count(viewingptname) < 1 else "More than", viewingptname))
        persistent.playthroughslist.remove(viewingptname)
        ResetPtVars()

    def AwaitUserInput():
        # This is an all-purpose function that is called whenever user-input is required to progress with an Action list; it defers the changes to be made until there is actually an input
        # - NOTE: I don't know how to make an action list wait for input and then resume; this is a workaround that calls this function once per screen update... I think
            # TODO: Figure out if "call in new context" is the designed solution to this problem, and how to achieve it
        global userinput, targetaction, viewingptname, viewingpt, slotdetails
        # The first thing to do is quit out unless there is something that actually needs processing
        if userinput:
            # Be sure we're dealing with a string. Pretty much anything will convert to a string - even objects. Also, using 'str()' on a string does not throw an exception, which is nice
            userinput = str(userinput)
            if targetaction == "newplaythroughname":
                # Make the new playthrough current, then add it to the end of the persistent list. Update the viewed playthrough to the new one.
                viewingptname = userinput
                persistent.playthroughslist.append(viewingptname)
                viewingpt = Playthrough(name=viewingptname)
            elif targetaction == "changeplaythroughname":
                # This updates 'viewingptname', then renames all of the files in 'viewingpt' via 'ReflectSlotChanges()', then updates 'viewingptname' in 'persistent.playthroughslist'
                viewingpt.slots = viewingpt.GetSlots()
                oldptname = viewingptname
                viewingptname = userinput
                for slot in viewingpt.slots:
                    slotdetails = slot
                    slotdetails.pop(1)
                    slotdetails[3] = slotdetails[3].replace(oldptname, viewingptname)
                    ReflectSlotChanges()
                if persistent.playthroughslist.count(oldptname) != 1:
                    raise Exception("Error: {} one copy of Playthrough \"{}\" in the persistent list".format("Less than" if persistent.playthroughslist.count(oldptname) < 1 else "More than", oldptname))
                persistent.playthroughslist[persistent.playthroughslist.index(oldptname)] = viewingptname
                viewingpt = Playthrough(name=viewingptname)
            elif targetaction == "newslotnumber":
                # This saves the new file if not already existent, then updates the playthrough list order
                filename = "{0}-{1:05}-{2}-{0} {1}-Unlocked".format(viewingptname, int(userinput) if userinput.isdecimal() else userinput, config.version)
                if renpy.can_load(filename):
                    raise Exception("Error: File \"{}\" already exists".format(filename))
                renpy.save(filename)
                MakePtLast()
            elif targetaction == "changeslotname":
                # Update 'slotdetails' with 'userinput', then reflect any changes to the relevant disk file
                slotdetails[3] = userinput
                ReflectSlotChanges()
            else:
                raise Exception("Error: 'userinput' ({}) sent to an invalid 'targetaction' ({})".format(userinput, targetaction))
            userinput, targetaction, = "", ""


# [ SCREENS ]
screen switchbutton(xpos=0.0, ypos=0.0):
    # Provide a button to switch to the Playthroughs save system
    button:
        tooltip "Switch to the Playthrough system"
        style_prefix "icon"
        pos (xpos, ypos)
        text icon_viewplaythroughs
        action SetVariable("persistent.save_system", "playthrough")

# The original save/load system screen, modified by OscarSix to simply be a wrapper for either of the screens used, below:
screen file_slots(title):
    # TODO: Metrics may need to be tested for and adjusted here, in case people have altered the text size via Preferences or Accessibility. This may require 'gui.rebuild()', which would suck
    style_prefix "fileslots"
    if persistent.save_system == "original":
        use original_file_slots(title=title)
        use switchbutton(0.25, 0.18)    # This places the icon outside the proper panel; position references the entire screen. This will show regardless of Dev version of original_file_slots()
    elif persistent.save_system == "playthrough":
        use playthrough_file_slots(title=title)
    else:
        $ raise Exception("Error: Invalid persistent.save_system - \"{}\"".format(persistent.save_system))

# Our/the game Dev's version of the original save/load screen
screen original_file_slots(title):
    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))
    use game_menu(title):
        fixed:
            #use switchbutton()    # This places the icon inside the proper panel; position references it. Dev can use this inside their own screen
            ## This ensures the input will get the enter event before any of the buttons do.
            order_reverse True
            ## The page name, which can be edited by clicking on a button.
            button:
                style "page_label"
                key_events True
                xalign 0.5
                action page_name_value.Toggle()
                input:
                    style "page_label_text"
                    value page_name_value
            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"
                xalign 0.5
                yalign 0.5
                spacing gui.slot_spacing
                for i in range(gui.file_slot_cols * gui.file_slot_rows):
                    $ slot = i + 1
                    button:
                        action FileAction(slot)
                        has vbox
                        add FileScreenshot(slot) xalign 0.5
                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"
                        text FileSaveName(slot):
                            style "slot_name_text"
                        key "save_delete" action FileDelete(slot)
            # Collect and display any active tooltip on this page
            $ help = GetTooltip()
            if help:
                text help style "fileslots_focus" italic True size gui.interface_text_size xalign 0.5 yalign 0.9
            ## Buttons to access other pages.
            hbox:
                style_prefix "page"
                xalign 0.5
                yalign 1.0
                spacing gui.page_spacing
                textbutton _("<") action FilePagePrevious()
                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto")
                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick")
                ## range(1, 10) gives the numbers from 1 to 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)
                textbutton _(">") action FilePageNext()

# The new playthrough system
screen playthrough_file_slots(title):
    python:
        # Make sure we're accessing the global variables
        global viewingptname, viewingpt
        # Check the validity of the playthrough name that we're viewing. If invalid, find the latest valid name. If none found, set 'viewingptname' to an empty string
        if ((config.has_autosave and viewingptname == "auto") or (config.has_quicksave and viewingptname == "quick") or (persistent.playthroughslist and viewingptname in persistent.playthroughslist)) == False:
            viewingptname = persistent.playthroughslist[-1] if persistent.playthroughslist else ""
        # Populate the viewed playthrough if 'viewingptname' is not an empty string - otherwise set it to None
        viewingpt = Playthrough(name=viewingptname) if viewingptname else None
    use game_menu(title):
        style_prefix "fileslots"
        # By using 'side' in this manner, we put any tooltips in a strip across the top of the container we're in, and everything else in the center (below)
        # - Because of the way in which side calculates its layout (center last), subcontainers get accurate metrics with which to handle their own calculations, dodging some viewport issues
        side "t c":
            # Top tooltip, displayed above everything else.
                # TODO: scroll only if contents outsize the container. Currently: Always scrolls
            fixed:
                ysize yvalue
                at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)     # Display only what is inside the container
                # Collect and display any active tooltip on this page
                $ help = GetTooltip()
                if help:
                    text help:
                        style "fileslots_focus"
                        layout "nobreak"
                        italic True
                        at marquee
            # Two panels, side-by-side in an hbox: Playthroughs and Slots
            hbox:
                spacing 60
                # Playthroughs panel
                vbox:
                    xsize 0.33
                    # This header and the panel below it are offset slightly to the left, to compensate for the width and spacing of the vertical scrollbar in the viewport below them
                    text "Playthroughs":
                        color interfacecolor
                        size gui.label_text_size
                        xalign 0.5
                        xoffset -round((gui.scrollbar_size + layoutseparator) / 2)
                    null height layoutseparator
                    # Display top panel, which contains 1-4 buttons
                    hbox:
                        ysize yvalue
                        xalign 0.5
                        xoffset -round((gui.scrollbar_size + layoutseparator) / 2)
                        # Provide a button to switch to the original save system
                        button:
                            tooltip "Switch to the Ren'Py [title] system"
                            style_prefix "icon"
                            text icon_viewrenpypages
                            action SetField(persistent, "save_system", "original")
                        if config.has_autosave:
                            textbutton  _("{#auto_page}A"):
                                tooltip "Show Autosaves"
                                style_prefix "selection"
                                action [SetVariable("viewingptname", "auto"),
                                        SetVariable("viewingpt", Playthrough(name="auto"))]
                        if config.has_quicksave:
                            textbutton _("{#quick_page}Q"):
                                tooltip "Show Quicksaves"
                                style_prefix "selection"
                                action [SetVariable("viewingptname", "quick"),
                                        SetVariable("viewingpt", Playthrough(name="quick"))]
                        # If we're on the Save screen, provide a button to allow the creation of a new, uniquely-named, playthrough that is also not simply a number (Ren'Py Pages)
                        if title == "Save":
                            button:
                                tooltip "Create a new Playthrough"
                                style_prefix "icon"
                                text icon_newplaythrough
                                action [SetVariable("targetaction", "newplaythroughname"),
                                        Show("querystring", query="{color=" + interfacecolor + "}Please give this Playthrough a unique name:{/color}", excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots", tcolor=focuscolor),
                                        AwaitUserInput()]
                    null height layoutseparator
                    # Vertically-scrolling viewport for the list of Playthroughs
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        spacing layoutseparator
                        vbox:
                            for i in range(len(persistent.playthroughslist) - 1, -1, -1):
                                # Using a side allows us to use xfill True or xsize 1.0 for the central button, without compromising the size of any end buttons or having to calculate around them
                                # NOTE: Square-bracket string interpolation cannot be meaningfully used with a binding used to hold the return from '__next__()'; they will all show the last value
                                side "l c r":
                                    # Rename button at the left, if we're dealing with the selected playthrough
                                    button:
                                        xysize (yvalue, yvalue)
                                        action None # Start with an empty, SIZED button and no action, then populate it if it's the current playthrough AND the functionality has not been diasbled
                                        if enable_renaming and persistent.playthroughslist[i] == viewingptname:
                                            tooltip "Rename the \"{}\" Playthrough".format(viewingptname)
                                            style_prefix "icon"
                                            text icon_rename
                                            action [SetVariable("targetaction", "changeplaythroughname"),
                                                    Show("querystring", query="{color=" + interfacecolor + "}Please give this Playthrough a unique name:{/color}", preload=viewingptname, excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots", tcolor=focuscolor),
                                                    AwaitUserInput()]
                                    # Playthrough selection button in the center
                                    button:
                                        tooltip "Show Slots in the \"{}\" Playthrough".format(persistent.playthroughslist[i])
                                        style "selection_button"
                                        xysize (1.0, yvalue)
                                        at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)     # This keeps the contents inside the box by cropping anything outside of it off
                                        text " {} ".format(persistent.playthroughslist[i]):
                                            layout "nobreak"
                                            hover_color hovercolor
                                            color (hovercolor if persistent.playthroughslist[i] == viewingptname else textcolor)
                                            at hovermarquee
                                        action [SetVariable("viewingptname", persistent.playthroughslist[i]),
                                                SetVariable("viewingpt", Playthrough(name=persistent.playthroughslist[i]))]
                                    # Delete button at the right, if we're dealing with the selected playthrough
                                    button:
                                        xysize (yvalue, yvalue)
                                        action None # As above
                                        if persistent.playthroughslist[i] == viewingptname:
                                            tooltip "Delete the \"{}\" Playthrough".format(viewingptname)
                                            style_prefix "icon"
                                            text icon_delete
                                            action Confirm("Are you sure you want to delete this Playthrough?\n{}{}".format("{size=" + str(gui.notify_text_size) + "}{color=" + str(insensitivecolor) + "}\nLocked Slots: " + str(viewingpt.lockcount) + "{/color}{/size}" if viewingpt.lockcount else "", "{size=" + str(gui.notify_text_size) + "}{color=" + str(insensitivecolor) + "}\nSlots from a later version: " + str(viewingpt.higherversioncount) + "{/color}{/size}" if viewingpt.higherversioncount else ""), yes=Function(DeletePlaythrough), confirm_selected=True)
# >>>   \/ \/ \/ REMOVE FROM FINAL BUILD!!! \/ \/ \/   <<<
                            # Test playthroughs for layout verification - Status: CURRENT, GOOD
                            if testplaythroughlistsize:
                                for i in range(1, 51, 1):
                                    side "l c r":
                                        button:
                                            xysize (yvalue, yvalue)
                                            action None
                                            if enable_renaming:
                                                tooltip "Rename the \"{}\" Playthrough".format(i)
                                                style_prefix "icon"
                                                text icon_rename
                                                action NullAction()
                                        button:
                                            tooltip "Show Slots in the \"{}\" Playthrough".format(i)
                                            style "selection_button"
                                            xysize (1.0, yvalue)
                                            at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)
                                            text " {} ".format(i):
                                                layout "nobreak"
                                                hover_color hovercolor
                                                selected_color hovercolor
                                                color textcolor
                                                at hovermarquee
                                            action NullAction()
                                        button:
                                            xysize (yvalue, yvalue)
                                            action None
                                            if True:
                                                tooltip "Delete the \"{}\" Playthrough".format(i)
                                                style_prefix "icon"
                                                text icon_delete
                                                action NullAction()
# >>>   /\ /\ /\ END REMOVAL SECTION /\ /\ /\   <<<
                # Fileslots panel
                vbox:
                    # Header
                    xfill True
                    text "Slots":
                        color interfacecolor
                        size gui.label_text_size
                    null height layoutseparator
                    # Provide (or not) buttons that alter the key that the slotslist is sorted on
                    if enable_sorting and viewingptname and viewingptname != "auto" and viewingptname != "quick":
                        hbox:
                            # TODO: Streamline styling... again
                            ysize yvalue
                            text "Sort by: "
                            button:
                                tooltip "Sort slots by most recently changed first"
                                style_prefix "icon"
                                selected_background textcolor
                                hover_background None
                                text icon_sortbyrecent:
                                    hover_color hovercolor
                                    selected_color hovercolor
                                action [SetVariable("persistent.sortby", "lastmodified"),
                                        viewingpt.SortSlots]
                            button:
                                tooltip "Sort slots by highest slot number first"
                                style_prefix "icon"
                                selected_background textcolor
                                hover_background None
                                text icon_sortbynumber:
                                    hover_color hovercolor
                                    selected_color hovercolor
                                action [SetVariable("persistent.sortby", "slotnumber"),
                                        viewingpt.SortSlots]
                            if enable_locking:
                                button:
                                    tooltip "Sort slots by showing locked slots first"
                                    style_prefix "icon"
                                    selected_background textcolor
                                    hover_background None
                                    text icon_sortbylocked:
                                        hover_color hovercolor
                                        selected_color hovercolor
                                    action [SetVariable("persistent.sortby", "lockedstatus"),
                                            viewingpt.SortSlots]
                            if enable_versioning:
                                button:
                                    tooltip "Sort slots by lowest version number"
                                    style_prefix "icon"
                                    selected_background textcolor
                                    hover_background None
                                    text icon_sortbyversion:
                                        hover_color hovercolor
                                        selected_color hovercolor
                                    action [SetVariable("persistent.sortby", "versionnumber"),
                                            viewingpt.SortSlots]
                        null height layoutseparator
                    # Vertically-scrolling viewport for the slotslist
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        spacing layoutseparator # This separates the slots from the scrollbar
                        vbox:
                            spacing layoutseparator
                            # Display all the fileslots that are in the playthrough being viewed, keyed off 'viewingptname'. If no playthrough is being viewed, display nothing
                            if viewingptname != "":
                                # For each slot in the Playthrough...
                                for slot in viewingpt.slots:
                                    # ...deconstruct the list...
                                    python:
                                        filename, lastmodified, slotnumber, versionnumber, editablename, lockedstatus = slot
                                        slotnumber = int(slotnumber) if slotnumber.isdecimal() else 0 # TODO: This needs proper error handling, as do other instances of this
                                        slotname = editablename if enable_renaming and editablename else "{} {}".format(viewingptname, slotnumber if slotnumber else "[[{} to {}]".format(lastmodified, versionnumber))
                                        slottextcolor = textcolor # Reset this each time, since the last time through might have made it 'insensitivecolor'
                                    # ...and turn it into a slotbutton with details and sub-buttons
                                    # Handle any slot which has been inserted into the list for the purpose of creating a new save, and therefore is not yet a disk file:
                                    if filename == "+ New Save +":
                                        # Only produce the button if we're on the Save screen
                                        # - NOTE: "auto"/"quick" 'playthrough's will not have been given any "+ New Save +" slots, so they *shouldn't* ever reach this code...
                                        if title == "Save":
                                            textbutton "+ New Save +":
                                                tooltip "Create a new save: {}".format(slotname)
                                                xysize (1.0, slotheight)
                                                text_align (0.5, 0.5)
                                                background slotbackground
                                                hover_foreground slotforeground
                                                action [SetVariable("targetaction", "newslotnumber"),
                                                        If(slotnumber, true=SetVariable("userinput", slotnumber), false=Show("querynumber", query="{color="+interfacecolor+"}Please select a slot number:{/color}", preload=str(lastmodified), minval=lastmodified, maxval=versionnumber, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots", tcolor=focuscolor)),
                                                        AwaitUserInput()]
                                    # Disable any slot that has a version number higher than this app; loading will likely fail and overwriting will likely lose data
                                    # TODO: This doesn't actually need to be a button. It might or might not be simpler for it not to be.
                                    # - NOTE: In theory, 'versionnumber' could be type int. However, that should only happen if 'filename' == "+ New Save +" - which is already handled, above
                                    #   - TODO: I'd be happier if we weren't using variables for more than one purpose. Look into restructuring 'slot'
                                    elif versionnumber.lower() > config.version.lower():
                                        if enable_versioning:
                                            textbutton "{} - Version {}".format(editablename, versionnumber):
                                                sensitive False
                                                xysize (1.0, slotheight)
                                                text_align (0.5, 0.5)
                                                background slotbackground
                                                action None
                                    # Everything else should all be pre-existing disk files that need to be shown
                                    else:
                                        button:
                                            # TODO: Setting up the inside of this button - all slot buttons - may help fix the Roald Dahl problem, and possibly make the UI faster/more elegant
                                            tooltip "{} {}".format("Load" if title == "Load" else "Overwrite", slotname)
                                            xysize (1.0, slotheight)
                                            background slotbackground
                                            hover_foreground slotforeground
                                            action [MakePtLast,
                                                    If(title == "Save", false=FileLoad(filename, slot=True), true=FileSave("{}-{:05}-{}-{}-Unlocked".format(viewingptname, slotnumber, config.version, editablename) if viewingptname != "auto" and viewingptname != "quick" else "{}-{}".format(viewingptname, slotnumber), slot=True))]
                                            if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                                key "save_delete" action FileDelete(filename, slot=True)
                                            if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                                tooltip "{} {}".format("Attempt to load" if title == "Load" else "Overwrite", slotname)
                                            if title == "Save" and (viewingptname == "auto" or (enable_locking and lockedstatus == "LOCKED")):
                                                sensitive False
                                                $ slottextcolor = insensitivecolor
                                                    # TODO: Test if needed, since we're already setting "sensitive False" - but may be needed to comply with color overrides at top
                                            hbox:
                                                # Thumbnail on the left. Setting it as a background to a frame permits regular content to appear overlaid, if needed
                                                frame:
                                                    xysize (config.thumbnail_width, slotheight) # TODO: This will result in bad positioning if slotheight != config.thumbnail_height. Fix it.
                                                    background FileScreenshot(filename, slot=True)
                                                    # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                                                    if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                                        add Solid("#000000CF")
                                                        vbox:
                                                            at truecenter
                                                            text "- Older Save -":
                                                                style "fileslots_focus"
                                                                size gui.slot_button_text_size
                                                                xalign 0.5
                                                            null height gui.slot_button_text_size
                                                            text "v{}".format(versionnumber):
                                                                style "fileslots_focus"
                                                                size gui.slot_button_text_size
                                                                xalign 0.5
                                                null width layoutseparator
                                                viewport:
                                                    scrollbars "vertical"
                                                    mousewheel "change"
                                                    align (0.5, 0.5)
                                                    xmaximum 0.98
                                                    ymaximum 0.99
                                                    vbox:
                                                        align (0.5, 0.5)
                                                        xfill True # TODO: Check to see if this solves the Roald Dahl problem
                                                        viewport:
                                                            # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
                                                            edgescroll (100, 500) #mousewheel "horizontal-change"
                                                            xfill False # TODO: Check to see if this solves the Roald Dahl problem
                                                            align (0.5, 0.5)
                                                            text "{}".format(slotname):
                                                                color slottextcolor
                                                                align (0.5, 0.5)
                                                                text_align 0.5
                                                                layout "subtitle"
                                                        null height layoutseparator
                                                        text "{}".format(FileTime(filename, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True)):
                                                            xalign 0.5
                                                            size gui.slot_button_text_size
                                                            color slottextcolor
                                                        null height layoutseparator
                                                        # Icon buttons
                                                        hbox:
                                                            xalign 0.5
                                                            # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                                                            if enable_renaming and editablename and (enable_locking == False or (enable_locking and lockedstatus != "LOCKED")):
                                                                button:
                                                                    tooltip "Rename {}".format(slotname)
                                                                    style_prefix "icon"
                                                                    text icon_rename
                                                                    action [SetVariable("targetaction", "changeslotname"),
                                                                            SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, lockedstatus]),
                                                                            Show("querystring", query="{color="+interfacecolor+"}Please enter the slot name:{/color}", preload=editablename, excludes="[{<>:\"/\|?*-", maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots", tcolor=focuscolor),
                                                                            AwaitUserInput()]
                                                            if enable_locking and lockedstatus:
                                                                button:
                                                                    tooltip "{} {}".format("Unlock" if lockedstatus == "LOCKED" else "Lock", slotname)
                                                                    style_prefix "icon"
                                                                    text (icon_locked if lockedstatus == "LOCKED" else icon_unlocked)
                                                                    # .format("{image=icon_locked}" if lockedstatus == "LOCKED" else "{image=icon_unlocked}")
                                                                    action [SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, "Unlocked" if lockedstatus == "LOCKED" else "LOCKED"]),
                                                                            ReflectSlotChanges]
                                                            if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                                                button:
                                                                    tooltip "Delete {}".format(slotname)
                                                                    style_prefix "icon"
                                                                    text icon_delete
                                                                    action FileDelete(filename, slot=True)


# [ ADDITIONAL SCREENS ]

# { SUPPORT SCREEN } - Provides the query_ screens with a degree of wrapping
# - container     : [optional] : an (x, y, xsize, ysize) tuple specifying the area that the input box will be centered in
# - bground       : [optional] : a Displayable for the background property of the largest non-transparent Frame(), which will be scaled to fit
# - query         : [optional] : a string containing the question to put to the player
screen queryframe(container=(0, 0, config.screen_width, config.screen_height), bground=None, query="Hmm?"):
    frame:
        area container
        background "gui/overlay/confirm.png"
        frame:
            at truecenter
            background bground
            xfill False
            yfill False
            padding (50, 50)
            frame:
                at truecenter
                xfill False
                yfill False
                vbox:
                    text query:
                        xalign 0.5
                        size gui.label_text_size
                    transclude

# { SUPPORT SCREEN } - Tacks Confirm/Cancel buttons onto the bottom of whatever called it, and sets 'variable' to 'newvalue' if Confirm is clicked. Both buttons will Hide() 'callingscreen'
# - Both 'variable' and 'callingscreen' are REQUIRED; 'newvalue' and 'isvalid' are [optional]
screen ccframe(callingscreen=None, variable=None, newvalue=None, isvalid=True):
    if variable is None or callingscreen is None:
        $ raise Exception("Invalid argument - screen ccframe([required] variable=\"variable_name\" and callingscreen=\"screen_name\"):")
    null height gui.text_size
    hbox:
        xalign 0.5
        null width gui.text_size
        textbutton "Confirm":
            size_group "ccbuttons"
            text_align (0.5, 0.5)
            if isvalid == False:
                sensitive False
            action (SetVariable(variable, newvalue), Hide(callingscreen))
        null width gui.text_size
        textbutton "Cancel":
            size_group "ccbuttons"
            text_align (0.5, 0.5)
            action Hide(callingscreen)
        null width gui.text_size
        key "game_menu" action Hide(callingscreen)

# { SUPPORT SCREEN } - Adds a box to the middle of a container, offering a text field to the player and storing the result in a specified variable. Designed for strings
# - query         : [optional] : Passed to screen queryframe() - a string containing the box title/a question to put to the player
# - preload       : [optional] : a string that initially populates the input field
# - excludes      : [optional] : a string passed to the input field that contains forbidden characters. Not usually used; must contain "[{" if it is  - WARNING: This is not checked!
# - invalid       : [optional] : a list containing invalid responses; if currentstring is in the list, the 'isvalid' flag is set to False
# - maxcharlen    : [optional] : an integer passed to the input field specifying the maximum character length of the response string
# - maxpixelwidth : [optional] : an integer passed to the input field specifying the maximum size of the response string in pixels, when rendered using the input style
# - variable      :  REQUIRED  : Passed to screen ccframe() - a string containing the name of the GOBAL variable that will store the result
# - container     : [optional] : Passed to screen queryframe() - an (x, y, xsize, ysize) tuple specifying the area that the input box will be centered in
# - bground       : [optional] : Passed to screen queryframe() - a Displayable for the background property of the largest non-transparent Frame(), which will be scaled to fit
# - styleprefix   : [optional] : a string containing the style_prefix to apply to the whole box, including any children
# - tcolor        : [optional] : a Color object (e.g. "#F00") for the text in the input field. This will override the default/specified styling
screen querystring(query="Hmm?", preload="", excludes="[{", invalid=[], maxcharlen=None, maxpixelwidth=None, variable=None, container=(0, 0, config.screen_width, int(config.screen_height * 0.5) if renpy.variant("mobile") else config.screen_height), bground=None, styleprefix=None, tcolor=None):
    style_prefix styleprefix
    if variable is None:
        $ raise Exception("Invalid argument - screen querystring([required] variable=\"variable_name\"):")
    modal True
    default currentstring = preload
    use queryframe(container=container, bground=bground, query=query):
        if excludes != "[{":
            text "Forbidden characters: [excludes!q]":
                xalign 0.5
                size gui.notify_text_size
                color gui.insensitive_color
        null height gui.text_size
        input:
            value ScreenVariableInputValue("currentstring", default=True, returnable=False)
            default preload
            exclude excludes
            length maxcharlen
            pixel_width maxpixelwidth
            xalign 0.5
            if tcolor is not None:
                color tcolor
        # Assume validity unless tested otherwise
        python:
            global targetaction
            isvalid = bool(currentstring)
                # Empty strings are not valid
            if isvalid:
                # Conditional invalidation based on purpose of input can go here:
                if currentstring.isdecimal():
                    if targetaction in ("newplaythroughname", "changeplaythroughname"):
                        isvalid = False
                            # If 'targetaction' is "newplaythroughname" or "changeplaythroughname", we need to prevent it from being an integer (because these are Ren'Py save system Page names)
                elif invalid:
                    if currentstring in invalid:
                        isvalid = False
                            # Since Playthrough names must be unique, it is invalid if it already exists in the list
        use ccframe(callingscreen="querystring", variable=variable, newvalue=currentstring, isvalid=isvalid)

# { SUPPORT SCREEN } - Adds a box to the middle of a container, offering a text field to the player and storing the result in a specified variable. Designed for numbers
# - query         : [optional] : Passed to screen queryframe() - a string containing the box title/a question to put to the player
# - preload       : [optional] : a string that initially populates the input field
# - minval        : [optional] : the minimum number that is considered valid
# - maxval        : [optional] : the maximum number that is considered valid
# - variable      :  REQUIRED  : Passed to screen ccframe() - a string containing the name of the GLOBAL variable that will store the result
# - container     : [optional] : Passed to screen queryframe() - an (x, y, xsize, ysize) tuple specifying the area that the input box will be centered in
# - bground       : [optional] : Passed to screen queryframe() - a Displayable for the background property of the largest non-transparent Frame(), which will be scaled to fit
# - styleprefix   : [optional] : a string containing the style_prefix to apply to the whole box, including any children
# - tcolor        : [optional] : a Color object (e.g. "#F00") for the text in the input field. This will override the default/specified styling
# NOTE: This is a cut-down version of a screen in another project, since this version is not required to handle floats or negative numbers
screen querynumber(query="Hmm?", preload="", minval=None, maxval=None, variable=None, container=(0, 0, config.screen_width, int(config.screen_height * 0.5) if renpy.variant("mobile") else config.screen_height), bground=None, styleprefix=None, tcolor=None):
    style_prefix styleprefix
    if variable is None:
        $ raise Exception("Invalid argument - screen querystring([required] variable=\"variable_name\"):")
    modal True
    default currentnumber = preload     # This is the variable attached to the input field, and automatically updated by it. It's a string
    default permitted = "0123456789"    # These are the characters accepted by the input field
    use queryframe(container=container, bground=bground, query=query):
        if minval or maxval:
            text "{} {} {}".format(minval if minval else maxval, "through" if minval and maxval else "or", maxval if minval and maxval else ("more" if minval else "less")):
                xalign 0.5
                size gui.notify_text_size
                color gui.insensitive_color
        null height gui.text_size
        # Add the input, and store the results in 'currentnumber'. Field is editable, hitting return does nothing, and the only permitted characters are the ones found in 'permitted'
        input:
            value ScreenVariableInputValue("currentnumber", default=True, returnable=False)
            xalign 0.5
            default preload
            allow permitted
            if tcolor is not None:
                color tcolor
        # - Test for validity, handling an empty string. Assume valid unless proved otherwise
        python:
            number = int(currentnumber) if currentnumber.isdecimal() else 0
            isvalid = True
            if minval: isvalid = False if minval > number else isvalid
            if maxval: isvalid = False if maxval < number else isvalid
        # Add Confirm/Cancel buttons to the bottom of the screen
        use ccframe(callingscreen="querynumber", variable=variable, newvalue=number, isvalid=isvalid)
