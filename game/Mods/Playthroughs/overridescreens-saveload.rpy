# [ DEBUG TOGGLES - REMOVE ALL CODE REFERENCING THESE BINDINGS ]
define config.developer = True
define feedback = ""


# [ NEXT TASKS ]
# - Streamline and triple-check styles are behaving correctly
# - Adapt all user-viewable strings to support translation (low priority)
# - Write and test package against the feature list on GitHub


# [ INITIALISATION - CORE - BEST TO LEAVE ALONE ]
define pathoffset = "Mods/Playthroughs/"
default persistent.save_system = "original"
default persistent.sortby = "lastmodified"
default persistent.playthroughslist = []
default viewingptname = ""
default viewingpt = []
default userinput = ""
default targetaction = ""
default slotdetails = []
init 1:
    # When exiting the game menu, or after loading, clear the variables that store the details of the playthrough being viewed. Do this by re-assigning a custom transition to those events
    # - NOTE: The specified duration needs to be greater than zero for the function to be called. Any transition where a function can be specified may be used
    # - NOTE: These lines redefine existing defines. This is not best practice, but it does mean that we can keep all of the changes of this mod to one file, and avoid altering further screens
    # - NOTE: If this behaviour is not desired, simply comment out the two lines below
    define config.after_load_transition = Dissolve(1, time_warp=ResetPtVars)
    define config.exit_transition = Dissolve(1, time_warp=ResetPtVars)


# [ INITIALISATION - BEHAVIOUR TOGGLES ]
# NOTE: The 'enable_' defines below will still perform their default behaviour if set to 'False' - but the player will either not see their effect, or not be able to alter it
define enable_versioning = True
    # This simply warns the player if a *Playthrough* save is from an older version of the game, by graying out the thumbnail and writing details over the top of it
    # If the save is from a newer version of the game, it will show: a disabled placeholder if True, or nothing at all if False. This is to prevent failed loads or loss of data
define enable_renaming = True
    # This enables the player to provide/edit a friendly name for any existing Playthrough save
    # TODO: Test what happens when previously renamed slots run into 'enable_renaming = False'. They *should* be "playthroughname + slotnumber", yet preserve anything in 'editablename'
define enable_locking = True
    # This enables the player to lock/unlock any Playthrough save. Locked saves cannot be renamed, overwritten or deleted in-game
    # - NOTE: If there are locked files present when 'enable_locking' is False, those files can be renamed and/or deleted. The "LOCKED" flag is preserved. This behaviour is correct.
define enable_sorting = True
    # This enables the player to sort Playthrough slotlists on a specified key. It ships with "lastmodified", "slotnumber", "lockedstatus" and "versionnumber" by default
define enable_iconcolors = True
    # This enables some glyphs to be color-coded. If False, all glyphs will be `textcolor`
        # TODO: This may be better as a persistent toggle, possibly changed by this packages' Preferences screen (if it gets one :P)


# [ INITIALISATION - CONVENIENCE ]
init 1:
    define config.has_autosave = True
    define config.has_quicksave = True
        # These override existing config settings. They are here purely for dev convenience, and can be commented out if they are interfering with existing code


# [ INITIALISATION - UI ]
define maxinputchars = 70
    # The maximum character count permitted for input fields
define layoutseparator = 5
    # The spacing between UI elements of the Playthrough save screen, in whole pixels
define smallscreentextsize = 52
    # Hardcoded minimum text size for small screen devices such as smartphones
define scrollbarsize = smallscreentextsize if renpy.variant("mobile") else gui.scrollbar_size
    # Adjust thickness of vertical scrollbars for the same reason (this package does not use horizontal ones)
define ptbuttonpos = (0.25, 0.18)
    # The position, as fractions of the (width, height) of the whole screen, of the button which switches to the Playthroughs system from the Ren'Py one
    # NOTE: If you set this to None, it will not display the button automatically. Instead, you must incorporate it your 'fileslots(title)' screen via 'use switch_button`
define textcolor = gui.text_color
define hovercolor = gui.hover_color
define focuscolor = "#FFF"
define insensitivecolor = gui.insensitive_color
define interfacecolor = gui.interface_text_color
    # Optional overrides for certain gui elements


