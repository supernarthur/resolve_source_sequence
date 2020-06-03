# Source sequence creator for DaVinci Resolve

This script leverages the resolve API to create one consolidated sequence with all the useful 
footage found in one or more other sequences.

The use cases may be :

- Copying all your grades to it (with ColorTrace) and making sure every shot has been color corrected
- Render all your shots to an intermediate codec with handles, without duplicates
- Prepare multiple edits for VFX
- Grade only in your source sequence, and copy all the grades to other sequences afterwards
- More ? I'm sure you can find a use case that makes sense in your workflow

## Installation

### Requirements

This script requires Python 3.6.

Using the GUI requires the Studio version of Resolve, version 16.2+. See below to use with the free version.

### Settings in Resolve

Make sure to enable External scripting by going in `Preferences`, `System`, `General`.
Then set the `External script using` option to `Local` or `Network`.

In the Fusion page, go to the `Fusion` menu, and open `Fusion Settings...`. 
Then navigate to the `Script` category, and select `Python 3.6`. 
Finally, save the settings, and quit Resolve for the settings to apply.

## Using the script

To execute the script, make sure your Resolve project is opened, and launch `source_sequence.py` with python3.6, either via a terminal window or double clicking the script (you may need to configure the default application for .py files).

A settings window will open.

In the top part, select the timelines you want the source sequence to be based on.
In the options category, you can set the handles length (in frames), which is used to merge two clips if their handles touch. You can also rename the source sequence to whatever name you like.

Once you click `Create`, the sequence will be created and opened.

## Known issues and workarounds

### Timewarps / Retime effects

This script is unable to correctly handle timewarps due to API limitations. 
If you have timewarps in your sequences, you can remove them by selecting the clips in your sequences, and then right-click, `Remove Attributes`, select `Retime effects` and `Ripple Sequence` before validating. 
Make sure to copy your sequences somewhere else beforehand to avoid losing those effects.

If you have a lot of sequences to work through, you can put them all in a new timeline, decompose them in place, and remove the retime effects on this sequence only. 
You can then use this timeline only in the source sequence settings.

### Using the script in the free version of resolve

This is intended for more advanced users.

Note the path of the folder in which the `source_sequence.py` script is located.
Open the console in resolve, select `Py3` in the top bar and type the following, replacing `/path/to/resolve_source_sequence` with the path you found :

```python
import fusionscript
import sys

sys.path.append("/path/to/resolve_source_sequence")

import source_sequence

resolve = fusionscript.scriptapp("Resolve")
```

Then, to use the script, type the following, replacing the parameters with the ones you want :

```python
source_sequence.main(resolve,
                     source_seq_name="source_sequence",
                     seq_list=["Timeline 1", "Timeline 2", "Timeline 3"],
                     handle_length=25)
```


