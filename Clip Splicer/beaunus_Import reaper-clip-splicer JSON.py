"""
ReaScript Name: Name item takes by last marker to cut item
Author: beaunus
Licence: GPL v3
REAPER: 5.0
Version: 1.0

Changelog:
v1.0 (2017-01-01)
  + Initial Release
"""

import json
import os


def get_track(track_id, track_objects):
  if track_id not in track_objects:
    track_index = RPR_GetNumTracks()
    RPR_InsertTrackAtIndex(track_index, False)
    new_track = RPR_GetTrack(0, track_index)
    RPR_GetSetMediaTrackInfo_String(new_track, "P_NAME", track_id, True)
    track_objects[track_id] = new_track
    RPR_TrackList_AdjustWindows(True)
    RPR_UpdateTimeline()
  return (track_objects[track_id], track_objects)

def get_performer(component):
  index_of_open = component.find("[")
  index_of_close = component.find("]", index_of_open)
  performer = component[index_of_open + 1:index_of_close]
  return performer

def add_component(component, current_position, track_objects, pause_lengths, prev_item):
  # If this component is a _PAUSE,
  # add an empty item to represent it.
  if component.startswith("_PAUSE"):
    (pause_track, track_objects) = get_track("_PAUSE", track_objects)
    new_item = RPR_AddMediaItemToTrack(pause_track)
    if (pause_lengths is not None and component in pause_lengths):
      RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", pause_lengths[component])
    else:
      RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)
    RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", current_position)
    RPR_AddTakeToMediaItem(new_item)
    current_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")
    this_take = RPR_GetActiveTake(new_item)
    RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", component, True)
  elif component == "_REPEAT_PREVIOUS_WORD":
    (repeat_track, track_objects) = get_track("_REPEAT", track_objects)
    new_item = RPR_AddMediaItemToTrack(repeat_track)
    prev_item_length = RPR_GetMediaItemInfo_Value(prev_item, "D_LENGTH")
    prev_item_name = RPR_GetSetMediaItemTakeInfo_String(RPR_GetActiveTake(prev_item), "P_NAME", None, False)[3]
    RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", prev_item_length)
    RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", current_position)
    RPR_SetMediaItemInfo_Value(new_item, "B_MUTE", True)
    RPR_AddTakeToMediaItem(new_item)
    current_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")
    this_take = RPR_GetActiveTake(new_item)
    RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", prev_item_name, True)
  else:
    performer = get_performer(component)
    (track, track_objects) = get_track(performer, track_objects)
    new_item = RPR_AddMediaItemToTrack(track)
    RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)
    RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", current_position)
    RPR_AddTakeToMediaItem(new_item)
    current_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")
    this_take = RPR_GetActiveTake(new_item)
    RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", component, True)
  return (current_position, track_objects, new_item)



(retval, filenameNeed4096, title, defext) = RPR_GetUserFileNameForRead(None, None, ".json")

if(filenameNeed4096 != 'None'):
  f = open(filenameNeed4096, 'r')
  folder = os.path.dirname(filenameNeed4096)

  # Parse the JSON file into an object
  specification = json.loads(f.read())

  current_position = RPR_GetCursorPosition()

  # Create an index of tracks to be used throughout the process
  track_objects = dict()

  # Create a FAKE index of pause lengths
  pause_lengths = {
    "_PAUSE_AFTER_COMPONENT": 2,
    "_PAUSE_AFTER_PAGE_NUMBER": 3,
    "_PAUSE_AFTER_WORD":4
    }

  # Iterate over each disc
  for disc_name, disc_val in specification.iteritems():
    # Iterate over each track
    for track in disc_val:
      prev_item = None
      # Iterate over each component
      if track is not None:
        for component in track:
          (current_position, track_objects, prev_item) = add_component(component, current_position, track_objects, pause_lengths, prev_item)
