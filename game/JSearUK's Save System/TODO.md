# [ DEVLOG ]
- Since I do not know how to edit the content/JSON of a file once it has saved, or easily regain control after a load, I'm going to store data in the filename and edit it using renaming
- Format: filename = "PlaythroughName-SlotNumber-VersionNumber-EditableName-LockStatus"(-LT1.save)
- **WARNING**: Any functionality relating to Quick- or Auto-saves assumes the English version of these names. I do not know how to handle translation, or even if translation is needed
- [EDIT:] Original Ren'Py code appears to translate the button labels, but uses hardcoded page names "auto" and "quick". So I think we're safe on this front

# [ TODO ]
- [x] TODO: Figure out why "James and the Giant Peach by R Dahl" produces an unnecessary scrollbar of non-standard size. Must be a side effect of layout and sizing?
- [EDIT:] This may not occur once Ren'Py has been upgraded to 7.4.8
- [EDIT:] HoverSpin icons inside the save slot button data viewport generate this behaviour. Possible solution: 'side:' - if not, write a demo and send it to Tom
- [x]  Re-write the mess I made of the Ren'py original save page page selection bar.       - [EDIT:] Further details in the relevant section
- [x]  Incorporate a way for future Devs to access and display any information saved with the file as JSON. Investigate the saving of JSON data to saves in the first place
- [EDIT:] 'enable_JSON', icon/timestamp button, open screen to see data, close and resume
- [x]  The Ren'Py save system should still be updated to implement naming/locking, if at all possible
- [EDIT:] Could do this by keeping a list of locked slots, and adding (an) overlay(s) to the slotbuttons that change 'save_name' before overwriting
- [x]  Investigate the translation system and rework text handling to accomodate this as much as possible
- [x] Attempt to compact as much of the properties as possible into styles
- [x]  Final pass: expand the code for clarity and see whether any more experienced coders are interested in wrestling it into a state of best practice
**WARNING**: Simply dropping the graphics files, plus this file and its .rpyc, into another project throws an exception. Building it in works fine.
- [EDIT:] This seems to be okay for games higher than 7.3.5
- [EDIT:] Games that use a published template to skin the entire UI (e.g. Pandora's Box) ignore these files, even if I add 'init offset = 99999' just before the screen
- [x]  Investigate further


# [ TESTING ]
- [x] Basic functionality: File save, File overwrite, File rename, File load, File delete, File lock/unlock, Playthrough create, Playthrough rename, Playthrough delete
- [x] Additional functionality: Dev toggles respected, Auto/Quick handled correctly, Playthrough list/Slots list updated correctly on any change (including changing/leaving Menu screens)
- [x] Layout: Handle lengthy/large text sensibly, maintain integrity even if window size changes, avoid absolute values wherever possible
- [x] Environment: Compensate for any unavoidable bugs; report said bugs to PyTom with as much detail as possible, and ideally a short script reproducing the bug


# [ BUGREPORTS ]
- [x] The viewport showing save details in each slot button sometimes shows an unscrollable scrollbar, despite there being lots of room
- [x] [EDIT:] Putting HoverSpin icons into the viewport guarantees this behavior. Certain results of 'layout "subtitle"' can also provoke this behaviour
- [x] [EDIT:] Moving the icons up a row, so that the timestamp is displayed below them, makes no difference

