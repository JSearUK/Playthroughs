define config.developer = True

# [ INITIALISATION - BEST TO LEAVE ALONE ]
default persistent.save_system = "original"
default persistent.sortby = "last_modified"
default persistent.playthroughs = []
default persistent.current_playthrough = None


# [ CONFIG VARIABLES ]
define enable_versioning = True # Warns players if save is out of date
define enable_renaming = True # Allow players to edit their playthrough and save names
define enable_locking = True # Allows players to lock and unlock saves. Locked saves cannot be renamed, overwritten or deleted.
define enable_sorting = True # Allows the player to sort their playthrough saves by a specific key, "last_modified" and "slot_num" are added. More may follow in future.
define enable_animation = False # Determines the hover behaviour of the UI. Current status: Unstable
define slotforeground = Frame(Transform("JSearUK's Save System/gui/emptyframe.png", matrixcolor=ColorizeMatrix(Color("#000"), Color(gui.text_color))))
define slotbackground = None #Solid("FFF1")
    # This is what is shown behind each slot, and can be any Displayable or None. Either hard-code it, or use a binding defined at a lower init level
    # - NOTE: Displayables are usually defined within a Frame in order to be scaled correctly, e.g. Frame("gui/nvl.png"). There are exceptions, such as Color() or Solid()
    # - NOTE: None is the default, removing the background, resulting in total transparency