# [ UI CALIBRATION/DISPLAYABLES ]
init python:
    # Calculate the text and button sizes we will use, based upon a variety of factors
    SetMetrics()
    # Set the background for Slots. This is what is shown behind each slot and, as above, can be a Displayable (e.g. Frame("gui/nvl.png"), or Solid("000000CF")) or None (removing it entirely)
        # - NOTE: Displayables are usually defined within a Frame in order to be scaled correctly, e.g. Frame("gui/nvl.png"). There are exceptions, such as Color() or Solid()
    slotbackground = renpy.displayable(Frame(pathoffset + "gui/slotbackground.png")) # Solid("#FFF1") #
    # Set the foreground for Slots, indicating when they have focus. It can be any Displayable, or None. If ColorizeMatrix is available, we can tint it to match the Dev's UI color scheme
    # Test for the existence of 'ColorizeMatrix', without running it:
    try:
        ColorizeMatrix
    except NameError:
        # ColorizeMatrix is not available. Use another form of focus highlighting e.g. Solid("#FFFFFF1F"), im. functions, etc. In this case, simply the default image, which is a white border
        slotforeground = renpy.displayable(Frame(pathoffset + "gui/slotforeground.png"))
    else:
        # ColorizeMatrix is available. Use it to tint the image to match the UI color
        slotforeground = renpy.displayable(Frame(Transform(pathoffset + "gui/slotforeground.png", matrixcolor = ColorizeMatrix(Color("#000"), Color(textcolor)))))
    # Locate a font file containing the glyphs we will use instead of image-based icons, below. This permits styling of the icons
    # - NOTE: To view glyphs: 1) Install the font (probably right-click the .ttf file -> Install), then 2) Visit https://fonts.google.com/noto/specimen/Noto+Sans+Symbols+2
    symboltext = pathoffset + "gui/NotoSansSymbols2-Regular.ttf"
    # Set the glyphs we will use for each icon
    # TODO: Overhaul this to be a Dict. Overhaul code that references it to make use of the Dict
    icon_viewplaythroughs = "{color=" + focuscolor + "}𝌮{/color}" if enable_iconcolors else "𝌮" # 𝌮
    icon_viewrenpypages   = "{color=" + focuscolor + "}𝌅{/color}" if enable_iconcolors else "𝌅" # 𝌅
    icon_newplaythrough   = "{color=" + "#00FF00" + "}🞤{/color}" if enable_iconcolors else "🞤" # 🞤
    icon_rename           = "{color=" + interfacecolor + "}🪶{/color}" if enable_iconcolors else "🪶" # 🪶
    icon_delete           = "{color=" + "#FF0000" + "}🞫{/color}" if enable_iconcolors else "🞫" # 🞫
    icon_locked           = "{color=" + "#FF0000" + "}🔒{/color}" if enable_iconcolors else "🔒" # ⚿
    icon_unlocked         = "{color=" + textcolor + "}🔓{/color}" if enable_iconcolors else "🔓" # ⚿
    icon_sortbyrecent     = "⭫" # Alternates: ⏱ 🗓 🕰 ⌚ ⭫
    icon_sortbynumber     = "#" # Alternates: 𝍸 #
    icon_sortbylocked     = "🔒" # Alternates: 🔒
    icon_sortbyversion    = "⚠" # Alternates: ⭭ 🗓 ⚠


# [ STYLING ]
    # TODO: Redfine these to cover all UI styles, and nothing more
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
style fileslots_frame is fileslots:
    xfill True
style fileslots_viewport is fileslots:
    xfill True
style fileslots_vscrollbar:
    unscrollable "hide"
    xsize scrollbarsize


# [ TRANSFORMS ]
transform scroll(chars=35):
    subpixel True
    ypos 1.0 yanchor 0.0
    linear 3.0 + (chars / 5) ypos 0.0 yanchor 1.0
    repeat

transform marquee(chars=35):
    subpixel True
    xpos 1.0 xanchor 0.0
    linear 3.0 + (chars / 5) xpos 0.0 xanchor 1.0
    repeat

transform hovermarquee(chars=10, xpos=0.5, xanchor=0.5):
    on hover:
        subpixel True
        xpos 1.0 xanchor 0.0
        linear 3.0 + (chars / 5) xpos 0.0 xanchor 1.0
        repeat
    on idle:
        xanchor xanchor xpos xpos


