
# [ INITIALISATION - BEST TO LEAVE ALONE ]
default persistent.savesystem = "original"
default persistent.sortby = "lastmodified"
default persistent.playthroughslist = []
default lastpage = None
default viewingptname = ""
default viewingpt = []
default userinput = ""
default targetaction = ""
default slotdetails = []

# When exiting the game menu, or after loading, clear the variables that store the details of the playthrough being viewed. Do this by re-assigning a custom transition to those events
# - NOTE: The specified duration needs to be greater than zero for the function to be called. Any transition where a function can be specified may be used
# - NOTE: These lines re-initialise defines. This is not best practice, but it does mean that we can keep all of the changes of this mod to one file, and avoid altering further screens
# - NOTE: If this behaviour is not desired, simply comment out the two lines below
define config.after_load_transition = Dissolve(1, time_warp=ResetPtVars)
define config.exit_transition = Dissolve(1, time_warp=ResetPtVars)

# [ INITIALISATION - FREELY MODIFIABLE ]
# NOTE: The five 'enable_' defines below will still perform their default behaviour if set to 'False' - but the player will either not see their effect, or not be able to alter it
define enable_versioning = True
    # This simply warns the player if a *Playthrough* save is from an older version of the game, by graying out the thumbnail and writing details over the top of it
    # If the save is from a newer version of the game, it will show: a disabled placeholder if True, or nothing at all if False. This is to prevent failed loads or loss of data
define enable_renaming = True
    # This enables the player to provide/edit a friendly name for any existing Playthrough save
    # TODO: For Ren'Py saves (excluding Auto/Quick), it shows an overlay/button on the slot that can be clicked on to provide a name for the new/overwritten slot
define enable_locking = True
    # This enables the player to lock/unlock any Playthrough save. Locked saves cannot be renamed, overwritten or deleted in-game
    # TODO: Check that this still works as intended with files that are locked when 'enable_locking' is False
    # - [EDIT:] If there are locked files preesent when 'enable_locking' is False, those files can be renamed and/or deleted. The "LOCKED" flag is preserved
        # TODO: Decide if this behaviour is correct, or needs amending
define enable_sorting = True
    # This enables the player to sort Playthrough slotlists on a specified key. It ships with "lastmodified" and "slotnumber" by default; "versionnumber" and "lockedstatus" may also be of use
define enable_animation = False
    # This determines the hover behaviour of the icons in the UI: True will make the icons spin, False will highlight their background
    # WARNING: At the moment, this makes the icons in the save slots somehow cause the viewport to show an unscrollable scrollbar, despite there being lots of room
define slotbackground = None #Solid("FFF1")
    # This is what is shown behind each slot, and can be any Displayable or None. Either hard-code it, or use a binding defined at a lower init level
    # - NOTE: Displayables are usually defined within a Frame in order to be scaled correctly, e.g. Frame("gui/nvl.png"). There are exceptions, such as Color() or Solid()
    # - NOTE: None is the default, removing the background, resulting in total transparency

# [ INITIALISATION - CONVENIENCE ]
define config.has_autosave = True
define config.has_quicksave = True
    # These override existing config settings. They are here purely for dev convenience, and can be commented out if they are interfering with existing code


# [ CLASSES ]
init python:
    # Reference: (https://www.renpy.org/doc/html/save_load_rollback.html#save-functions-and-variables)
    class Playthrough:
        """The Playthough class (summary line)

        The playthrough class stores the name of the play through and a list of saves for that playthough (detailed line)

        Attributes:
            attribute1_EXAMPLE (data type): Description of attribute1
            name (str): The name of the playthough
            slots (:obj:`list` of :obj:`str`): The list of files for the game
            lockcount (int): The count of the number of saves locked
            higherversioncount (int): The count of the number of slots with a higher version than config.version
        """

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


# [ STYLING ]
style fileslots:
    margin (0, 0)
    padding (0, 0)
style fileslots_frame is fileslots:
    xfill True
style fileslots_button is fileslots
style fileslots_text:
    outlines [(absolute(1), "#000", 0, 0)]
style fileslots_button_text is fileslots_text:
    hover_color gui.hover_color
    insensitive_color gui.insensitive_color
