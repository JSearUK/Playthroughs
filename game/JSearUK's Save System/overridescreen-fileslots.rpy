define config.developer = True

# [ INITIALISATION - BEST TO LEAVE ALONE ]
default persistent.save_system = "original"
default persistent.sortby = "last_modified"
default persistent.playthroughs = []
default persistent.current_playthrough = None

# When exiting the game menu, or after loading, clear the variables that store the details of the playthrough being viewed. Do this by re-assigning a custom transition to those events
# - NOTE: The specified duration needs to be greater than zero for the function to be called. Any transition where a function can be specified may be used
# - NOTE: These lines re-initialise defines. This is not best practice, but it does mean that we can keep all of the changes of this mod to one file, and avoid altering further screens
# - NOTE: If this behaviour is not desired, simply comment out the three lines below


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
define enable_sorting = True
    # This enables the player to sort Playthrough slotlists on a specified key. It ships with "lastmodified" and "slotnumber" by default; "versionnumber" and "lockedstatus" may also be of use
define enable_animation = False
    # This determines the hover behaviour of the icons in the UI: True will make the icons spin, False will highlight their background
    # WARNING: At the moment, this makes the icons in the save slots somehow cause the viewport to show an unscrollable scrollbar, despite there being lots of room
define slotbackground = None #Solid("FFF1")
    # This is what is shown behind each slot, and can be any Displayable or None. Either hard-code it, or use a binding defined at a lower init level
    # - NOTE: Displayables are usually defined within a Frame in order to be scaled correctly, e.g. Frame("gui/nvl.png"). There are exceptions, such as Color() or Solid()
    # - NOTE: None is the default, removing the background, resulting in total transparency

# [ CLASSES ]
python early:

    # Reference: (https://www.renpy.org/doc/html/save_load_rollback.html#save-functions-and-variables)
    class Playthrough:
        """The Playthrough class (summary line)

        The playthrough class stores the name of the play through and a list of saves for that playthrough (detailed line)

        Attributes:
            attribute1_EXAMPLE (data type): Description of attribute1
            name (str): The name of the playthrough
            lock_count (int): The count of the number of saves locked
            higher_version_count (int): The count of the number of slots with a higher version than config.version

        """
        # WARNING: New instances of this object are created frequently, albeit assigned to the same variable. I'm going to assume the garbage collector frees up previously allocated memory
        # NOTE: I may need to find a way to determine if this is happening correctly. Failing that, I expect that there is a way to explicitly release the previous object
        # [EDIT:] I read this (https://stackify.com/python-garbage-collection/). This suggests I don't need to worry about it, and provides a profiler should I feel the need to check


        def __init__(self, name):
            self.name = name

            # self.lock_count = [slot.version for slot in self.slots].count("LOCKED")
            self.lock_count = 0
            # self.higher_version_count = [slot.version.lower() > config.version.lower() for slot in self.slots].count(True)
            self.higher_version_count = 0

            persistent.playthroughs.append(self)
            persistent.current_playthrough = self

        def __eq__(self, other):
            if isinstance(other, Playthrough):
                return self.name == other.name
            return False

        def __ne__(self, other):
            return not self.__eq__(other)

        @property
        def slots(self):
            """:obj:`set` of :obj:`SaveInfo`: Returns the collection of slots for this playthrough."""
            slots = set()
            saves = renpy.list_saved_games("^" + self.name + "-", fast=True)

            for save in saves:
                slot_json = renpy.slot_json(save)
                save_split = save.split('-')

                save_info = SaveInfo(save, renpy.slot_mtime(save), save_split[1], slot_json["_version"], slot_json["_save_name"], "UNLOCKED")
                slots.add(save_info)

            return slots

        @property
        def sorted_slots(self):
            """:obj:`list` of :obj:`SaveInfo`: Returns a sorted list of SaveInfo objects"""
            return sorted(self.slots, key=lambda x: getattr(x, persistent.sortby), reverse=True)

        def create_save(self):
            """Creates a save with a playthrough style filename"""
            filename = "{}-{}".format(self.name, len(self.slots)+1)
            renpy.save(filename, extra_info=save_name)
            # Move playthrough to end of "playthroughs"
            persistent.playthroughs.append(persistent.playthroughs.pop(persistent.playthroughs.index(self)))

        def delete(self):
            """Deletes all saves in playthrough, removes playthrough from parent list, and then deletes its reference"""
            for slot in self.slots:
                renpy.unlink_save(slot.file_name)
            persistent.playthroughs.remove(self)
            del self

    class SaveInfo:
        """A data class for storing info of a save.

        Attributes:
            file_name (str): The name of the save file.
            last_modified (int): The epoch time when the save was last modified.
            slot_num (str): The position of the save slot.
            version (str): The version the save was played on.
            name (str): The name of the save.
            locked_status (str): Whether the save is 'LOCKED' or 'UNLOCKED'.

        """
        
        def __init__(self, file_name, last_modified, slot_num, version, name, locked_status):
            self.file_name = file_name
            self.last_modified = last_modified
            self.slot_num = slot_num
            self.version = version
            self.name = name
            self.locked_status = locked_status