# [ CLASSES ]
init python:
    # Reference: (https://www.renpy.org/doc/html/save_load_rollback.html#save-functions-and-variables)
    class Playthrough:
        def __init__(self, name=None):
            # Constructor - defines and initialises the new object properly
            if name == None:
                raise Exception("Invalid argument - object '{self}' of class 'Playthrough': __init__([required] name=string)")
            self.name = name
            self.slots = self.GetSlots()
            self.lockcount = [slot[4] for slot in self.slots].count("LOCKED")
            self.higherversioncount = [True if slot[5].lower() > config.version.lower() else False for slot in self.slots].count(True)
            self.SortSlots()

        def GetSlots(self):
            # This needs to return a list of lists, where each sublist contains all the data about the slot except the thumbnail. This is so that we can use both indices and list comprehension
            # Populate the slotslist by using a 'regex'. 'Regex' is short for "regular expression". It defines rules for extracting wanted data out of a pile of it
            # - This particular regex says that we want matches that: "^"(begins with) + (self.name(the name field of this object) + "-"(to avoid unwanted partial matches))
            files, slots = renpy.list_saved_games("^" + self.name + "-", fast=True), []
            # - We need a slot structure:
            #   - Filename          : Full string as used by Ren'Py file functions
            #   - Last modified     : UNIX epoch offset     - WARNING: Ren'Py file renaming preserves the OS timestamp on Windows. It may not on other systems
            #   - Slot number       : An integer greater than zero
            #   - Editable name     : What the player sees. It defaults to Playthrough Name + Slot Number
            #   - Locked status     : A string. Code currently assigns meaning to "LOCKED" or "", nothing else
            #   - Version number    : The version number of the game when the file was last properly saved (as opposed to renamed). WARNING: Must go last, in case Dev uses "-" in it
            # - With this in place, our code references the list (with the exception of the thumbnail). Every change to filename subdata must be reflected to the disk file immediately
            for file in files:
                subdata = file.split("-")
                if (self.name == "auto" or self.name == "quick"):
                    slots.append([file, renpy.slot_mtime(file), int(subdata[1]), FileSaveName(file, empty="", slot=True), "", ""])
                else:
                    slots.append([file, renpy.slot_mtime(file)] + [int(subdata[1])] + subdata[2:4] + ["-".join(subdata[4:])])
            # Pass the data back to the calling expression
            return slots

        def SortSlots(self, reverse=True):
            # Strip any existing slots that have a filename that is "+ New Save +", because we cannot assume that we're dealing with a slotslist that has not already been sorted
            # - NOTE: This doesn't appear to be necessary. I don't know why? - [EDIT:] There is other code that shouldn't work, and does. I think it's just the way Ren'Py handles stuff internally
            # Sort the slots in (reverse) order according to the value of 'persistent.sortby':
            # - NOTE: The '.sort()' method mutates the original list, making changes in place
            slotkeys = ["filename", "lastmodified", "slotnumber", "editablename", "lockedstatus", "versionnumber"]
            # ... Since "auto"/"quick" saves are performed cyclically, sorting by "lastmodified" is the same as sorting by "slotnumber" would be for Playthrough slotlists
            sortby = "lastmodified" if (self.name == "auto" or self.name == "quick") else persistent.sortby
            # ... Default to "lastmodified" if the requested 'sortby' cannot be found in 'slotkeys[]', and store the index of the required key
            sortkey = slotkeys.index(sortby) if sortby in slotkeys else slotkeys.index("lastmodified")
            # ... Perform the sort. The '.sort()' method uses a lambda to find the key data to sort against for each item(list of slot details) in the iterable(list of slots)
            # - NOTE: lambdas are disposable anonymous functions that use (an) input(s) to derive a required output. More here: (https://www.w3schools.com/python/python_lambda.asp)
            if sortby in ("versionnumber","lockedstatus"):
                reverse = False
                # TODO: Fix kludgey override above and make the button call the function with parameters
                # - [EDIT:] NOTE: "Function(viewingpt.SortSlots, reverse=False)" not working - [EDIT:] NOTE: viewingpt.SortSlots(), or "viewingpt.SortSlots", or "viewingpt.SortSlots()", may.
            self.slots.sort(reverse=reverse, key=lambda x: x[sortkey])
            # If appropriate, add slots that define "+ New Save +" slots by position. Since "auto"/"quick" are hard-sorted by "lastmodified", this will not affect those 'playthrough's
            i = slotkeys.index("slotnumber")
            if sortby == "slotnumber" and len(self.slots) > 1:
                # We've already sorted the list, so run through it backwards and insert "+ New Save +" slots where needed
                # - NOTE: Going backwards preserves the indices of yet-to-be-checked slots, because any newly-inserted slots are increasing the length of the list even as we step through it
                span = len(self.slots) - 1
                for slot in range(span, 0, -1):
                    lower, upper = self.slots[slot][i], self.slots[slot - 1][i]
                    if upper-lower == 2:
                        # There is a single-slot gap here
                        self.slots.insert(slot, ["+ New Save +", "", lower + 1, "", "", ""])
                    elif upper-lower > 2:
                        # There is a multi-slot gap here; store the range (as integers) in the 'lastmodified' and 'versionnumber' fields
                        self.slots.insert(slot, ["+ New Save +", lower + 1, "", "", "", upper - 1 ])
            # Finally, insert a "+ New Save +" slot at the beginning of the list - unless we're in "auto"/"quick"
            if self.name != "auto" and self.name != "quick":
                # Find the highest slotnumber there currently is, and add 1. Insert this "+ New Save +" slot at the beginning of the list
                slotnumbers = [slot[i] for slot in self.slots if slot[0] != "+ New Save +"]
                # Dodge 'max()' crashing over an empty list...
                slotnumber = max(slotnumbers) if slotnumbers != [] else 0
                slotnumber += 1
                self.slots.insert(0, ["+ New Save +", "", slotnumber, "", "", ""])


