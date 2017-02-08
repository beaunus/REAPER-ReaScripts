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
  """Returns the track object with the specified id.

  If the track_objects array doesn't already contain the specified track,
  add a new track with the given track_id and add it to the track_objects array.
  Otherwise, simply return the track object.

  Args:
    track_id: The identifier for the track.
    track_objects: The array of track objects in the session.

  Returns:
    The REAPER track object that represents the track with
    the specified identifier.
  """
  if track_id not in track_objects:
    # Create a new track.
    track_index = RPR_GetNumTracks()
    RPR_InsertTrackAtIndex(track_index, False)
    new_track = RPR_GetTrack(0, track_index)

    # Add the new track to the track_objects array.
    track_objects[track_id] = new_track

    # Name the track according to the track_id.
    RPR_GetSetMediaTrackInfo_String(new_track, "P_NAME", track_id, True)

    # Update the UI
    RPR_TrackList_AdjustWindows(True)
    RPR_UpdateTimeline()
  return (track_objects[track_id], track_objects)

def get_performer(component_string):
  """Returns the performer of the specified component.

  Args:
    component_string: The JSON representation of the component.  For example:
      "Apple [Beau]"
  Returns:
    The performer of the component.  For example: "Beau"
  """
  index_of_open = component_string.find("[")
  index_of_close = component_string.find("]", index_of_open)
  performer = component_string[index_of_open + 1:index_of_close]
  return performer

def add_pause(component, cur_position, track_objects, pause_lengths):
  """Add the pause specified in the given component to the session.

  Args:
    component: The JSON representation of the component.
    cur_position: The starting position of the component.
    track_objects: The array of REAPER track objects in which to add components.
    pause_lengths: The dictionary of pause lengths for this specification.

  Returns:
    A tuple containing the following:
      cur_position: The new cursor position, after adding the component.
      track_objects: The array of RPR_MediaTracks,
        since it may have been modified.
      new_item: The new RPR_MediaItem that represents the newly added component.
  """
  # Get the RPR_MediaTrack for pauses.
  (pause_track, track_objects) = get_track("_PAUSE", track_objects)

  # Add a new item to the pause_track.
  new_item = RPR_AddMediaItemToTrack(pause_track)

  # Determine the length of the pause.
  if (pause_lengths is not None and component in pause_lengths):
    RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", pause_lengths[component])
  else:
    RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)

  # Put the newly created pause in place,
  # add it to a new take on the pause track,
  # and name it according to the component specification.
  RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)
  RPR_AddTakeToMediaItem(new_item)
  this_take = RPR_GetActiveTake(new_item)
  RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", component, True)

  # Increment the cursor_position and return
  cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")
  return (cur_position, track_objects, new_item)

def add_repeat(component, cur_position, track_objects, prev_item):
  """Adds a repeat specified by the given component to the session.

  Args:
    component: The JSON representation of the component.
    cur_position: The starting position of the component.
    track_objects: The array of REAPER track objects in which to add components.
    prev_item: The previous RPR_MediaItem.

  Returns:
    A tuple containing:
      cur_position: The new cursor position, after adding the component.
      track_objects: The array of RPR_MediaTracks,
        since it may have been modified.
      new_item: The new RPR_MediaItem that represents the newly added component.
  """
  # Get the RPR_MediaTrack for repeats.
  (repeat_track, track_objects) = get_track("_REPEAT", track_objects)

  # Add a new item to the repeat_track.
  new_item = RPR_AddMediaItemToTrack(repeat_track)

  # Determine the previous item's length and name.
  prev_item_length = RPR_GetMediaItemInfo_Value(prev_item, "D_LENGTH")
  prev_item_name = \
  RPR_GetSetMediaItemTakeInfo_String(RPR_GetActiveTake(prev_item), \
                                     "P_NAME", None, False)[3]
  # Set the repeat item's attributes and add a new take.
  RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", prev_item_length)
  RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)
  RPR_SetMediaItemInfo_Value(new_item, "B_MUTE", True)
  RPR_AddTakeToMediaItem(new_item)

  # Increment the cur_position.
  cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")

  # Get the newly created take and name it accordingly.
  this_take = RPR_GetActiveTake(new_item)
  RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", prev_item_name, True)

  return (cur_position, track_objects, new_item)

def add_clip(component, cur_position, track_objects, prev_item):
  # Determine the performer of the clip.
  performer = get_performer(component)

  # Get the track that the clip should be inserted into.
  (track, track_objects) = get_track(performer, track_objects)
  new_item = RPR_AddMediaItemToTrack(track)

  # Set the length and position of the new RPR_MediaItem
  RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)
  RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)

  # Add a RPR_Take to the new media item.
  RPR_AddTakeToMediaItem(new_item)

  # Increment the cur_position.
  cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")

  # Name the take according to the component.
  this_take = RPR_GetActiveTake(new_item)
  RPR_GetSetMediaItemTakeInfo_String(this_take, "P_NAME", component, True)

  return (cur_position, track_objects, new_item)

def add_component(component, cur_position, track_objects, pause_lengths, \
                  prev_item):
  """Adds the specified component to the session.

  Args:
    component: The JSON representation of the component.
    cur_position: The starting position of the component.
    track_objects: The array of REAPER track objects in which to add components.
    pause_lengths: The dictionary of pause lengths for this specification.
    prev_item: The previous RPR_MediaItem.
      This is used for "REPEAT_PREVIOUS_WORD" components.

  Returns:
    A tuple containing:
      cur_position: The new cursor position, after adding the component.
      track_objects: The array of RPR_MediaTracks,
        since it may have been modified.
      new_item: The new RPR_MediaItem that represents the newly added component.
  """
  # If this component is a _PAUSE, add an empty item to represent it.
  if component.startswith("_PAUSE"):
    (cur_position, track_objects, new_item) = \
    add_pause(component, cur_position, track_objects, pause_lengths)
  # If this component is a _REPEAT, add a muted copy of the previous item
  # to represent it.
  elif component == "_REPEAT_PREVIOUS_WORD":
    (cur_position, track_objects, new_item) = \
    add_repeat(component, cur_position, track_objects, prev_item)
  # Otherwise, add the performed clip to the session.
  else:
    (cur_position, track_objects, new_item) = \
    add_clip(component, cur_position, track_objects, prev_item)
  return (cur_position, track_objects, new_item)

if __name__ == "__main__":

  # Prompt the user for the JSON file that describes the disc layout
  (retval, filenameNeed4096, title, defext) = \
  RPR_GetUserFileNameForRead(None, None, ".json")

  if(filenameNeed4096 != 'None'):

    # Open the file and load it into an dictionary object.

    f = open(filenameNeed4096, 'r')
    folder = os.path.dirname(filenameNeed4096)

    # Parse the JSON file into an object
    specification = json.loads(f.read())

    cur_position = RPR_GetCursorPosition()

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
            (cur_position, track_objects, prev_item) = \
            add_component(component, cur_position, track_objects, \
                          pause_lengths, prev_item)
