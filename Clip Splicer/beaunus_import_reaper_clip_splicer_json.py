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

import datetime
import json
import os
import string
import time

"""
TODO:
pylint
doc strings
add markers and regions
consolidate redundant code
"""

# pylint: disable=undefined-variable


def get_performer(component_string):
    """Returns the performer of the specified component.

    Args:
        component_string: The JSON representation of the component.
                          For example: "Apple [Beau]"
    Returns:
        The performer of the component. For example: "Beau"
    """
    index_of_open = component_string.find("[")
    index_of_close = component_string.find("]", index_of_open)
    performer = component_string[index_of_open + 1:index_of_close]
    return performer


def component_key(component_string):
    return get_performer(component_string) + component_string


class reaper_clip_splicer:
    """A class to represent a REAPER clip splicer project.

    Attributes:
        media_tracks: REAPER MediaTracks to be used for components.
                      Indexed by performer name.
        pause_lengths: Times to pause between certain component types.
                       Indexed by pause_length name.
        discs: Disc specifications.  Indexed by disc name.
        available_files: Files that correspond to specified components.
        unavailable_files: Files that are unavailable for the project.
    """

    def __init__(self, specification, folder):
        """Initializes a new reaper_clip_splicer project.
        """
        self.media_tracks = dict()
        self.pause_lengths = dict()
        self.discs = specification
        self.available_files = set()
        self.unavailable_files = set()
        self.folder = folder

        self.initialize_pause_lengths()

    def initialize_pause_lengths(self):
        # Determine pauses that need to be specified
        # Iterate over each disc
        # pylint: disable=unused-variable
        for disc_name, disc_val in self.discs.iteritems():
            # Iterate over each track
            for track in disc_val:
                # Iterate over each component
                if track is not None:
                    for component in track:
                        if component.startswith("_PAUSE"):
                            if component not in self.pause_lengths:
                                self.pause_lengths[component] = None

        # Prompt user for pause lengths
        user_lengths = RPR_GetUserInputs("Specify Pauses",
                                         len(self.pause_lengths),
                                         ','.join(
                                             self.pause_lengths.iterkeys()),
                                         "1,1,1,1,1,1,1", 99)[4].split(",")
        i = 0
        for pause_name in self.pause_lengths.iterkeys():
            self.pause_lengths[pause_name] = int(user_lengths[i])
            i += 1

    def get_track(self, track_id):
        """Returns the track object with the specified id.

        If the track_objects array doesn't already contain the specified track,
        add a new track with the given track_id and add it to the track_objects array.
        Otherwise, simply return the track object.

        Args:
            track_id: The identifier for the track.

        Returns:
            The REAPER MediaTrack object that represents the track with
            the specified identifier.
        """
        if track_id not in self.media_tracks:
            # Create a new track.
            track_index = RPR_GetNumTracks()
            RPR_InsertTrackAtIndex(track_index, False)
            new_track = RPR_GetTrack(0, track_index)

            # Add the new track to the track_objects array.
            self.media_tracks[track_id] = new_track

            # Name the track according to the track_id.
            RPR_GetSetMediaTrackInfo_String(
                new_track, "P_NAME", track_id, True)

            # Update the UI
            RPR_TrackList_AdjustWindows(True)
            RPR_UpdateTimeline()
        return self.media_tracks[track_id]

    def add_pause(self, component, cur_position):
        """Add the pause specified in the given component to the session.

        Args:
            component: The JSON representation of the component.
            cur_position: The starting position of the component.

        Returns:
            A tuple containing the following:
                cur_position: The new cursor position, after adding the component.
                new_item: The new REAPER MediaItem that represents the newly added component.
        """
        # Get the REAPER MediaTrack for pauses.
        pause_track = self.get_track("_PAUSE")

        # Add a new item to the pause_track.
        new_item = RPR_AddMediaItemToTrack(pause_track)

        # Determine the length of the pause.
        if self.pause_lengths is not None and component in self.pause_lengths:
            RPR_SetMediaItemInfo_Value(
                new_item, "D_LENGTH", self.pause_lengths[component])
        else:
            RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)

        # Put the newly created pause in place,
        # add it to a new take on the pause track,
        # and name it according to the component specification.
        RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)
        RPR_AddTakeToMediaItem(new_item)
        this_take = RPR_GetActiveTake(new_item)
        RPR_GetSetMediaItemTakeInfo_String(
            this_take, "P_NAME", component, True)

        # Increment the cursor_position and return
        cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")
        return (cur_position, new_item)

    def add_repeat(self, cur_position, prev_item):
        """Adds a repeat specified by the given component to the session.

        Args:
            cur_position: The starting position of the component.
            prev_item: The previous REAPER MediaItem.

        Returns:
            A tuple containing:
                cur_position: The new cursor position, after adding the component.
                new_item: The new RPR_MediaItem that represents the newly added component.
        """
        # Get the RPR_MediaTrack for repeats.
        repeat_track = self.get_track("_REPEAT")

        # Add a new item to the repeat_track.
        new_item = RPR_AddMediaItemToTrack(repeat_track)

        # Determine the previous item's length and name.
        prev_item_length = RPR_GetMediaItemInfo_Value(prev_item, "D_LENGTH")
        prev_item_name = \
            RPR_GetSetMediaItemTakeInfo_String(RPR_GetActiveTake(prev_item),
                                               "P_NAME", None, False)[3]
        # Set the repeat item's attributes and add a new take.
        RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", prev_item_length)
        RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)
        RPR_SetMediaItemInfo_Value(new_item, "B_MUTE", True)
        RPR_AddTakeToMediaItem(new_item)

        # Add the previous item's source to this one.
        this_take = RPR_GetActiveTake(new_item)
        prev_take = RPR_GetActiveTake(prev_item)
        prev_source = RPR_GetMediaItemTake_Source(prev_take)
        RPR_SetMediaItemTake_Source(this_take, prev_source)

        # Increment the cur_position.
        cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")

        # Get the newly created take and name it accordingly.
        this_take = RPR_GetActiveTake(new_item)
        RPR_GetSetMediaItemTakeInfo_String(
            this_take, "P_NAME", prev_item_name, True)

        return (cur_position, new_item)

    def add_clip(self, component, cur_position):
        """Adds the specified clip to the session.

        Args:
            component: The JSON representation of the clip.
            cur_position: The starting position of the component.

        Returns:
            A tuple containing:
                cur_position: The new cursor position, after adding the component.
                new_item: The new REAPER MediaItem that represents the newly added component.
        """
        # Determine the performer of the clip.
        performer = get_performer(component)

        # Get the track that the clip should be inserted into.
        track = self.get_track(performer)
        new_item = RPR_AddMediaItemToTrack(track)

        # Determine if the specified file exists.
        filename = self.folder + "/clips/" + component + ".wav"
        file_exists = RPR_file_exists(filename)
        if file_exists:
            self.available_files.add(component + "\n")
            # Select the proper track.
            RPR_SetOnlyTrackSelected(track)
            # Insert the media
            RPR_InsertMedia(filename, 0)
            cur_position = RPR_GetCursorPosition()
            new_item = RPR_GetSelectedMediaItem(
                0, RPR_CountSelectedMediaItems(0) - 1)
        else:
            self.unavailable_files.add(component + "\n")
            # Set the length and position of the new RPR_MediaItem
            RPR_SetMediaItemInfo_Value(new_item, "D_LENGTH", 1)
            RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", cur_position)

            # Add a RPR_Take to the new media item.
            RPR_AddTakeToMediaItem(new_item)

            # Increment the cur_position.
            cur_position += RPR_GetMediaItemInfo_Value(new_item, "D_LENGTH")

        # Name the take according to the component.
        this_take = RPR_GetActiveTake(new_item)
        RPR_GetSetMediaItemTakeInfo_String(
            this_take, "P_NAME", component, True)

        return (cur_position, new_item)

    def render_components(self, cursor_position):
        # Iterate over each disc
        # pylint: disable=unused-variable
        for disc_name, disc_val in self.discs.iteritems():
            # Iterate over each track
            for track in disc_val:
                prev_item = None
                # Iterate over each component
                if track is not None:
                    for component in track:
                        (cursor_position, prev_item) = \
                            self.add_component(
                                component, cursor_position, prev_item)
                        RPR_SetEditCurPos(cursor_position, False, False)

    def add_component(self, component, cur_position, prev_item):
        """Adds the specified component to the session.

        Args:
            component: The JSON representation of the component.
            cur_position: The starting position of the component.

        Returns:
            A tuple containing:
                cur_position: The new cursor position, after adding the component.
                new_item: The new REAPER MediaItem that represents the newly added component.
        """
        # If this component is a _PAUSE, add an empty item to represent it.
        if component.startswith("_PAUSE"):
            (cur_position, new_item) = \
                self.add_pause(component, cur_position)
        # If this component is a _REPEAT, add a muted copy of the previous item
        # to represent it.
        elif component == "_REPEAT_PREVIOUS_WORD":
            (cur_position, new_item) = self.add_repeat(cur_position, prev_item)
        # Otherwise, add the performed clip to the session.
        else:
            (cur_position, new_item) = self.add_clip(component, cur_position)
        return (cur_position, new_item)

    def generate_report(self):
        """Creates a file that reports the available and unavailable files
        for the project.
        """
        # Export the report of available and unavailable files
        now = str(datetime.datetime.now())
        report_file = open(
            self.folder + "/reaper_clip_splicer_report-" + now + ".txt", "w")
        report_file.write("beaunus REAPER Clip Splicer Report\n")
        report_file.write(now + "\n\n")

        report_file.write("Available components" + "\n")
        report_file.writelines(sorted(self.available_files, key=component_key))
        report_file.write("\n")
        report_file.write("Unavailable components" + "\n")
        report_file.writelines(sorted(self.unavailable_files, key=component_key))


def main():
    """Execute the script.
    """
    # Prompt the user for the JSON file that describes the disc layout
    filename = RPR_GetUserFileNameForRead(None, None, ".json")[1]

    if filename != None:

        # Open the file and load it into an dictionary object.

        file = open(filename, 'r')
        folder = os.path.dirname(filename)

        # Parse the JSON file into an object
        specification = json.loads(file.read())

        my_reaper_clip_splicer = reaper_clip_splicer(specification, folder)

        cursor_position = RPR_GetCursorPosition()

        my_reaper_clip_splicer.render_components(cursor_position)

        my_reaper_clip_splicer.generate_report()

if __name__ == "__main__":
    main()