# [ FUNCTIONS ]
init -1 python:
    def SetMetrics():
        global lastknownaccessibilityscale, lastknownfontsize, textsize, yvalue, slotheight, qfspacer
        # Record current settings
        lastknownaccessibilityscale = preferences.font_size
        lastknownfontsize = gui.text_size
        # Clamp text size to sensible values
        textsize = max(min(lastknownfontsize, 80), 20)
        # Enlarge text size if player is using a small screen
        if renpy.variant("mobile") and textsize < smallscreentextsize:
            textsize = smallscreentextsize
        # yvalue is used to line up the edges of various UI elements, primarily buttons which need extra space around the text to look good
        yvalue = int(textsize * 1.5 * lastknownaccessibilityscale)
        # The height of the save slots is calculated from the height of the save thumbnail (typically defined in 'gui.rpy'), the size of three icons, and the above-defined 'layoutseparator'
        slotheight = int(max(config.thumbnail_height, (yvalue * 3)) + (layoutseparator * 2))
        # Permits compressed spacing inside input boxes if the player is using a mobile device
        qfspacer = int(layoutseparator * 2) if renpy.variant("mobile") else yvalue

    def ResetPtVars(timeline=1.0):
        # This is a dummy transition timeline function that instantly returns as complete. The entire purpose is to reset the playthrough variables
        # TODO: This should be altered so that it still performs the function of whatever transition was in place before we hijacked it - learn how
        global userinput, targetaction, viewingptname, viewingpt, slotdetails
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
            if subdata: newfilename += "-" + str(subdata)   # TODO: See if this can be done with .join() - [EDIT:] probably, but can I be bothered? This works :P
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

    def ProcessUserInput():
        # This is an all-purpose function that is called whenever user input is available
        # - NOTE: I don't know how to make an action list wait for input and then resume; this is a workaround that calls this function once per screen update... I think
            # TODO: Figure out if "call in new context" is the designed solution to this problem, and how to achieve it - [EDIT:] The `Confirm()` action manages this. Must be doable.
        global userinput, targetaction, viewingptname, viewingpt, slotdetails
        # The first thing to do is quit out unless there is something that actually needs processing (redundant ... unless someone puts it into an 'action' list)
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
                    if slotdetails[3] != "LOCKED":
                        slotdetails[2] = slotdetails[2].replace(oldptname, viewingptname)
                    ReflectSlotChanges()
                if persistent.playthroughslist.count(oldptname) != 1:
                    raise Exception("Error: {} one copy of Playthrough \"{}\" in the persistent list".format("Less than" if persistent.playthroughslist.count(oldptname) < 1 else "More than", oldptname))
                persistent.playthroughslist[persistent.playthroughslist.index(oldptname)] = viewingptname
                viewingpt = Playthrough(name=viewingptname)
            elif targetaction == "newslotnumber":
                # This saves the new file if not already existent, then updates the playthrough list order
                filename = "{0}-{1}-{0} {1}-Unlocked-{2}".format(viewingptname, userinput, config.version)
                if renpy.can_load(filename):
                    raise Exception("Error: File \"{}\" already exists".format(filename))
                renpy.save(filename)
                MakePtLast()
            elif targetaction == "changeslotname":
                # Update 'slotdetails' with 'userinput', then reflect any changes to the relevant disk file
                slotdetails[2] = userinput
                ReflectSlotChanges()
            else:
                raise Exception("Error: 'userinput' ({}) sent to an invalid 'targetaction' ({})".format(userinput, targetaction))
            userinput, targetaction = "", ""


# [ SCREENS ]
# The original save screen, modified and overridden
screen save():
    tag menu
    if persistent.save_system == "original":
        use file_slots("Save")
        if ptbuttonpos:
            use switch_button(ptbuttonpos[0], ptbuttonpos[1])
    elif persistent.save_system == "playthrough":
        use playthrough_file_slots("Save")
    else:
        $ raise Exception("Error: Invalid persistent.save_system - \"{}\"".format(persistent.save_system))

# The original load screen, modified and overridden
screen load():
    tag menu
    if persistent.save_system == "original":
        use file_slots("Load")
        if ptbuttonpos:
            use switch_button(ptbuttonpos[0], ptbuttonpos[1])
    elif persistent.save_system == "playthrough":
        use playthrough_file_slots("Load")
    else:
        $ raise Exception("Error: Invalid persistent.save_system - \"{}\"".format(persistent.save_system))

# Provide a button to switch to the Playthroughs system
screen switch_button(xpos=0.0, ypos=0.0):
    button:
        tooltip "Switch to the Playthrough system"
        style_prefix "icon"
        xysize (yvalue, yvalue)
        pos (xpos, ypos)
        text icon_viewplaythroughs:
            line_leading int(yvalue / 5) # TODO: This line-leading thing is kludgey - see if it can't be more elegantly fixed
        action SetVariable("persistent.save_system", "playthrough")