# [ CLASSES ]
python early:
    class Playthrough:
        """The Playthrough class (summary line)

        The playthrough class stores the name of the play through and a list of saves for that playthrough (detailed line)

        Attributes:
            attribute1_EXAMPLE (data type): Description of attribute1
            name (str): The name of the playthrough
            lock_count (int): The count of the number of saves locked
            higher_version_count (int): The count of the number of slots with a higher version than config.version

        """

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

                save_info = SaveInfo(save, renpy.slot_mtime(save), save_split[1], slot_json["_version"], slot_json["_save_name"], slot_json.get("locked_status", "UNLOCKED"))
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

            persistent.playthroughs.append(persistent.playthroughs.pop(persistent.playthroughs.index(self))) # Move playthrough to end of "playthroughs"

        def json_additional_info(self, file):
            file["playthrough_name"] = self.name
            file["status"] = "UNLOCKED"

        def delete(self):
            """Deletes all saves in playthrough, removes playthrough from parent list, and then deletes its reference"""
            for slot in self.slots:
                renpy.unlink_save(slot.file_name)
            persistent.playthroughs.remove(self)
            del self

    class SaveInfo:
        """A class for storing info and methods of a save.

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

        def rename(self, new_name):
            self.name = new_name

            slot_json = renpy.slot_json(self.file_name)
            slot_json["_save_name"] = new_name

        def toggle_lock(self):
            if self.locked_status == "LOCKED":
                self.locked_status = "UNLOCKED"

            elif self.locked_status == "UNLOCKED":
                self.locked_status = "LOCKED"

    def add_save_json_data(file):
        file["locked_status"] = "UNLOCKED"

# [ FUNCTIONS ]
init -1 python:
    def generate_playthroughs_from_saves():
        saves = renpy.list_saved_games(fast=True)
        for save in saves:
            playthrough_name = save.split('-')[0]

            if playthrough_name == "_reload": continue
            if playthrough_name in {playthrough.name for playthrough in persistent.playthroughs}: continue

            playthrough = Playthrough(name=playthrough_name)

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

init 1 python:
    generate_playthroughs_from_saves()
    config.save_json_callbacks.append(add_save_json_data)

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
            imagebutton:
                action SetVariable("persistent.save_system", "playthrough")
                idle "JSearUK's Save System/gui/playthroughview.png"
                tooltip "Switch to the Playthrough system"
                hover_background (None if enable_animation else Solid(gui.text_color))
                if enable_animation:
                    at HoverSpin

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
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

            ## Buttons to access other pages.
            hbox:
                style_prefix "page"

                align (0.5, 1.0)

                spacing gui.page_spacing

                textbutton _("<") action FilePagePrevious() tooltip "View previous page"

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto") tooltip "View Autosaves"
                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick") tooltip "View Quicksaves"

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
    $ yvalue = 32 if gui.text_size < 22 else int(gui.text_size * 1.5)

    use game_menu(title):
        # Collect and display any active tooltip on this page
        $ help = GetTooltip()
        if help:
            text help:
                style "fileslots_input"
                italic True
                size gui.interface_text_size
                pos (50, -50)

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
                            # Display buttons for the contents of 'persistent.playthroughs' in reverse order. Filtering out "auto" and "quick"
                            for playthrough in reversed(filter(lambda playthrough: playthrough.name not in ("auto", "quick"), persistent.playthroughs)):

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
                                        text_selected_color gui.hover_color
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
                                spacing 5
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
                                                if slot.locked_status == "UNLOCKED":
                                                    action Show("save_input", playthrough=persistent.current_playthrough)

                                            elif title == "Load":
                                                tooltip "Load [slot.name]"
                                                action FileLoad(slot.file_name, slot=True)
                                            xysize(1.0, config.thumbnail_height)
                                            background slotbackground
                                            hover_foreground slotforeground

                                            if slot.locked_status == "UNLOCKED":
                                                key "save_delete" action FileDelete(slot.file_name, slot=True)

                                            hbox:
                                                # Thumbnail
                                                fixed:
                                                    xysize (config.thumbnail_width, config.thumbnail_height)

                                                    add FileScreenshot(slot.file_name, slot=True)
                                                    # Grey out the thumbnail if versioning is enabled, the version number is known, and it doesn't match the current version
                                                    if enable_versioning and slot.version != config.version:
                                                        add "#000000CF"
                                                        vbox:
                                                            align (0.5, 0.5)

                                                            text "- Older Save -":
                                                                xalign 0.5
                                                                size gui.slot_button_text_size
                                                                style "fileslots_input"

                                                            text "v[slot.version]":
                                                                xalign 0.5
                                                                size gui.slot_button_text_size
                                                                style "fileslots_input"

                                                viewport:
                                                    scrollbars "vertical"
                                                    mousewheel "change"
                                                    align (0.5, 0.5)

                                                    vbox:
                                                        align (0.5, 0.5)
                                                        spacing 10
                                                        xfill True

                                                        # Save name
                                                        viewport:
                                                            # Putting the slotname in its own box helps us to handle 'editablename's that exceed the space they're given without breaking the layout
                                                            # TODO: Why the **** do we occasionally wind up with a weird scrollbar?!? o7
                                                            # - [EDIT:] To reproduce this: screen size of 1920x1080, text size 33 and an 'editablename' of "James and the Giant Peach by R Dahl"
                                                            #           - or a text size of 66 and a Playthrough name of "Test", then hit the '+ New Save +' button
                                                            # - [EDIT:] Adding the HoverSpin transform to the icons has also made all of the buttons gain the weird scrollbar...
                                                            #    - [EDIT:] Restructuring the button using 'side:' may help. That 'ymaximum' probably doesn't help, either
                                                            #       - [EDIT:] There is an attempt at this commented out, below...
                                                            edgescroll (100, 500) #mousewheel "horizontal-change"
                                                            xfill False
                                                            align (0.5, 0.5)

                                                            text slot.name:
                                                                align (0.5, 0.5)
                                                                layout "subtitle"

                                                        # Last modified time
                                                        text FileTime(slot.file_name, format=_("{#file_time}%A, %B %d %Y, %H:%M"), slot=True):
                                                            xalign 0.5
                                                            size gui.slot_button_text_size

                                                        # Icon buttons
                                                        hbox:
                                                            xalign 0.5
                                                            spacing 10

                                                            # NOTE: "auto/quick" have empty 'editablename' and 'lockedstatus' fields, so only ever get the Delete button
                                                            if enable_renaming and slot.locked_status == "UNLOCKED":
                                                                imagebutton:
                                                                    idle "JSearUK's Save System/gui/rename.png"
                                                                    tooltip "Rename [slot.name]"
                                                                    hover_background (None if enable_animation else Solid(gui.text_color))
                                                                    if enable_animation:
                                                                        at HoverSpin
                                                                    action Show("save_input", slot=slot)

                                                            if enable_locking and slot.locked_status == "LOCKED":
                                                                imagebutton:
                                                                    idle "JSearUK's Save System/gui/unlocked.png"
                                                                    tooltip "Unlock [slot.name]"
                                                                    hover_background (None if enable_animation else Solid(gui.text_color))
                                                                    if enable_animation:
                                                                        at HoverSpin
                                                                    action Function(slot.toggle_lock)

                                                            elif enable_locking and slot.locked_status == "UNLOCKED":
                                                                imagebutton:
                                                                    idle "JSearUK's Save System/gui/locked.png"
                                                                    tooltip "Lock [slot.name]"
                                                                    hover_background (None if enable_animation else Solid(gui.text_color))
                                                                    if enable_animation:
                                                                        at HoverSpin
                                                                    action Function(slot.toggle_lock)

                                                            if enable_locking == False or (enable_locking and slot.locked_status != "LOCKED"):
                                                                imagebutton:
                                                                    tooltip "Delete [slot.name]"
                                                                    idle "JSearUK's Save System/gui/delete.png"
                                                                    hover_background (None if enable_animation else Solid(gui.text_color))
                                                                    if enable_animation:
                                                                        at HoverSpin
                                                                    action FileDelete(slot.file_name, slot=True)

                                if title == "Save":
                                    # Only produce the button if we're on the Save screen
                                    # - NOTE: "auto"/"quick" 'playthrough's will not have been given any "+ New Save +" slots, so they *shouldn't* ever reach this code...
                                    textbutton "+ New Save +":
                                        xysize (1.0, config.thumbnail_height)
                                        background slotbackground
                                        hover_foreground slotforeground
                                        action Show("save_input", playthrough=persistent.current_playthrough)
                                        text_align (0.5, 0.5)

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
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz"
                length 35
                xalign 0.5

            null height 20

            hbox:
                xalign 0.5

                textbutton "Confirm":
                    sensitive playthrough_name not in {playthrough.name for playthrough in persistent.playthroughs}
                    if playthrough:
                        action SetField(playthrough, "name", playthrough_name)
                    else:
                        action [Function(Playthrough, playthrough_name), ShowMenu("save")]

                null width 30

                textbutton "Cancel":
                    action Hide("playthrough_input")

    key "game_menu" action Hide("playthrough_input")

    # Show("querystring", query=", excludes="[invalid=persistent.playthroughslist + ["auto", "quick"], maxcharlen=35, variable="userinput", bground=Frame(), styleprefix="fileslots"),

screen save_input(playthrough=None, slot=None):
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
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz"
                length 35
                xalign 0.5

            null height 20

            hbox:
                xalign 0.5

                textbutton "Confirm":
                    size_group "ccbuttons"
                    if playthrough:
                        action [Function(playthrough.create_save), Hide("save_input")]
                    elif slot:
                        action [Function(slot.rename, save_name), Hide("save_input")]

                null width 30

                textbutton "Cancel":
                    size_group "ccbuttons"
                    action Hide("save_input")

    key "game_menu" action Hide("save_input")