# [ FUNCTIONS ]
init -1 python:
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

    def AwaitUserInput():
        # This is an all-purpose function that is called whenever user-input is required to progress with an Action list; it defers the changes to be made until there is actually an input
        # - NOTE: I don't know how to make an action list wait for input and then resume; this is a workaround that calls this function once per screen update... I think
            # TODO: Figure out if "call in new context" is the designed solution to this problem, and how to achieve it
        global userinput, targetaction, viewingptname, viewingpt, slotdetails
        # The first thing to do is quit out unless there is something that actually needs processing
        if userinput:
            # Be sure we're dealing with a string. Pretty much anything will convert to a string - even objects. Also, using 'str()' on a string does not throw an exception, which is nice
            userinput = str(userinput)

            if targetaction == "changeslotname":
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
# The original save/load system
screen file_slots(title):
    if persistent.save_system == "original":
        use original_file_slots(title=title)
    elif persistent.save_system == "playthrough":
        use playthrough_file_slots(title=title)

screen original_file_slots(title):
    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):
        fixed:
            # Added a button to switch to the Playthroughs system. This doesn't need to reference 'yvalue' because there is no text or edges around that need to be aligned with
            imagebutton:
                action SetVariable("persistent.save_system", "playthrough")
                idle "JSearUK's Save System/gui/playthroughview.png"
                tooltip "Switch to the Playthrough system"
                hover_background (None if enable_animation else Solid(gui.text_color))

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

                tooltip "Click to rename"
                
            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                align (0.5, 0.5)

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

                        tooltip "{} {} Slot {}".format(title, "to" if title == "Save" else "from", slot)

            # Collect and display any active tooltip on this page
            $ help = GetTooltip()
            if help:
                text help:
                    style "fileslots_input"
                    italic True
                    size gui.interface_text_size
                    align (0.5, 0.9)
            
            # Page selection
            # TODO: Come up with a sensible solution to the page numbers getting too big. Test if current layout breaks if text too big? Is this what 'fixed:' solves?      - [EDIT:] Nope.
            # - [EDIT:] If gui.interface_text_size gets to 70 (someone might do it...) and the page number reaches 206 on a 1920x1080 screen, the right arrow disappears
            # - [EDIT:] Use the sizegroup property on the buttons? ATM repeatedly clicking the arrows will slowly expand/contract the hbox width, shuffling the arrows out from under the mouse
            # - [EDIT:] Suggest simply dividing the screen into fractions (20: {space} A <<< << < 1 2 3 4 5 6 7 8 9 10 > >> >>> Q {space} )
            # TODO: Ah! Use a 'side:' to keep the arrows and A/Q where they should be. The center area to be a viewport containing an hbox, which:
            #    - has the current page centered, and five? ten? size_group'd page_buttons either side. Buttons < 1 have no text and are NullActioned()
            hbox:
                style_prefix "page"
                
                align (0.5, 1.0)
                
                spacing gui.page_spacing
                
                textbutton _("<") action FilePagePrevious() tooltip "View previous page"

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto") tooltip "View Autosaves"
                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick") tooltip "View Quicksaves"
                        
                # Make sure we show the correct and current page range (even if visiting auto/quick saves)
                # TODO: See if we can't make the arrow buttons respect 'currentpage'; atm they will reset the whole range if clicked while viewing auto/quick
                python:
                    try:
                        lower_range = max(1, int(persistent._file_page) - 8)
                        upper_range = max(10, int(persistent._file_page) + 1)
                    except ValueError:
                        lower_range = 1
                        upper_range = 10

                for page in range(lower_range, upper_range):
                    textbutton "[page]" action FilePage(page) tooltip "View Page {}".format(page)

                textbutton _(">"):
                    tooltip "View next page"
                    action FilePageNext()