# The new playthrough system
screen playthrough_file_slots(title):
    python:
        # Make sure we're accessing the global variables
        global viewingptname, viewingpt, targetaction, userinput
        # Check whether we have a user input waiting to be processed
        if userinput:
            ProcessUserInput()
        # Check whether the font size has changed
        if preferences.font_size != lastknownaccessibilityscale or gui.text_size != textsize:
            SetMetrics()
        # Check the validity of the playthrough name that we're viewing. If invalid, find the latest valid name. If none found, set 'viewingptname' to an empty string
        if ((config.has_autosave and viewingptname == "auto") or (config.has_quicksave and viewingptname == "quick") or (persistent.playthroughslist and viewingptname in persistent.playthroughslist)) == False:
            viewingptname = persistent.playthroughslist[-1] if persistent.playthroughslist else ""
        # Populate the viewed playthrough if 'viewingptname' is not an empty string, unless we're expecting user input
        if viewingptname != "" and targetaction == "":
            viewingpt = Playthrough(name=viewingptname)
            # NOTE: ONLY recreating this on playthrough name change broke a lot of things, because the UI would not update when it should (because the object hadn't changed).
            #       Thus, I've limited the damage by disallowing re-creation of the object if we're waiting on user input i.e. there's a modal screen over the top of the UI.
            #       It's still not ideal, because events such as hovered/unhovered will still recreate the whole Playthrough object (complete with disk read)
    use game_menu(title):
        style_prefix "fileslots"
        # By using 'side' in this manner, we put any tooltips in a strip across the top of the container we're in, and everything else in the center (below)
        # - Because of the way in which side calculates its layout (center last), subcontainers get accurate metrics with which to handle their own calculations, dodging some viewport issues
        side "t c":
            # Top tooltip, displayed above everything else.
                # TODO: scroll only if contents outsize the container. Currently: Always scrolls - [EDIT:] No way found to do this. Ren'Py 8 may provide access to internal metrics
            fixed:
                ysize yvalue
                # Display only what is inside the container, by cropping off anything outside it
                at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)
                # Collect and display any active tooltip on this page
                $ help = GetTooltip() or feedback or ("" if viewingptname else "Use {=icon_text}[icon_newplaythrough]{/=} to start a new Playthrough")
                if help:
                    text help:
                        at marquee(len(help))
                        style "fileslots_focus"
                        layout "nobreak"
                        italic True
            # Two panels, side-by-side in an hbox: Playthroughs and Slots
            hbox:
                spacing int(layoutseparator * 2)
                # Playthroughs panel
                vbox:
                    xsize 0.35 * lastknownaccessibilityscale
                    # This header and the panel below it are offset slightly to the left, to compensate for the width and spacing of the vertical scrollbar in the viewport below them
                    text "Playthroughs":
                        size gui.label_text_size
                        color interfacecolor
                        xalign 0.5
                        xoffset -round((scrollbarsize + layoutseparator) / 2)
                    null height layoutseparator
                    # Display top panel, which contains 1-4 buttons
                    use display_top_buttons(title)
                    null height layoutseparator
                    # Vertically-scrolling vpgrid for the list of Playthroughs
                    vpgrid:
                        cols 1
                        scrollbars "vertical"
                        mousewheel True
                        side_spacing layoutseparator
                        spacing layoutseparator
                        for i in range(len(persistent.playthroughslist) - 1, -1, -1):
                            use display_playthrough_button(i)
                # Fileslots panel
                vbox:
                    xfill True
                    # Header
                    text "Saves":
                        size gui.label_text_size
                        color interfacecolor
                    null height layoutseparator
                    # Provide (or not) buttons that alter the key that the slotslist is sorted on
                    if enable_sorting and viewingptname and viewingptname != "auto" and viewingptname != "quick":
                        use display_sorting_buttons
                        null height layoutseparator
                    # Display all the fileslots that are in the playthrough being viewed, keyed off 'viewingptname'. If no playthrough is being viewed, display nothing
                    if viewingptname != "":
                        # Vertically-scrolling vpgrid for the slotslist
                        vpgrid:
                            cols 1
                            scrollbars "vertical"
                            mousewheel True
                            side_spacing layoutseparator
                            spacing layoutseparator
                            for slot in viewingpt.slots:
                                use display_slot_button(slot, title)

# Displays the top 1-4 buttons above the Playthroughs list
screen display_top_buttons(title=None):
    if title != None:
        hbox:
            ysize yvalue
            xalign 0.5
            xoffset -round((scrollbarsize + layoutseparator) / 2)
            # Provide a button to switch to the original save system
            button:
                tooltip "Switch to the Ren'Py [title] system"
                style_prefix "icon"
                xysize (yvalue, yvalue)
                text icon_viewrenpypages:
                    line_leading int(yvalue / 5)
                action [SetVariable("persistent.save_system", "original")
                        ]
            if config.has_autosave:
                textbutton  _("{#auto_page}A"):
                    tooltip "Show Autosaves"
                    style_prefix "selection"
                    xysize (yvalue, yvalue)
                    action [SetVariable("viewingptname", "auto"),
                            SetVariable("viewingpt", Playthrough(name="auto"))
                            ]
            if config.has_quicksave:
                textbutton _("{#quick_page}Q"):
                    tooltip "Show Quicksaves"
                    style_prefix "selection"
                    xysize (yvalue, yvalue)
                    action [SetVariable("viewingptname", "quick"),
                            SetVariable("viewingpt", Playthrough(name="quick"))
                            ]
            # If we're on the Save screen, provide a button to allow the creation of a new, uniquely-named, playthrough that is also not simply a number (Ren'Py Pages)
            if title == "Save":
                button:
                    tooltip "Create a new Playthrough"
                    style_prefix "icon"
                    xysize (yvalue, yvalue)
                    text icon_newplaythrough:
                        line_leading int(yvalue / 5)
                    action [SetVariable("targetaction", "newplaythroughname"),
                            Show("querystring", query="{color=" + interfacecolor + "}Please give this Playthrough a unique name{/color}", excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=maxinputchars, variable="userinput", bground="gui/frame.png", styleprefix="fileslots", tcolor=focuscolor)
                            ]

# Displays any sorting buttons above the Slots list
screen display_sorting_buttons():
    hbox:
        # TODO: Streamline styling... again
        # TODO: Er. This can become a loop through a list of lists. On the other hand, this works and is easy to understand. Low priority
        ysize yvalue
        button:
            tooltip "Sort slots by most recently changed first"
            style_prefix "icon"
            xysize (yvalue, yvalue)
            selected_background textcolor
            hover_background None
            text icon_sortbyrecent:
                line_leading int(yvalue / 5)
                hover_color hovercolor
                selected_color hovercolor
            action [SetVariable("persistent.sortby", "lastmodified"),
                    viewingpt.SortSlots
                    ]
        button:
            tooltip "Sort slots by highest slot number first"
            style_prefix "icon"
            xysize (yvalue, yvalue)
            selected_background textcolor
            hover_background None
            text icon_sortbynumber:
                line_leading int(yvalue / 5)
                hover_color hovercolor
                selected_color hovercolor
            action [SetVariable("persistent.sortby", "slotnumber"),
                    viewingpt.SortSlots
                    ]
        if enable_locking:
            button:
                tooltip "Sort slots by showing locked slots first"
                style_prefix "icon"
                xysize (yvalue, yvalue)
                selected_background textcolor
                hover_background None
                text icon_sortbylocked:
                    line_leading int(yvalue / 5)
                    hover_color hovercolor
                    selected_color hovercolor
                action [SetVariable("persistent.sortby", "lockedstatus"),
                        viewingpt.SortSlots
                        ]
        if enable_versioning:
            button:
                tooltip "Sort slots by lowest version number first"
                style_prefix "icon"
                xysize (yvalue, yvalue)
                selected_background textcolor
                hover_background None
                text icon_sortbyversion:
                    line_leading int(yvalue / 5)
                    hover_color hovercolor
                    selected_color hovercolor
                action [SetVariable("persistent.sortby", "versionnumber"),
                        viewingpt.SortSlots
                        ]

