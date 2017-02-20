# beaunus REAPER Clip Splicer

## Define the _performance specification_

Use a Google Sheet to define the discs and tracks.

https://docs.google.com/spreadsheets/d/1FlhfMCX0HRUWVk8Or2GJZTPwxc_uaci3KM-0VbspnIY/edit#gid=0

### Using the _performance specification_

### Understanding the JSON representation

The specification is represented by a dictionary.

    {
      // Disc 01
      "Disc_01 Title": [
        null, // CD Track 00 is irrelevant.
        // Track 01
        [
          "Track_01 Component_01",
          ...,
          "Track_01 Component_N"
        ],
        ...,
        // Track N
        [
          "Track_N Component_01",
          ...,
          "Track_N Component_N"
        ]
      ],
      ...,
      // Disc N
      "Disc_N Title": [
        null, // CD Track 00 is irrelevant.
        // Track 01
        [
          "Track_01 Component_01",
          ...,
          "Track_01 Component_N"
        ],
        ...,
        // Track N
        [
          "Track_N Component_01",
          ...,
          "Track_N Component_N"
        ]
      ],
    }

### Adding templates

The real power of the spreadsheet is creating _templates_.  A _template_ uses a
custom Google Apps Script to create an array of components, given a simple set
of template arguments.

Here's an example of a template from the spreadsheet.

<table>
    <tr>
        <th>Disc</th>
        <th>Track</th>
        <th>Component</th>
        <th>Performer</th>
        <th>Template</th>
        <th>Template Parameters</th>
        <th>Template Arguments</th>
    </tr>
    <tr>
        <td>My Amazing Disc</td>
        <td>1</td>
        <td></td>
        <td></td>
        <td>Repeat Words</td>
        <td>
            performer (string)<br/>
            word (string)<br/>
            num_repetitions (int)
        </td>
        <td>
            John Lennon<br/>
            Love<br/>
            3
        </td>
    </tr>
</table>

In order to interpret the above data, you will need to adjust the spreadsheet's
`templates.gs` script in the following ways:

1. In the function `template()`, add a case for the template `"Repeat Words"`.
1. Add a function `templateRepeatWords()`.

The function should return an array of components.  For example:

    [
      "Love [John Lennon]",
      "_PAUSE_AFTER_PAGE_NUMBER",
      "Love [John Lennon]",
      "_PAUSE_AFTER_PAGE_NUMBER",
      "Love [John Lennon]",
      "_PAUSE_AFTER_PAGE_NUMBER"
    ]

## Import the specification into a REAPER session.

1. Run the script `Script: beaunus_import_reaper_clip_splicer_json.py`
1. Select a .json file that contains a Clip Splicer specification.
1. Examine the generated report to see what needs to be recorded.
    - The report can be found in the same folder as the .json file.

## Record the clips

1. If the _performance sequence_ is simple enough to manually trim each clip,
simply record the clips without a lyrics track.
1. If you want to automated the trimming process:
    1. Import the _performance sequence_ into a lyrics track in a REAPER
    session.
    1. Set a reasonable tempo.
    1. Record the clips in order.

## Trim and save the clips

Performances should be __loudness normalized__ to -23LUFS.

If you have used a lyrics track:

1. Convert the lyrics to markers.
1. Split the performance using dynamic split.
1. Trim silence at the beginnings and ends of clips.
1. beaunus_Name item takes by last marker to cut item.lua
1. SWS: Create regions from selected items (name by active take)
1. Render regions.

Finished clips should be named according to the following convention:

`[label] [[performer]].[file extension]`

`$region [$track]`

For example:

`Love [John Lennon].wav`

Clips should be put in the folder `"clips"` relative to the .json file.

After all the clips have been recorded, you can again 'Import the specification
into a REAPER session.'