style fileslots_input is fileslots_text:
    # I use pure white as a color for "text focus"; contextual information or input that the user should pay attention to. Ofc, if the dev is using white everywhere, this won't be as effective /shrug
    # NOTE: Dropping this into The Question results in tooltip text that is transparent (the outline is present), but only on the Playthroughs page - it is as intended on the Ren'Py page?
    # - [EDIT:] Changing the value to "#FFFF" has no effect. Possible workaround: two outlines, so at least one is high contrast [(absolute(2), "#000F", 0, 0), (absolute(1), "#FFFF", 0, 0)]
        # TODO: Figure out why, and how to avoid the override in other games
    color "#FFF"
style fileslots_viewport is fileslots:
    xfill True
style fileslots_vscrollbar:
    unscrollable "hide"


# [ TRANSFORMS ]
transform HoverSpin:
    # rotate_pad True       # - [EDIT:] This doesn't seem to make any difference, either because the image is square or because the background is transparent. So no need for further computation
    # Until 7.4.9 is released, it is necessary to handle both normal and selected states, because this is usually applied to a button
    on selected_hover, hover:
        linear 1.0 rotate 359
        rotate 0
        repeat
    on selected_idle, idle:
        rotate 0



# [ SCREENS ]
screen file_slots(title):
    # Some 'ysize's in this screen are set to 'yvalue', if 'gui.text_size' is significantly smaller than the icon height (30px + 1px border). This helps to line up various edges
    # - It is recalculated each time the screen is shown, because some games permit the player to change 'gui.text_size' via the Preferences screen, or via the Accessibility screen
    $ yvalue = 32 if gui.text_size < 22 else int(gui.text_size * 1.5)
    if persistent.savesystem == "original":
        # Use the Ren'Py save system
        # - NOTE: files created by the Playthrough system will not be visible here, as that system is precluded from creating Playthroughs that are simply numbers (here, Pages)
        default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))
        use game_menu(title):
            fixed:
                # Added a button to switch to the Playthroughs system. This doesn't need to reference 'yvalue' because there is no text or edges around that need to be aligned with
                textbutton "{image=gui/playthroughview.png}":
                    tooltip "Switch to the Playthrough system"
                    text_align (0.5, 0.5)
                    if enable_animation:
                        at HoverSpin
                    else:
                        hover_background Solid(gui.text_color) padding (4, 4)
                    action SetVariable("persistent.savesystem", "playthroughs")
                order_reverse True
                # The page name
                button:
                    tooltip "Click to rename" style "page_label" xalign 0.5
                    key_events True
                    input style "page_label_text" value page_name_value
                    action page_name_value.Toggle()
                # The file slots
                grid gui.file_slot_cols gui.file_slot_rows:
                    style_prefix "slot" xalign 0.5 yalign 0.5 spacing gui.slot_spacing
                    for i in range(gui.file_slot_cols * gui.file_slot_rows):
                        $ slot = i + 1
                        button:
                            tooltip "{} {} Slot {}".format(title, "to" if title == "Save" else "from", slot)
                            action FileAction(slot)
                            has vbox
                            key "save_delete" action FileDelete(slot)
                            add FileScreenshot(slot) xalign 0.5
                            text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")) style "slot_time_text"
                            text FileSaveName(slot) style "slot_name_text"
                # Collect and display any active tooltip on this page
                $ help = GetTooltip()
                if help:
                    text help style "fileslots_input" italic True size gui.interface_text_size xalign 0.5 yalign 0.9
                # Page selection
                # TODO: Come up with a sensible solution to the page numbers getting too big. Test if current layout breaks if text too big? Is this what 'fixed:' solves?      - [EDIT:] Nope.
                # - [EDIT:] If gui.interface_text_size gets to 70 (someone might do it...) and the page number reaches 206 on a 1920x1080 screen, the right arrow disappears
                # - [EDIT:] Use the sizegroup property on the buttons? ATM repeatedly clicking the arrows will slowly expand/contract the hbox width, shuffling the arrows out from under the mouse
                # - [EDIT:] Suggest simply dividing the screen into fractions (20: {space} A <<< << < 1 2 3 4 5 6 7 8 9 10 > >> >>> Q {space} )
                # TODO: Ah! Use a 'side:' to keep the arrows and A/Q where they should be. The center area to be a viewport containing an hbox, which:
                #    - has the current page centered, and five? ten? size_group'd page_buttons either side. Buttons < 1 have no text and are NullActioned()
                hbox:
                    style_prefix "page" xalign 0.5 yalign 1.0 spacing gui.page_spacing
                    textbutton _("<"):
                        tooltip "View previous page"
                        action FilePagePrevious()
                    if config.has_autosave:
                        textbutton _("{#auto_page}A"):
                            tooltip "View Autosaves"
                            action FilePage("auto")
                    if config.has_quicksave:
                        textbutton _("{#quick_page}Q"):
                            tooltip "View Quicksaves"
                            action FilePage("quick")
                    # Make sure we show the correct and current page range (even if visiting auto/quick saves)
                    # TODO: See if we can't make the arrow buttons respect 'currentpage'; atm they will reset the whole range if clicked while viewing auto/quick
                    python:
                        global lastpage
                        currentpage = FileCurrentPage()
                        # Respect the last page viewed in the previous game session by not initialising 'lastpage' until we have a valid 'currentpage'
                        # WARNING: THIS IS THE LINE THAT THROWS AN EXCEPTION WHEN THE .RPY AND .RPYC FILES ARE DROPPED INTO CERTAIN DISTRIBUTED PROJECTS! (7.3.5 or below?) IT SAYS:
                        #   File "game/overridescreen-fileslots.rpy", line 363, in <module>
                        #       if lastpage == None: lastpage = int(currentpage) if currentpage.isdecimal() else 1
                        # AttributeError: 'str' object has no attribute 'isdecimal'
                        if lastpage == None: lastpage = int(currentpage) if currentpage.isdecimal() else 1
                        # Preserve the last numeric page viewed
                        currentpage = int(currentpage) if currentpage.isdecimal() else lastpage
                        lastpage = currentpage
                        # Set range bounds accordingly
                        maxpage = 10 if currentpage < 10 else currentpage + 1
                        minpage = 1 if currentpage < 10 else  currentpage - 8
                    for page in range(minpage, maxpage):
                        textbutton "[page]":
                            tooltip "View Page {}".format(page)
                            action FilePage(page)
                    textbutton _(">"):
                        tooltip "View next page"
                        action FilePageNext()
    else:
        # Use the Playthroughs save system
        python:
            # Make sure we're accessing the global variables
            global viewingptname, viewingpt
            # Check the validity of the playthrough name that we're viewing. If invalid, find the latest valid name. If none found, set 'viewingptname' to an empty string
            if ((config.has_autosave and viewingptname == "auto") or (config.has_quicksave and viewingptname == "quick") or (persistent.playthroughslist and viewingptname in persistent.playthroughslist)) == False:
                viewingptname = persistent.playthroughslist[-1] if persistent.playthroughslist else ""
            # Populate the viewed playthrough if 'viewingptname' is not an empty string - otherwise set it to None
            viewingpt = Playthrough(name=viewingptname) if viewingptname else None
        use game_menu(title):
            # Collect and display any active tooltip on this page
            $ help = GetTooltip()
            if help:
                text help style "fileslots_input" italic True size gui.interface_text_size line_leading -(gui.interface_text_size + 5) xalign 1.0 xoffset -(gui.scrollbar_size + 10) layout "nobreak"
            # NOTE: I'm not actually sure why there is a 'fixed' here, or even what it does, exactly?
            fixed:
                style_prefix "fileslots"
                # Two panels, side-by-side in an hbox: Playthroughs and Slots
                hbox:
                    # Playthroughs panel
                    vbox:
                        xsize 0.33
                        # This header and the panel below it are offset slightly to the left, to compensate for the width and spacing of the vertical scrollbar in the viewport below them
                        text "Playthroughs" color gui.interface_text_color size gui.label_text_size xalign 0.5 xoffset -round(gui.scrollbar_size * 1.33 / 2)
                        # Display top panel, which contains 1-4 buttons
                        hbox:
                            xalign 0.5 xoffset -round(gui.scrollbar_size * 1.33 / 2)
                            # Provide a button to switch to the original save system
                            button:
                                tooltip "Switch to the Ren'Py {} system".format(title)
                                xysize (yvalue, yvalue)
                                hover_background (None if enable_animation else Solid(gui.text_color))
                                text "{image=gui/renpyview.png}":
                                    align (0.5, 0.5)
                                    if enable_animation:
                                        at HoverSpin
                                action SetVariable("persistent.savesystem", "original")
                            if config.has_autosave:
                                textbutton  _("{#auto_page}A"):
                                    tooltip "{}".format("" if viewingptname == "auto" else "Show Autosaves")
                                    xysize (yvalue, yvalue) selected_background gui.text_color
                                    text_align (0.5, 0.5) text_selected_color gui.hover_color
                                    action [SetVariable("viewingptname", "auto"),
                                            SetVariable("viewingpt", Playthrough(name="auto"))]
                            if config.has_quicksave:
                                textbutton _("{#quick_page}Q"):
                                    tooltip "{}".format("" if viewingptname == "quick" else "Show Quicksaves")
                                    xysize (yvalue, yvalue) selected_background gui.text_color
                                    text_align (0.5, 0.5) text_selected_color gui.hover_color
                                    action [SetVariable("viewingptname", "quick"),
                                            SetVariable("viewingpt", Playthrough(name="quick"))]
                            # If we're on the Save screen, provide a button to allow the creation of a new, uniquely-named, playthrough that is also not simply a number (Ren'Py Pages)
                            if title == "Save":
                                button:
                                    tooltip "Create a new Playthrough"
                                    xysize (yvalue, yvalue)
                                    hover_background (None if enable_animation else Solid(gui.text_color))
                                    text "{image=gui/newplaythrough.png}":
                                        align (0.5, 0.5)
                                        if enable_animation:
                                            at HoverSpin
                                    action [SetVariable("targetaction", "newplaythroughname"),
                                            Show("querystring", query="{color=" + gui.interface_text_color + "}Please give this Playthrough a unique name:{/color}", excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
                                            AwaitUserInput()]
                        null height gui.text_size / 8
                        # Vertically-scrolling viewport for the list of Playthroughs
                        viewport:
                            scrollbars "vertical" mousewheel True spacing round(gui.scrollbar_size / 3)
                            vbox:
                                xfill True
                                # Display buttons for the contents of 'persistent.playthroughslist[]' in reverse order
                                for i in range(len(persistent.playthroughslist) - 1, -1, -1):
                                    # Using a side allows us to use xfill True or xsize 1.0 for the central button, without compromising the size of any end buttons or having to calculate around them
                                    side "l c r":
                                        # Rename button at the left, if we're dealing with the selected playthrough and 'enable_renaming' is True
                                        button:
                                            xysize (yvalue, yvalue)
                                            action NullAction()
                                            if persistent.playthroughslist[i] == viewingptname and enable_renaming:
                                                tooltip "Rename the \"{}\" Playthrough".format(viewingptname)
                                                hover_background (None if enable_animation else Solid(gui.text_color))
                                                text "{image=gui/rename.png}":
                                                    align (0.5, 0.5)
                                                    if enable_animation:
                                                        at HoverSpin
                                                action [SetVariable("targetaction", "changeplaythroughname"),
                                                        Show("querystring", query="{color=" + gui.interface_text_color + "}Please give this Playthrough a unique name:{/color}", preload=viewingptname, excludes="[{<>:\"/\|?*-", invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
                                                        AwaitUserInput()]
                                        # The name of the playthrough in the middle, which selects it if clicked. It's in a viewport so it can scroll horizontally if it's too large
                                        button:
                                            tooltip ("" if persistent.playthroughslist[i] == viewingptname else ("Show Slots in the \"" + persistent.playthroughslist[i] + "\" Playthrough"))
                                            xsize 1.0 ysize yvalue
                                            selected_background Solid(gui.text_color)
                                            viewport:
                                                xfill False align (0.5, 0.5) edgescroll (50, 500) #mousewheel "horizontal-change"       - [EDIT:] Alternative scrolling option
                                                text " {} ".format(persistent.playthroughslist[i]):
                                                    layout "nobreak"
                                                    hover_color gui.hover_color color (gui.hover_color if persistent.playthroughslist[i] == viewingptname else gui.text_color)
                                            action [SetVariable("viewingptname", persistent.playthroughslist[i]),
                                                    SetVariable("viewingpt", Playthrough(name=persistent.playthroughslist[i]))]
                                        # Delete button at the right, if we're dealing with the selected playthrough
                                        button:
                                            xysize (yvalue, yvalue)
                                            action NullAction()
                                            if persistent.playthroughslist[i] == viewingptname:
                                                tooltip "Delete the \"{}\" Playthrough".format(viewingptname)
                                                hover_background (None if enable_animation else Solid(gui.text_color))
                                                text "{image=gui/delete.png}":
                                                    align (0.5, 0.5)
                                                    if enable_animation:
                                                        at HoverSpin
                                                action Confirm("Are you sure you want to delete this Playthrough?\n{}{}".format("{size=" + str(gui.notify_text_size) + "}{color=" + str(gui.insensitive_color) + "}\nLocked Slots: " + str(viewingpt.lockcount) + "{/color}{/size}" if viewingpt.lockcount else "", "{size=" + str(gui.notify_text_size) + "}{color=" + str(gui.insensitive_color) + "}\nSlots from a later version: " + str(viewingpt.higherversioncount) + "{/color}{/size}" if viewingpt.higherversioncount else ""), yes=Function(DeletePlaythrough), confirm_selected=True)
#
#                                # Test playthroughs for layout verification
#                                for i in range(1, 51, 1):
#                                    button:
#                                        tooltip "Show Slots in the \"{:02}\" Playthrough".format(i) xsize 1.0 ysize yvalue
#                                        action NullAction()
#                                        viewport:
#                                            xfill False xmaximum 0.856 align (0.5, 0.5) mousewheel "horizontal-change" #edgescroll (50, 500)
#                                            text "{:02}".format(i) align (0.5, 0.5) layout "nobreak" hover_color gui.hover_color
#                                        hover_background Solid(gui.text_color, xsize=0.856, align=(0.5, 0.5), ysize=yvalue)
#                                        textbutton "{image=gui/delete.png}" tooltip "Delete the \"{:02}\" Playthrough".format(i) align (0.0, 0.5) text_align (0.5, 0.5) text_anchor (16, 16) ysize yvalue hover_background Solid(gui.text_color) action NullAction()
#                                        textbutton "{image=gui/rename.png}" tooltip "Rename the \"{:02}\" Playthrough".format(i) align (1.0, 0.5) text_align (0.5, 0.5) text_anchor (16, 16) ysize yvalue hover_background Solid(gui.text_color) action NullAction()
#
                    # Horizontal spacer
                    null width 60
                    # Fileslots panel
                    vbox:
                        xsize 1.0
                        text "Slots" color gui.interface_text_color size gui.label_text_size
                        # Provide (or not) buttons that alter the key that the slotslist is sorted on
                        # TODO: See if I can't tighten this up. It might not need to have all those properties specified
                        hbox:
                            if enable_sorting and viewingptname and viewingptname != "auto" and viewingptname != "quick":
                                textbutton " Recent ":
                                    tooltip "Sort slots by most recently changed first"
                                    text_align (0.5, 0.5) align (0.5, 0.5) ysize yvalue
                                    selected_background gui.text_color text_selected_color gui.hover_color
                                    action [SetVariable("persistent.sortby", "lastmodified"),
                                            viewingpt.SortSlots]
                                textbutton " Number ":
                                    tooltip "Sort slots by highest slot number first"
                                    text_align (0.5, 0.5) align (0.5, 0.5) ysize yvalue
                                    selected_background gui.text_color text_selected_color gui.hover_color
                                    action [SetVariable("persistent.sortby", "slotnumber"),
                                            viewingpt.SortSlots]
                            null height yvalue
                        null height gui.text_size / 8
                        # Vertically-scrolling viewport for the slotslist
                        viewport:
                            scrollbars "vertical" mousewheel True spacing round(gui.scrollbar_size / 3)
                            vbox:
                                xsize 1.0
                                # Display all the fileslots that are in the playthrough being viewed, keyed off 'viewingptname'. If no playthrough is being viewed, display nothing
                                if viewingptname != "":
                                    # For each slot in the Playthrough...
                                    for slot in viewingpt.slots:
                                        # ...deconstruct the list...
                                        python:
                                            filename, lastmodified, slotnumber, versionnumber, editablename, lockedstatus = slot
                                            slotnumber = int(slotnumber) if slotnumber.isdecimal() else 0
                                            slotname = editablename if enable_renaming and editablename else "{} {}".format(viewingptname, slotnumber if slotnumber else "[[{} to {}]".format(lastmodified, versionnumber))
                                            textcolor = gui.text_color
                                        # ...and turn it into a slotbutton with details and sub-buttons
                                        # Handle any slot which has been inserted into the list for the purpose of creating a new save, and therefore is not yet a disk file:
                                        if filename == "+ New Save +":
                                            # Only produce the button if we're on the Save screen
                                            # - NOTE: "auto"/"quick" 'playthrough's will not have been given any "+ New Save +" slots, so they *shouldn't* ever reach this code...
                                            if title == "Save":
                                                textbutton "+ New Save +":
                                                    tooltip "Create a new save: {}".format(slotname)
                                                    xsize 1.0 ysize config.thumbnail_height text_align (0.5, 0.5)
                                                    background slotbackground hover_foreground Frame("gui/emptyframe.png")
                                                    action [SetVariable("targetaction", "newslotnumber"),
                                                            If(slotnumber, true=SetVariable("userinput", slotnumber), false=Show("querynumber", query="{color="+gui.interface_text_color+"}Please select a slot number:{/color}", preload=str(lastmodified), minval=lastmodified, maxval=versionnumber, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots")),
                                                            AwaitUserInput()]
                                        # Disable any slot that has a version number higher than this app; loading will likely fail and overwriting will likely lose data
                                        # - NOTE: In theory, 'versionnumber' could be type int. However, that should only happen if 'filename' == "+ New Save +" - which is already handled, above
                                        elif versionnumber.lower() > config.version.lower():
                                            if enable_versioning:
                                                $ textcolor = gui.insensitive_color
                                                textbutton "{} - Version {}".format(editablename, versionnumber):
                                                    sensitive False
                                                    xsize 1.0 ysize config.thumbnail_height text_align (0.5, 0.5)
                                                    background slotbackground
                                                    action NullAction()
                                        # Everything else should all be pre-existing disk files that need to be shown
                                        else:
                                            button:
                                                tooltip "{} {}".format("Load" if title == "Load" else "Overwrite", slotname)
                                                xsize 1.0 ysize config.thumbnail_height
                                                background slotbackground hover_foreground Frame("gui/emptyframe.png")
                                                action [MakePtLast,
                                                        If(title == "Save", false=FileLoad(filename, slot=True), true=FileSave("{}-{:05}-{}-{}-Unlocked".format(viewingptname, slotnumber, config.version, editablename) if viewingptname != "auto" and viewingptname != "quick" else "{}-{}".format(viewingptname, slotnumber), slot=True))]
                                                if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                                    key "save_delete" action FileDelete(filename, slot=True)
                                                if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                                    tooltip "{} {}".format("Attempt to load" if title == "Load" else "Overwrite", slotname)
                                                if title == "Save" and (viewingptname == "auto" or (enable_locking and lockedstatus == "LOCKED")):
                                                    sensitive False
                                                    $ textcolor = gui.insensitive_color
                                                hbox:
                                                    # Thumbnail on the left. Setting it as a background to a frame permits regular content to appear overlaid, if needed
                                                    frame:
                                                        xsize config.thumbnail_width ysize config.thumbnail_height
                                                        background FileScreenshot(filename, slot=True)
                                                        # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                                                        if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                                            add Solid("#000000CF")
                                                            vbox:
                                                                at truecenter
                                                                text "- Older Save -" xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                                                null height gui.slot_button_text_size
                                                                text "v{}".format(versionnumber) xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                                    null width gui.scrollbar_size
                                                    viewport:
                                                        scrollbars "vertical" mousewheel "change"
                                                        align (0.5, 0.5) xmaximum 0.98 ymaximum 0.99
                                                        vbox:
                                                            align (0.5, 0.5) xfill True #box_wrap True
                                                            viewport:
                                                                # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
                                                                # TODO: Why the **** do we occasionally wind up with a weird scrollbar?!? o7
                                                                # - [EDIT:] To reproduce this: screen size of 1920x1080, text size 33 and an 'editablename' of "James and the Giant Peach by R Dahl"
                                                                #           - or a text size of 66 and a Playthrough name of "Test", then hit the '+ New Save +' button
                                                                # - [EDIT:] Adding the HoverSpin transform to the icons has also made all of the buttons gain the weird scrollbar...
                                                                #    - [EDIT:] Restructuring the button using 'side:' may help. That 'ymaximum' probably doesn't help, either
                                                                #       - [EDIT:] There is an attempt at this commented out, below...
                                                                edgescroll (100, 500) #mousewheel "horizontal-change"
                                                                xfill False align (0.5, 0.5)
                                                                text "{}".format(slotname) color textcolor align (0.5, 0.5) text_align 0.5 layout "subtitle"
                                                            null height 10
                                                            text "{}".format(FileTime(filename, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True)) xalign 0.5 size gui.slot_button_text_size color textcolor
                                                            null height 10
                                                            # Icon buttons
                                                            hbox:
                                                                xalign 0.5
                                                                # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                                                                if enable_renaming and editablename and (enable_locking == False or (enable_locking and lockedstatus != "LOCKED")):
                                                                    button:
                                                                        tooltip "Rename {}".format(slotname)
                                                                        hover_background (None if enable_animation else Solid(gui.text_color))
                                                                        text "{image=gui/rename.png}":
                                                                            align (0.5, 0.5)
                                                                            if enable_animation:
                                                                                at HoverSpin
                                                                        action [SetVariable("targetaction", "changeslotname"),
                                                                                SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, lockedstatus]),
                                                                                Show("querystring", query="{color="+gui.interface_text_color+"}Please enter the slot name:{/color}", preload=editablename, excludes="[{<>:\"/\|?*-", maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
                                                                                AwaitUserInput()]
                                                                if enable_locking and lockedstatus:
                                                                    button:
                                                                        tooltip "{} {}".format("Unlock" if lockedstatus == "LOCKED" else "Lock", slotname)
                                                                        hover_background (None if enable_animation else Solid(gui.text_color))
                                                                        text "{}".format("{image=gui/locked.png}" if lockedstatus == "LOCKED" else "{image=gui/unlocked.png}"):
                                                                            align (0.5, 0.5)
                                                                            if enable_animation:
                                                                                at HoverSpin
                                                                        action [SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, "Unlocked" if lockedstatus == "LOCKED" else "LOCKED"]),
                                                                                ReflectSlotChanges]
                                                                if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                                                    button:
                                                                        tooltip "Delete {}".format(slotname)
                                                                        hover_background (None if enable_animation else Solid(gui.text_color))
                                                                        text "{image=gui/delete.png}":
                                                                            align (0.5, 0.5)
                                                                            if enable_animation:
                                                                                at HoverSpin
                                                                        action FileDelete(filename, slot=True)
#
#                                                # TODO: Test using 'side:' to structure this button more robustly
#                                                side "l c":
#                                                    # Thumbnail on the left. Setting it as a background to a frame permits regular content to appear overlaid, if needed
#                                                    frame:
#                                                        xsize config.thumbnail_width ysize config.thumbnail_height
#                                                        background FileScreenshot(filename, slot=True)
#                                                        # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
#                                                        if enable_versioning and versionnumber != "" and versionnumber != config.version:
#                                                            add Solid("#000000CF")
#                                                            vbox:
#                                                                at truecenter
#                                                                text "- Older Save -" xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
#                                                                null height gui.slot_button_text_size
#                                                                text "v{}".format(versionnumber) xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
#                                                    # Slot data and options
#                                                    viewport:
#                                                        xfill False yfill True xsize 0.98 edgescroll (100, 500) at truecenter
#                                                        side "b c":
#                                                            # Timestamp and Icon buttons
#                                                            vbox:
#                                                                at truecenter
#                                                                null height 10
#                                                                text "{}".format(FileTime(filename, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True)):
#                                                                    xalign 0.5 size gui.slot_button_text_size color textcolor layout "nobreak"
#                                                                null height 10
#                                                                hbox:
#                                                                    xalign 0.5
#                                                                    # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
#                                                                    if enable_renaming and editablename and (enable_locking == False or (enable_locking and lockedstatus != "LOCKED")):
#                                                                        button:
#                                                                            tooltip "Rename {}".format(slotname)
#                                                                            hover_background (None if enable_animation else Solid(gui.text_color))
#                                                                            text "{image=gui/rename.png}":
#                                                                                align (0.5, 0.5)
#                                                                                if enable_animation:
#                                                                                    at HoverSpin
#                                                                            action [SetVariable("targetaction", "changeslotname"),
#                                                                                    SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, lockedstatus]),
#                                                                                    Show("querystring", query="{color="+gui.interface_text_color+"}Please enter the slot name:{/color}", preload=editablename, excludes="[{<>:\"/\|?*-", maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
#                                                                                    AwaitUserInput()]
#                                                                    if enable_locking and lockedstatus:
#                                                                        button:
#                                                                            tooltip "{} {}".format("Unlock" if lockedstatus == "LOCKED" else "Lock", slotname)
#                                                                            hover_background (None if enable_animation else Solid(gui.text_color))
#                                                                            text "{}".format("{image=gui/locked.png}" if lockedstatus == "LOCKED" else "{image=gui/unlocked.png}"):
#                                                                                align (0.5, 0.5)
#                                                                                if enable_animation:
#                                                                                    at HoverSpin
#                                                                            action [SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, "Unlocked" if lockedstatus == "LOCKED" else "LOCKED"]),
#                                                                                    ReflectSlotChanges]
#                                                                    if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
#                                                                        button:
#                                                                            tooltip "Delete {}".format(slotname)
#                                                                            hover_background (None if enable_animation else Solid(gui.text_color))
#                                                                            text "{image=gui/delete.png}":
#                                                                                align (0.5, 0.5)
#                                                                                if enable_animation:
#                                                                                    at HoverSpin
#                                                                            action FileDelete(filename, slot=True)
#                                                            # The name of the slot. Since this could be lengthy and/or a large font, we need to make it fit gracefully
#                                                            viewport:
#                                                                xfill False at truecenter
#                                                                # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
#                                                                edgescroll (100, 500)
#                                                                #mousewheel "horizontal-change"
#                                                                text "{}".format(slotname) color textcolor align (0.5, 0.5) layout "subtitle" text_align 0.5
#
                                        # Spacer between save slots. Can be commented out if desired
                                        null height round(gui.scrollbar_size / 3)



# [ ADDITIONAL SCREENS ]

# { SUPPORT SCREEN } - Provides the query_ screens with a degree of wrapping
# - container     : [optional] : an (x, y, xsize, ysize) tuple specifying the area that the input box will be centered in
# - bground       : [optional] : a Displayable for the background property of the largest non-transparent Frame(), which will be scaled to fit
# - query         : [optional] : a string containing the question to put to the player
screen queryframe(container=(0, 0, config.screen_width, config.screen_height), bground=None, query="Hmm?"):
    frame:
        area container background "gui/overlay/confirm.png"
        frame:
            at truecenter background bground xfill False yfill False padding (50, 50)
            frame:
                at truecenter xfill False yfill False
                vbox:
                    text query xalign 0.5 size gui.label_text_size
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
            size_group "ccbuttons" text_align (0.5, 0.5)
            if isvalid == False:
                sensitive False
            action (SetVariable(variable, newvalue), Hide(callingscreen))
        null width gui.text_size
        textbutton "Cancel" size_group "ccbuttons" text_align (0.5, 0.5) action Hide(callingscreen)
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
screen querystring(query="Hmm?", preload="", excludes="[{", invalid=[], maxcharlen=None, maxpixelwidth=None, variable=None, container=(0, 0, config.screen_width, config.screen_height), bground=None, styleprefix=None, tcolor=None):
    style_prefix styleprefix
    if variable is None:
        $ raise Exception("Invalid argument - screen querystring([required] variable=\"variable_name\"):")
    modal True
    default currentstring = preload
    use queryframe(container=container, bground=bground, query=query):
        if excludes != "[{":
            text "Forbidden characters: [excludes!q]" xalign 0.5 size gui.notify_text_size color gui.insensitive_color
        null height gui.text_size
        input:
            value ScreenVariableInputValue("currentstring", default=True, returnable=False)
            default preload exclude excludes length maxcharlen pixel_width maxpixelwidth xalign 0.5
            if tcolor is not None:
                color tcolor
        # Assume validity unless tested otherwise
        python:
            global targetaction
            isvalid = True
            if invalid != [] and currentstring in invalid: isvalid = False
            # Conditional invalidation based on purpose of input can go here:
            # - If 'targetaction' is "newplaythroughname" or "changeplaythroughname", we need to prevent it from being an integer (because these are Ren'Py save system Page names)
            if (targetaction == "newplaythroughname" or targetaction == "changeplaythroughname") and currentstring.isdecimal(): isvalid = False
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
screen querynumber(query="Hmm?", preload="", minval=None, maxval=None, variable=None, container=(0, 0, config.screen_width, config.screen_height), bground=None, styleprefix=None, tcolor=None):
    style_prefix styleprefix
    if variable is None:
        $ raise Exception("Invalid argument - screen querystring([required] variable=\"variable_name\"):")
    modal True
    default currentnumber = preload     # This is the variable attached to the input field, and automatically updated by it. It's a string
    default permitted = "0123456789"    # These are the characters accepted by the input field
    use queryframe(container=container, bground=bground, query=query):
        if minval or maxval:
            text "{} {} {}".format(minval if minval else maxval, "through" if minval and maxval else "or", maxval if minval and maxval else ("more" if minval else "less")) xalign 0.5 size gui.notify_text_size color gui.insensitive_color
        null height gui.text_size
        # Add the input, and store the results in 'currentnumber'. Field is editable, hitting return does nothing, and the only permitted characters are the ones found in 'permitted'
        input:
            value ScreenVariableInputValue("currentnumber", default=True, returnable=False)
            xalign 0.5 default preload allow permitted
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