# Provides functionality that displays, selects, modifies or deletes the `i`th playthrough in `persistent.playthroughslist[]` via the `use` feature
screen display_playthrough_button(i=None):
    if i != None:
        # Using a side allows us to use xfill True or xsize 1.0 for the central button, without compromising the size of any end buttons or having to calculate around them
        side "l c r":
            # Rename button at the left, if we're dealing with the selected playthrough - otherwise a blank, sized area
            fixed:
                xysize (yvalue, yvalue)
                if enable_renaming and persistent.playthroughslist[i] == viewingptname:
                    button:
                        tooltip "Rename the \"{}\" Playthrough".format(viewingptname)
                        style_prefix "icon"
                        xysize (yvalue, yvalue)
                        text icon_rename:
                            line_leading int(yvalue / 5)
                        action [SetVariable("targetaction", "changeplaythroughname"),
                                Show("querystring", query="{color=" + interfacecolor + "}Please give this Playthrough a unique name{/color}", preload=viewingptname, excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=maxinputchars, variable="userinput", bground="gui/frame.png", styleprefix="fileslots", tcolor=focuscolor)
                                ]
            # Playthrough selection button in the center, sized last, which permits internal sizing to work correctly
            button:
                tooltip "Show saves in the \"{}\" Playthrough".format(persistent.playthroughslist[i])
                style "selection_button"
                xysize (1.0, yvalue)
                at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)
                text persistent.playthroughslist[i]:
                    layout "nobreak"
                    hover_color hovercolor
                    color (hovercolor if persistent.playthroughslist[i] == viewingptname else textcolor)
                    at hovermarquee(len(persistent.playthroughslist[i]))
                action [SetVariable("viewingptname", persistent.playthroughslist[i]),
                        SetVariable("viewingpt", Playthrough(name=persistent.playthroughslist[i]))
                        ]
            # Delete button at the right, if we're dealing with the selected playthrough - otherwise a blank, sized area
            fixed:
                xysize (yvalue, yvalue)
                if persistent.playthroughslist[i] == viewingptname:
                    button:
                        tooltip "Delete the \"{}\" Playthrough".format(viewingptname)
                        style_prefix "icon"
                        xysize (yvalue, yvalue)
                        text icon_delete:
                            line_leading int(yvalue / 5)
                        action [Confirm("Are you sure you want to delete this Playthrough?\n{}{}".format("{size=" + str(gui.notify_text_size) + "}{color=" + str(insensitivecolor) + "}\nLocked saves: " + str(viewingpt.lockcount) + "{/color}{/size}" if viewingpt.lockcount else "", "{size=" + str(gui.notify_text_size) + "}{color=" + str(insensitivecolor) + "}\nSaves from a later version: " + str(viewingpt.higherversioncount) + "{/color}{/size}" if viewingpt.higherversioncount else ""), yes=Function(DeletePlaythrough), confirm_selected=True)
                                ]