# New playthrough system
screen playthrough_file_slots(title):
    # Some 'ysize's in this screen are set to 'yvalue', if 'gui.text_size' is significantly smaller than the icon height (30px + 1px border). This helps to line up various edges
    # - It is recalculated each time the screen is shown, because some games permit the player to change 'gui.text_size' via the Preferences screen, or via the Accessibility screen
    $ yvalue = 32 if gui.text_size < 22 else int(gui.text_size * 1.5)
    # - NOTE: files created by the Playthrough system will not be visible here, as that system is precluded from creating Playthroughs that are simply numbers (here, Pages)
    # Use the Playthroughs save system

    use game_menu(title):
        # Collect and display any active tooltip on this page
        $ help = GetTooltip()
        if help:
            text help:
                style "fileslots_input"
                italic True
                size gui.interface_text_size
                pos (50, -50)

        # NOTE: I'm not actually sure why there is a 'fixed' here, or even what it does, exactly?
        fixed:
            style_prefix "fileslots"
            # Two panels, side-by-side in an hbox: Playthroughs and Slots
            hbox:
                spacing 50
                # Playthroughs panel
                vbox:
                    xsize 0.33
                    spacing 3

                    # This header and the panel below it are offset slightly to the left, to compensate for the width and spacing of the vertical scrollbar in the viewport below them
                    text "Playthroughs":
                        color gui.interface_text_color
                        size gui.label_text_size
                        xalign 0.5

                    # Display top panel, which contains 1-4 buttons
                    hbox:
                        xalign 0.5
                        spacing 10

                        # Provide a button to switch to the original save system
                        imagebutton:
                            action SetField(persistent, "save_system", "original")
                            idle "JSearUK's Save System/gui/renpyview.png"
                            hover_background (None if enable_animation else Solid(gui.text_color))
                            if enable_animation:
                                at HoverSpin
                            tooltip "Switch to the Ren'Py [title] system"
                            
                        if config.has_autosave:
                            textbutton  _("{#auto_page}A"):
                                tooltip "Show Autosaves"
                                text_selected_color gui.hover_color
                                action SetField(persistent, "current_playthrough", "auto")

                        if config.has_quicksave:
                            textbutton _("{#quick_page}Q"):
                                tooltip "Show Quicksaves"
                                text_selected_color gui.hover_color
                                action SetField(persistent, "current_playthrough", "quick")

                        # If we're on the Save screen, provide a button to allow the creation of a new, uniquely-named, playthrough that is also not simply a number (Ren'Py Pages)
                        if title == "Save":
                            imagebutton:
                                tooltip "Create a new Playthrough"
                                idle "JSearUK's Save System/gui/newplaythrough.png"
                                hover_background (None if enable_animation else Solid(gui.text_color))
                                if enable_animation:
                                    at HoverSpin
                                action Show("playthrough_input")

                    # Vertically-scrolling viewport for the list of Playthroughs
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        spacing 5

                        vbox:
                            # Display buttons for the contents of 'persistent.playthroughslist[]' in reverse order
                            for playthrough in reversed(persistent.playthroughs):
                                # # Using a side allows us to use xfill True or xsize 1.0 for the central button, without compromising the size of any end buttons or having to calculate around them
                                hbox:
                                    xfill True

                                    if enable_renaming:
                                        imagebutton:
                                            idle "JSearUK's Save System/gui/rename.png"
                                            hover_background (None if enable_animation else Solid(gui.text_color))
                                            if enable_animation:
                                                at HoverSpin
                                            action Show("playthrough_input", playthrough=playthrough)
                                            tooltip "Rename the \"[playthrough.name]\" Playthrough"

                                    textbutton playthrough.name:
                                        tooltip "Show Slots in the \"[playthrough.name]\" Playthrough"
                                        selected_background Solid(gui.text_color)
                                        text_hover_color gui.hover_color
                                        action SetField(persistent, "current_playthrough", playthrough)
                                        align (0.5, 0.5)

                                    imagebutton:
                                        tooltip "Delete the \"[playthrough.name]\" Playthrough"
                                        idle "JSearUK's Save System/gui/delete.png"
                                        hover_background (None if enable_animation else Solid(gui.text_color))
                                        if enable_animation:
                                            at HoverSpin
                                        action Confirm("Are you sure you want to delete this Playthrough?", Function(playthrough.delete), confirm_selected=True)
                                        xalign 1.0

                # Fileslots panel
                vbox:
                    xfill True

                    text "Slots":
                        color gui.interface_text_color
                        size gui.label_text_size
                    # Provide (or not) buttons that alter the key that the slotslist is sorted on
                    # TODO: See if I can't tighten this up. It might not need to have all those properties specified
                    if persistent.current_playthrough:
                        hbox:
                            spacing 20

                            if enable_sorting:
                                textbutton "Recent":
                                    tooltip "Sort slots by most recently changed first"
                                    align (0.5, 0.5)
                                    selected_background gui.text_color
                                    text_selected_color gui.hover_color
                                    action [SetField(persistent, "sortby", "last_modified")]

                                textbutton "Number":
                                    tooltip "Sort slots by highest slot number first"
                                    align (0.5, 0.5)
                                    selected_background gui.text_color
                                    text_selected_color gui.hover_color
                                    action [SetField(persistent, "sortby", "slot_num")]

                        # Vertically-scrolling viewport for the slotslist
                        viewport:
                            scrollbars "vertical"
                            mousewheel True

                            vbox:
                                # Display all the fileslots that are in the playthrough being viewed, keyed off 'viewingptname'. If no playthrough is being viewed, display nothing
                                    # For each slot in the Playthrough...
                                for slot in persistent.current_playthrough.sorted_slots:
                                    if slot.version > config.version and enable_versioning:
                                        textbutton "[slot.name] - Version [slot.version]":
                                            xysize (1.0, config.thumbnail_height)
                                            background slotbackground
                                            action NullAction()

                                    else:
                                        button:
                                            if title == "Save":
                                                tooltip "Overwrite [slot.name]"
                                                action Show("new_save_slot", playthrough=persistent.current_playthrough)
                                            elif title == "Load":
                                                tooltip "Load [slot.name]"
                                                action FileLoad(slot.file_name, slot=True)
                                            xysize(1.0, config.thumbnail_height)
                                            background slotbackground
                                            hover_foreground Frame("JSearUK's Save System/gui/emptyframe.png")

                                    # ...deconstruct the list...
                                    # python:
                                    #     try: slotnumber = int(slot.slot_num)
                                    #     except ValueError: slotnumber = 0
                                    #     slotname = slot.name if enable_renaming and slot.name else "{} {}".format(current_playthrough, slotnumber if slotnumber else "[[{} to {}]".format(slot.last_modified, slot.version))
                                    #     textcolor = gui.text_color
                                    # ...and turn it into a slotbutton with details and sub-buttons
                                    # Handle any slot which has been inserted into the list for the purpose of creating a new save, and therefore is not yet a disk file:

                                    # Disable any slot that has a version number higher than this app; loading will likely fail and overwriting will likely lose data
                                    # - NOTE: In theory, 'versionnumber' could be type int. However, that should only happen if 'filename' == "+ New Save +" - which is already handled, above
                                    # if slot.version.lower() > config.version.lower():

                                    # Everything else should all be pre-existing disk files that need to be shown
                                    # else:
                                        # button:
                                        #     tooltip "{} {}".format("Load" if title == "Load" else "Overwrite", slotname)
                                        #     xsize 1.0 ysize config.thumbnail_height
                                        #     background slotbackground hover_foreground Frame("JSearUK's Save System/gui/emptyframe.png")
                                        #     action [MakePtLast,
                                        #             If(title == "Save", false=FileLoad(slot.file_name, slot=True), true=FileSave("{}-{:05}-{}-{}-Unlocked".format(current_playthrough, slotnumber, config.version, slot.name) if current_playthrough != "auto" and current_playthrough != "quick" else "{}-{}".format(current_playthrough, slotnumber), slot=True))]
                                        #     if enable_locking == False or (enable_locking and slot.locked_status != "LOCKED"):
                                        #         key "save_delete" action FileDelete(slot.file_name, slot=True)
                                        #     if enable_versioning and slot.version != "" and slot.version != config.version:
                                        #         tooltip "{} {}".format("Attempt to load" if title == "Load" else "Overwrite", slotname)
                                        #     if title == "Save" and (current_playthrough == "auto" or (enable_locking and slot.locked_status == "LOCKED")):
                                        #         sensitive False
                                        #         $ textcolor = gui.insensitive_color
                                        #     hbox:
                                        #         # Thumbnail on the left. Setting it as a background to a frame permits regular content to appear overlaid, if needed
                                        #         frame:
                                        #             xsize config.thumbnail_width ysize config.thumbnail_height
                                        #             background FileScreenshot(slot.file_name, slot=True)
                                        #             # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                                        #             if enable_versioning and slot.version != "" and slot.version != config.version:
                                        #                 add Solid("#000000CF")
                                        #                 vbox:
                                        #                     at truecenter
                                        #                     text "- Older Save -" xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                        #                     null height gui.slot_button_text_size
                                        #                     text "v{}".format(slot.version) xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                        #         null width gui.scrollbar_size
                                        #         viewport:
                                        #             scrollbars "vertical" mousewheel "change"
                                        #             align (0.5, 0.5) xmaximum 0.98 ymaximum 0.99
                                        #             vbox:
                                        #                 align (0.5, 0.5) xfill True #box_wrap True
                                        #                 viewport:
                                        #                     # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
                                        #                     # TODO: Why the **** do we occasionally wind up with a weird scrollbar?!? o7
                                        #                     # - [EDIT:] To reproduce this: screen size of 1920x1080, text size 33 and an 'editablename' of "James and the Giant Peach by R Dahl"
                                        #                     #           - or a text size of 66 and a Playthrough name of "Test", then hit the '+ New Save +' button
                                        #                     # - [EDIT:] Adding the HoverSpin transform to the icons has also made all of the buttons gain the weird scrollbar...
                                        #                     #    - [EDIT:] Restructuring the button using 'side:' may help. That 'ymaximum' probably doesn't help, either
                                        #                     #       - [EDIT:] There is an attempt at this commented out, below...
                                        #                     edgescroll (100, 500) #mousewheel "horizontal-change"
                                        #                     xfill False align (0.5, 0.5)
                                        #                     text "{}".format(slotname) color textcolor align (0.5, 0.5) text_align 0.5 layout "subtitle"
                                        #                 null height 10
                                        #                 text "{}".format(FileTime(slot.file_name, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True)) xalign 0.5 size gui.slot_button_text_size color textcolor
                                        #                 null height 10
                                        #                 # Icon buttons
                                        #                 hbox:
                                        #                     xalign 0.5
                                        #                     # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                                        #                     if enable_renaming and slot.name and (enable_locking == False or (enable_locking and slot.locked_status != "LOCKED")):
                                        #                         button:
                                        #                             tooltip "Rename {}".format(slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{image=JSearUK's Save System/gui/rename.png}":
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action [SetVariable("targetaction", "changeslotname"),
                                        #                                     SetVariable("slotdetails", [slot.file_name, "{:05}".format(slotnumber), slot.version, slot.name, slot.locked_status]),
                                        #                                     Show("querystring", query="{color="+gui.interface_text_color+"}Please enter the slot name:{/color}", preload=slot.name, excludes="[{<>:\"/\|?*-", maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
                                        #                                     AwaitUserInput()]
                                        #                     if enable_locking and slot.locked_status:
                                        #                         button:
                                        #                             tooltip "{} {}".format("Unlock" if slot.locked_status == "LOCKED" else "Lock", slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{}".format("{image=gui/locked.png}" if slot.locked_status == "LOCKED" else "{image=JSearUK's Save System/gui/unlocked.png}"):
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action [SetVariable("slotdetails", [slot.file_name, "{:05}".format(slotnumber), slot.version, slot.name, "Unlocked" if slot.locked_status == "LOCKED" else "LOCKED"]),
                                        #                                     ReflectSlotChanges]
                                        #                     if enable_locking == False or (enable_locking and slot.locked_status != "LOCKED"):
                                        #                         button:
                                        #                             tooltip "Delete {}".format(slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{image=JSearUK's Save System/gui/delete.png}":
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action FileDelete(slot.file_name, slot=True)
    #
                                if title == "Save":
                                    # Only produce the button if we're on the Save screen
                                    # - NOTE: "auto"/"quick" 'playthrough's will not have been given any "+ New Save +" slots, so they *shouldn't* ever reach this code...
                                    textbutton "+ New Save +":
                                        xysize (1.0, config.thumbnail_height)
                                        background slotbackground
                                        hover_foreground Frame("JSearUK's Save System/gui/emptyframe.png")
                                        action Show("new_save_slot", playthrough=playthrough)
                                    # action [SetVariable("targetaction", "newslotnumber"), Function(AwaitUserInput)]
                                    # action [ If(slotnumber, true=SetVariable("userinput", slotnumber), false=Show("querynumber", query="{color="+gui.interface_text_color+"}Please select a slot number:{/color}", preload=str(lastmodified), minval=lastmodified, maxval=slot.version, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots")),
                                        # TODO: Test using 'side:' to structure this button more robustly
                                        # side "l c":
                                        #     # Thumbnail on the left. Setting it as a background to a frame permits regular content to appear overlaid, if needed
                                        #     frame:
                                        #         xsize config.thumbnail_width ysize config.thumbnail_height
                                        #         background FileScreenshot(filename, slot=True)
                                        #         # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                                        #         if enable_versioning and versionnumber != "" and versionnumber != config.version:
                                        #             add Solid("#000000CF")
                                        #             vbox:
                                        #                 at truecenter
                                        #                 text "- Older Save -" xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                        #                 null height gui.slot_button_text_size
                                        #                 text "v{}".format(versionnumber) xalign 0.5 size gui.slot_button_text_size style "fileslots_input"
                                        #     # Slot data and options
                                        #     viewport:
                                        #         xfill False yfill True xsize 0.98 edgescroll (100, 500) at truecenter
                                        #         side "b c":
                                        #             # Timestamp and Icon buttons
                                        #             vbox:
                                        #                 at truecenter
                                        #                 null height 10
                                        #                 text "{}".format(FileTime(filename, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True)):
                                        #                     xalign 0.5 size gui.slot_button_text_size color textcolor layout "nobreak"
                                        #                 null height 10
                                        #                 hbox:
                                        #                     xalign 0.5
                                        #                     # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                                        #                     if enable_renaming and editablename and (enable_locking == False or (enable_locking and lockedstatus != "LOCKED")):
                                        #                         button:
                                        #                             tooltip "Rename {}".format(slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{image=gui/rename.png}":
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action [SetVariable("targetaction", "changeslotname"),
                                        #                                     SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, lockedstatus]),
                                        #                                     Show("querystring", query="{color="+gui.interface_text_color+"}Please enter the slot name:{/color}", preload=editablename, excludes="[{<>:\"/\|?*-", maxcharlen=35, variable="userinput", bground=Frame("gui/frame.png"), styleprefix="fileslots"),
                                        #                                     AwaitUserInput()]
                                        #                     if enable_locking and lockedstatus:
                                        #                         button:
                                        #                             tooltip "{} {}".format("Unlock" if lockedstatus == "LOCKED" else "Lock", slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{}".format("{image=gui/locked.png}" if lockedstatus == "LOCKED" else "{image=gui/unlocked.png}"):
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action [SetVariable("slotdetails", [filename, "{:05}".format(slotnumber), versionnumber, editablename, "Unlocked" if lockedstatus == "LOCKED" else "LOCKED"]),
                                        #                                     ReflectSlotChanges]
                                        #                     if enable_locking == False or (enable_locking and lockedstatus != "LOCKED"):
                                        #                         button:
                                        #                             tooltip "Delete {}".format(slotname)
                                        #                             hover_background (None if enable_animation else Solid(gui.text_color))
                                        #                             text "{image=gui/delete.png}":
                                        #                                 align (0.5, 0.5)
                                        #                                 if enable_animation:
                                        #                                     at HoverSpin
                                        #                             action FileDelete(filename, slot=True)
                                        #             # The name of the slot. Since this could be lengthy and/or a large font, we need to make it fit gracefully
                                        #             viewport:
                                        #                 xfill False at truecenter
                                        #                 # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
                                        #                 edgescroll (100, 500)
                                        #                 #mousewheel "horizontal-change"
                                        #                 text "{}".format(slotname) color textcolor align (0.5, 0.5) layout "subtitle" text_align 0.5

                                    # Spacer between save slots. Can be commented out if desired
                                    # null height round(gui.scrollbar_size / 3)



# [ ADDITIONAL SCREENS ]
screen playthrough_input(playthrough=None):
    default playthrough_name = ""

    frame:
        align (0.5, 0.5)
        padding (50, 50)

        vbox:
            align (0.5, 0.5)

            text "Please give this Playthrough a unique name:":
                xalign 0.5
                size gui.label_text_size
                color gui.interface_text_color
            text "Forbidden characters: No Numbers or Symbols":
                xalign 0.5
                size gui.notify_text_size
                color gui.insensitive_color

            null height 20

            input:
                value ScreenVariableInputValue("playthrough_name")
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                length 35
                xalign 0.5

            null height 20

            hbox:
                xalign 0.5

                textbutton "Confirm":
                    size_group "ccbuttons"
                    if playthrough:
                        action [SetField(playthrough, "name", playthrough_name)]
                    else:
                        action [Function(Playthrough, playthrough_name)]

                null width 30

                textbutton "Cancel":
                    size_group "ccbuttons"
                    action Hide("playthrough_input")

                key "game_menu" action Hide("playthrough_input")

    # Show("querystring", query=", excludes="[invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame(), styleprefix="fileslots"),

screen new_save_slot(playthrough):
    frame:
        align (0.5, 0.5)
        padding (50, 50)

        vbox:
            align (0.5, 0.5)

            text "Please give this save a unique name:":
                xalign 0.5
                size gui.label_text_size
                color gui.interface_text_color
            text "Forbidden characters: No Numbers or Symbols":
                xalign 0.5
                size gui.notify_text_size
                color gui.insensitive_color

            null height 20

            input:
                value VariableInputValue("save_name")
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                length 35
                xalign 0.5

            null height 20

            hbox:
                xalign 0.5

                textbutton "Confirm":
                    size_group "ccbuttons"
                    action [Function(playthrough.create_save)]

                null width 30

                textbutton "Cancel":
                    size_group "ccbuttons"
                    action Hide("new_save_slot")

                key "game_menu" action Hide("new_save_slot")

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
            try: number = int(currentnumber)
            except ValueError: number = 0
            isvalid = True
            if minval: isvalid = False if minval > number else isvalid
            if maxval: isvalid = False if maxval < number else isvalid
        # Add Confirm/Cancel buttons to the bottom of the screen
        use ccframe(callingscreen="querynumber", variable=variable, newvalue=number, isvalid=isvalid)
