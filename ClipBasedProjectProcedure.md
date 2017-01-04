### Clip based project procedure

A clip based project has a few major phases:

1. Define the specification for the CD.
2. Record the clips.
3. Compile the clips into tracks and discs.

## Define the _performance specification_

Use a Google Sheet to define the discs and tracks.
Relevant information includes:
  * **disc**:
  <br />
  A label used to identify the disc.  Usually, this will be the name of the CD.
  * **track**:
  <br />
  A label used to identify the track.  Usually, this will be the track number.
  * **sequence number**:
  <br />
  A number used to keep clips in order.
  * **label**:
  <br />
  A label used to identify the clip.
  <br />
  For single words, it will likely be the word itself.
  <br />
  For paragraphs or sentences, it should be a succinct phrase, such as
  "Introduction Generic".
  * **text** _(optional)_:
  <br />
  The text itself, if it differs from the _label_.
  * **performer** _(optional)_:
  <br />
  An identifier for the performer of the clip.
  <br />Usually, this will be empty or a person's name.

For example:

| disc | track  | sequence | label         | text               | performer |
| ---- | ------ | -------- | ------------- | ------------------ | --------- |
| 1    | 1      | 1        | Instruction2B | Welcome to our CD! | Joe       |
| 1    | 1      | 2        | Word1         |                    | Joe       |

## Record the clips

1. Export the _specification_ sheet into _performance sequences_ for each
performer.

https://docs.google.com/spreadsheets/d/1FlhfMCX0HRUWVk8Or2GJZTPwxc_uaci3KM-0VbspnIY/edit#gid=0

2. If the _performance sequence_ is simple enough to manually trim each clip,
simply record the clips without a lyrics track.
3. If you want to automated the trimming process:
    1. Import the _performance sequence_ into a lyrics track in a REAPER
    session.
    2. Set a reasonable tempo.
    3. Record the clips in order.

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

`[label]-[performer]-[creation_datetime].[file extension]`

`$region-$track-$year$month$dayT$hour$minute$second`

For example:

`Instruction5B-Tom-20170103T070418Z-01.wav`

## Export available clips and lengths

1. Generate a CSV file with all the clips lengths.
<br />`python wave_file.py generate_csv_of_waves [folder] [csv file name]`
1. Import the CSV into the Google Sheet.
1. Lookup the lengths with the following formula:
<br />`=VLOOKUP(CONCATENATE([label], ".wav"),index!A:C,3)`

## Define silences

Once all the clips have been recorded, the lengths of each clip will be known.
At this point, you can define silences, since the final disc length can be
calculated.

## Compile the clips

1. Import the fully specified project into REAPER.