# Provides functionality that displays, selects, modifies or deletes the save given by `slot` via the `use` feature
screen display_slot_button(slot=None, title=None):
    if slot != None and title != None:
        python:
            # Unpack the details from the given slot
            filename, lastmodified, slotnumber, editablename, lockedstatus, versionnumber = slot
            # Produce a name for the slot...
            if enable_renaming and editablename:
                slotname = editablename
            else:
                # ...if 'editablename' is not available/permitted, use playthrough name and slot number; if 'slotnumber' is not available, 'lastmodified' and 'versionnumber' will hold the range
                slotname = "{} {}".format(viewingptname, slotnumber if slotnumber else "[[{} to {}]".format(lastmodified, versionnumber))
            slottextcolor = textcolor
                # Reset this each time, since the last time through might have made it 'insensitivecolor', and it appears to be preserved between 'use's
        # Handle any slot which has been inserted into the list for the purpose of creating a new save, and therefore is not yet a disk file:
        if filename == "+ New Save +":
            # Only produce the button if we're on the Save screen
            # NOTE: "auto"/"quick" 'playthrough's will not have been given any "+ New Save +" slots, so they *shouldn't* ever reach this code...
            if title == "Save":
                button:
                    tooltip "Create a new save: \"{}\"".format(slotname)
                    xysize (1.0, slotheight)
                    background slotbackground
                    hover_foreground slotforeground
                    text "+ New Save +":
                        align (0.5, 0.5)
                        hover_color hovercolor
                    action [SetVariable("targetaction", "newslotnumber"),
                            If(slotnumber, true=SetVariable("userinput", slotnumber), false=Show("querynumber", query="{color="+interfacecolor+"}Please select a slot number:{/color}", preload=str(lastmodified), minval=lastmodified, maxval=versionnumber, variable="userinput", bground="gui/frame.png", styleprefix="fileslots", tcolor=focuscolor))
                            ]
        # Disable any slot that has a version number higher than this app; loading will likely fail and overwriting will likely lose data
        elif versionnumber.lower() > config.version.lower():
            if enable_versioning:
                frame:
                    xysize (1.0, slotheight)
                    background slotbackground
                    vbox:
                        align (0.5, 0.5)
                        spacing layoutseparator
                        for i in ["- Newer save -", "( v{} )".format(versionnumber), editablename]:
                            text i:
                                xalign 0.5
                                color insensitivecolor
                                layout "subtitle"
        # Everything else should all be pre-existing disk files that need to be shown
        else:
            default hasfocus = False
                # Used to store whether or not the button has detected that it has focus, in order to apply a transform or not to a child text displayable
            $ timestamp = "{}".format(FileTime(filename, format=_("{#file_time}   <%H:%M ~ %A %B %d, %Y>"), slot=True))
            button:
                tooltip "{} save:  \"{}\"{}".format("Load" if title == "Load" else "Overwrite", slotname, timestamp)
                xysize (1.0, slotheight)
                background slotbackground
                hover_foreground slotforeground
                # Store hovered status in 'hasfocus', which controls activation of movement transforms. 'SetLocalVariable()' is used because this screen is 'use'd by other screens
                # NOTE: 'unhovered' will not fire if e.g. the Accessibilty screen is accessed via kybind, then dismissed via the "Return" button. The transform runs until the next unhover
                hovered SetLocalVariable("hasfocus", True)
                unhovered SetLocalVariable("hasfocus", False)
                # This next line is a nested/compund action list, where several things may or may not happen
                action [If(title == "Save",
                            false=  [MakePtLast, FileLoad(filename, slot=True)],
                            true=   [SetLocalVariable("hasfocus", False),
                                    Confirm("Are you sure you want to overwrite this save?{}".format("{size=" + str(gui.notify_text_size) + "}{color=" + str(insensitivecolor) + "}\n\nSaved by version " + str(versionnumber) + "{/color}{/size}" if enable_versioning and versionnumber != "" and versionnumber != config.version else ""), confirm_selected=True,
                                        no= [NullAction()],
                                        yes=[FileDelete(filename, slot=True, confirm=False), FileSave("{}-{}".format(viewingptname, slotnumber) if viewingptname in ["auto", "quick"] else "{}-{}-{}-Unlocked-{}".format(viewingptname, slotnumber, editablename, config.version), slot=True, confirm=False), MakePtLast])])
                        ]
                if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                    key "save_delete" action [SetLocalVariable("hasfocus", False), FileDelete(filename, slot=True)]
                if enable_versioning and versionnumber != "" and versionnumber != config.version:
                    tooltip "{} save:  \"{}\"{}".format("Attempt to Load" if title == "Load" else "Overwrite", slotname, timestamp)
                if title == "Save" and (viewingptname == "auto" or (enable_locking and lockedstatus == "LOCKED")):
                    # Setting sensitive to 'False' helpfully disables all hover- and tooltip-related behaviour
                    sensitive False
                    $ slottextcolor = insensitivecolor
                side "l c r":
                    # Thumbnail on the left of the button
                    fixed:
                        xysize (int(config.thumbnail_width + (layoutseparator * 2)), slotheight)
                            # Preserve a border of whatever the slotbackground shows
                        frame:
                            xysize (config.thumbnail_width, config.thumbnail_height)
                            align (0.5, 0.5)
                            background Frame(FileScreenshot(filename, slot=True))
                            # Darken the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                            if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)
                                add Solid("#000000CF")
                                vbox:
                                    at truecenter
                                    text "- Older Save -":
                                        style "fileslots_focus"
                                        size gui.slot_button_text_size
                                        xalign 0.5
                                        layout "nobreak"
                                    null height gui.slot_button_text_size
                                    text "v{}".format(versionnumber):
                                        style "fileslots_focus"
                                        size gui.slot_button_text_size
                                        xalign 0.5
                                        layout "nobreak"
                    # Save name in the center, either marquee'ing or scrolling on focus (based on yvalue)
                    fixed:
                        xysize (1.0, 1.0)
                        at Transform(crop=(0, 0, 1.0, 1.0), crop_relative=True)
                        text slotname:
                            at ((scroll(len(slotname)) if yvalue > 86 else marquee(len(slotname))) if hasfocus else None)
                            color (hovercolor if hasfocus else slottextcolor)
                            align (0.5, 0.5)
                            text_align 0.5
                            layout "subtitle"
                    # Iconbuttons for Rename, Lock/Unlock, and Delete on the left of the button, stacked and centered vertically
                    frame:
                        # NOTE: If not 'enable_locking', the Delete icon shows.
                        #       If 'enable_locking' and not 'lockedstatus', the Delete icon shows.
                        #       If 'enable_locking' and 'lockedstatus', the Lock/Unlock icons show.
                        #       Therefore, at least one icon is always showing, and we don't need to code for their absence.
                        # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                        xsize int(yvalue + (layoutseparator * 2))
                            # BUG: If you don't have at least one dimension specified here, self-calculating doesn't properly position this within the 'side:'
                            # TODO: Slap a demo together and give it to Tom
                        padding (layoutseparator, layoutseparator)
                            # Preserve a border of whatever the save slot background is
                        yalign 0.5
                        vbox:
                            if enable_renaming and editablename and (enable_locking == False or (enable_locking and lockedstatus != "LOCKED")):
                                button:
                                    tooltip "Rename save:  \"{}\"{}".format(slotname, timestamp)
                                    style_prefix "icon"
                                    xysize (yvalue, yvalue)
                                    text icon_rename:
                                        line_leading int(yvalue / 5)
                                    action [SetVariable("targetaction", "changeslotname"),
                                            SetVariable("slotdetails", [filename, slotnumber, editablename, lockedstatus, versionnumber]),
                                            Show("querystring", query="{color="+interfacecolor+"}Please enter the slot name:{/color}", preload=editablename, excludes="[{<>:\"/\|?*-", maxcharlen=maxinputchars, variable="userinput", bground="gui/frame.png", styleprefix="fileslots", tcolor=focuscolor)
                                            ]
                            if enable_locking and lockedstatus:
                                button:
                                    tooltip "{} save:  \"{}\"{}".format("Unlock" if lockedstatus == "LOCKED" else "Lock", slotname, timestamp)
                                    style_prefix "icon"
                                    xysize (yvalue, yvalue)
                                    text (icon_locked if lockedstatus == "LOCKED" else icon_unlocked):
                                        line_leading int(yvalue / 5)
                                    action [SetVariable("slotdetails", [filename, slotnumber, editablename, "Unlocked" if lockedstatus == "LOCKED" else "LOCKED", versionnumber]),
                                            ReflectSlotChanges
                                            ]
                            if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                button:
                                    tooltip "Delete save:  \"{}\"{}".format(slotname, timestamp)
                                    style_prefix "icon"
                                    xysize (yvalue, yvalue)
                                    text icon_delete:
                                        line_leading int(yvalue / 5)
                                    action [FileDelete(filename, slot=True)
                                            ]


# [ ADDITIONAL SCREENS ]


# { SUPPORT SCREEN } - Adds a box to the middle of a container, offering a text field to the player and storing the result in a specified variable. Designed for strings
# - query         : [optional] : Passed to screen queryframe() - a string containing the box title/a question to put to the player
# - preload       : [optional] : a string that initially populates the input field
# - excludes      : [optional] : a string passed to the input field that contains forbidden characters. Not usually used; must contain "[{" if it is  - WARNING: This is not checked!
# - invalid       : [optional] : a list containing invalid responses; if currentstring is in the list, the 'isvalid' flag is set to False
# - maxcharlen    : [optional] : an integer passed to the input field specifying the maximum character length of the response string
# - maxpixelwidth : [optional] : an integer passed to the input field specifying the maximum size of the response string in pixels, when rendered using the input style
# - variable      :  REQUIRED  : Passed to screen ccframe() - a string containing the name of the GLOBAL variable that will store the result
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
                color insensitivecolor
        if maxcharlen:
            text "{}/{}".format(len(currentstring), maxcharlen):
                xalign 0.5
                size gui.notify_text_size
                color (insensitivecolor if len(currentstring) <= maxcharlen else "#F00")
        null height qfspacer
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
                    if targetaction in ["newplaythroughname", "changeplaythroughname"]:
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
                color insensitivecolor
        null height qfspacer
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

# { SUPPORT SCREEN } - Provides the query_ screens with a degree of wrapping
# - container     : [optional] : an (x, y, xsize, ysize) tuple specifying the area that the input box will be centered in
# - bground       : [optional] : a Displayable for the background property of the largest non-transparent Frame(), which will be scaled to fit
# - query         : [optional] : a string containing the question to put to the player
screen queryframe(container=(0, 0, config.screen_width, config.screen_height), bground=None, query="Hmm?"):
    frame:
        area container
        background Frame("gui/overlay/confirm.png")
        frame:
            at truecenter
            background Frame(bground)
            xfill False
            yfill False
            padding (qfspacer, qfspacer)
            vbox:
                at truecenter
                text query:
                    xalign 0.5
                    size gui.label_text_size
                transclude

# { SUPPORT SCREEN } - Tacks Confirm/Cancel buttons onto the bottom of whatever called it, and sets 'variable' to 'newvalue' if Confirm is clicked. Both buttons will Hide() 'callingscreen'
# - Both 'variable' and 'callingscreen' are REQUIRED; 'newvalue' and 'isvalid' are [optional]
# - NOTE: The padding is in place on the buttons in case a Dev wants to give them a background
screen ccframe(callingscreen=None, variable=None, newvalue=None, isvalid=True):
    if variable is None or callingscreen is None:
        $ raise Exception("Invalid argument - screen ccframe([required] variable=\"variable_name\" and callingscreen=\"screen_name\"):")
    key "game_menu" action [SetVariable("targetaction", ""), Hide(callingscreen)]
    null height qfspacer
    hbox:
        xalign 0.5
        spacing qfspacer
        textbutton "Confirm":
            size_group "ccbuttons"
            text_align (0.5, 0.5)
            padding (layoutseparator, layoutseparator)
            if isvalid == False:
                sensitive False
            action (SetVariable(variable, newvalue), Hide(callingscreen))
        textbutton "Cancel":
            size_group "ccbuttons"
            text_align (0.5, 0.5)
            padding (layoutseparator, layoutseparator)
            action [SetVariable("targetaction", ""), Hide(callingscreen)]
