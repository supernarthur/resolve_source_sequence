#!/usr/bin/env python3.6
"""
source_sequence.py
"""

import tkinter as tk
from common.python_get_resolve import GetResolve


class Interface(tk.Frame):
    """
    Main window to dial settings before creating the source_sequence
    """
    def __init__(self, window, resolve, **kwargs):

        # Init
        tk.Frame.__init__(self, window, **kwargs)
        self.pack(fill=tk.BOTH)

        # Data
        self.window = window
        self.resolve = resolve
        self.project_manager = resolve.GetProjectManager()
        self.resolve_project = self.project_manager.GetCurrentProject()
        self.fps = round(float(
            self.resolve_project.GetSetting("timelineFrameRate")))

        # Widgets
        self.create_widgets()

    def create_widgets(self):

        self.tl_frame = tk.LabelFrame(self.window,
                                      text="Select timelines",
                                      padx=10,
                                      pady=10)
        self.tl_frame.pack(fill=tk.BOTH)
        self.timeline_checkbox_list = []
        for index in range(int(self.resolve_project.GetTimelineCount())):
            timeline = self.resolve_project.GetTimelineByIndex(index + 1)
            self.timeline_checkbox_list.append({})
            self.timeline_checkbox_list[index]["variable"] = tk.IntVar()
            self.timeline_checkbox_list[index]["name"] = timeline.GetName()
            self.timeline_checkbox_list[index]["checkbox"] = tk.Checkbutton(
                self.tl_frame,
                variable=self.timeline_checkbox_list[index]["variable"],
                text=timeline.GetName(),
                width=20,
                anchor=tk.W)
            self.timeline_checkbox_list[index]["checkbox"].pack()

        self.options_frame = tk.LabelFrame(self.window,
                                           text="Options",
                                           padx=10,
                                           pady=10)
        self.options_frame.pack(fill="both")
        self.handles_label = tk.Label(self.options_frame,
                                      text="Handles length")
        self.handles_label.grid(row=0, column=0, sticky=tk.W)
        self.handles = tk.IntVar()
        self.handles.set(self.fps)
        self.handles_field = tk.Entry(self.options_frame,
                                      textvariable=self.handles,
                                      width=30)
        self.handles_field.grid(row=0, column=1)
        self.tl_name_label = tk.Label(self.options_frame,
                                      text="Source sequence name",
                                      anchor=tk.W)
        self.tl_name_label.grid(row=1, column=0, sticky=tk.W)
        self.tl_name = tk.StringVar()
        self.tl_name.set("source_sequence")
        self.tl_name_field = tk.Entry(self.options_frame,
                                      textvariable=self.tl_name,
                                      width=30)
        self.tl_name_field.grid(row=1, column=1)

        self.buttons_frame = tk.Frame(self.window,
                                      padx=10,
                                      pady=10)
        self.buttons_frame.pack(fill="both")
        self.create_button = tk.Button(self.buttons_frame,
                                       text="Create",
                                       command=self._create_source_sequence)
        self.create_button.pack(side=tk.LEFT)
        self.cancel_button = tk.Button(self.buttons_frame,
                                       text="Cancel",
                                       command=self.master.destroy)
        self.cancel_button.pack(side=tk.LEFT)

    def _create_source_sequence(self):
        tl_list = [tl["name"] for tl in self.timeline_checkbox_list
                   if tl["variable"].get() == 1]
        main(self.resolve,
             self.tl_name.get(),
             tl_list,
             self.handles.get())
        self.quit()


def get_limelines_by_name(resolve_project, timeline_names):
    """
    For a given list of timeline names, will output a list of timeline objects
    """
    all_timelines = []
    output = []
    for index in range(int(resolve_project.GetTimelineCount())):
        all_timelines.append(resolve_project.GetTimelineByIndex(index + 1))
    for timeline_name in timeline_names:
        for timeline_object in all_timelines:
            if timeline_object.GetName() == timeline_name:
                output.append(timeline_object)
                break
    return output


def get_tl_items(resolve, timeline_names):
    """
    For a given list of timeline names, will output a list of all
    timeline items in video tracks
    """
    project_manager = resolve.GetProjectManager()
    resolve_project = project_manager.GetCurrentProject()
    scope = get_limelines_by_name(resolve_project, timeline_names)
    all_clips = []
    for timeline in scope:
        for video_track_index in range(int(timeline.GetTrackCount("video"))):
            all_clips += timeline.GetItemListInTrack("video",
                                                     video_track_index + 1)
    return all_clips


def extract_tl_item_info(timeline_item):
    """
    For a given timeline item object, will return a dict with the info:
        "mp_item": corresponding media pool item
        "segments": list of (in, out) edited segments (floats)
        "media_id": unique media ID
    """
    mediapool_item = timeline_item.GetMediaPoolItem()
    media_id = mediapool_item.GetMediaId()
    segments = [(int(timeline_item.GetLeftOffset()),
                 int(timeline_item.GetRightOffset()))]
    return {"mp_item": mediapool_item,
            "media_id": media_id,
            "segments": segments}


def get_clip_index_by_media_id(clip_info, clip_list):
    """
    For a given clip info dict, will return the index at which it is found
    in the list by comparing media_id
    If nothing is found, return None
    """
    media_id_list = [item["media_id"] for item in clip_list]
    try:
        output = media_id_list.index(clip_info["media_id"])
    except ValueError:
        return None
    else:
        return output


def are_segments_mergeable(seg1, seg2, handle_length):
    if seg1[0] <= seg2[0]:
        first, second = seg1, seg2
    else:
        first, second = seg2, seg1
    return first[1] >= (second[0] - handle_length * 2)


def compute_new_segments(segments, handle_length):
    """
    Reduces a list of segments to only the useful ones, by merging them
    Will merge clips if they would overlap when handles are applied
    Credit to this repo for help
    https://github.com/AlexandreDecan/portion/blob/master/portion/interval.py
    """
    # We sort by upper bound to simplify merging
    # Basically if sorted, 1 cannot be merged with 3
    # if it cannot be merged with 2
    segments.sort(key=lambda item: item[0])

    if len(segments) == 1:
        return segments
    elif len(segments) >= 2:
        index = 0
        while index < len(segments) - 1:
            current = segments[index]
            next_one = segments[index + 1]
            if are_segments_mergeable(current, next_one, handle_length):
                lower_bound = min(current[0], next_one[0])
                upper_bound = max(current[1], next_one[1])
                merged = (lower_bound, upper_bound)
                segments.pop(index)  # This is current
                segments.pop(index)  # This is next_one
                segments.insert(index, merged)  # We replace them by merged
            else:
                index += 1
    return segments


def compute_source_sequence(clip_info_list, handle_length):
    """
    From a list of dicts generated by extract_tl_item_info(),
    will generate a new list of the same format, with only the useful media
    Basically, for each segment,
        If it overlaps with nothing, we add it to the source sequence
        If it is completely bound by an already existing segment, we do nothing
        If it overlaps with one or more of the already existing segments,
            we compute a new one with the useful length
    """
    output = []
    for clip_info in clip_info_list:
        index = get_clip_index_by_media_id(clip_info, output)
        if index is not None:
            # The clip already exists in the output, we do a dirty
            # addition to the segments
            output[index]["segments"] = (output[index]["segments"]
                                         + clip_info["segments"])
        else:
            # The clip is not in the output, so we add it as is
            output.append(clip_info)

    # We loop on the output list to merge segments in place where possib:e
    for index, output_clip_info in enumerate(output):
        segments = output_clip_info["segments"]
        if len(segments) > 1:
            output[index]["segments"] = compute_new_segments(segments,
                                                             handle_length)
    return output


def create_source_sequence(resolve, name, clip_info_list):
    """
    Creates a source sequence from a given name and a list of info
    generated by compute_source_sequence() or extract_tl_item_info()
    """
    project_manager = resolve.GetProjectManager()
    resolve_project = project_manager.GetCurrentProject()
    media_pool = resolve_project.GetMediaPool()
    edit_metadata = []
    for clip in clip_info_list:
        for segment in clip["segments"]:
            edit_metadata.append({"mediaPoolItem": clip["mp_item"],
                                  "startFrame": segment[0],
                                  "endFrame": segment[1]})
    timeline = media_pool.CreateEmptyTimeline(name)
    resolve_project.SetCurrentTimeline(timeline)
    for edit in edit_metadata:
        status = media_pool.AppendToTimeline([edit])
    return timeline


def main(resolve, source_seq_name, seq_list, handle_length):
    output = []
    for clip in get_tl_items(resolve, seq_list):
        output.append(extract_tl_item_info(clip))
    output = compute_source_sequence(output, handle_length)
    timeline = create_source_sequence(resolve,
                                      source_seq_name,
                                      output)
    project = resolve.GetProjectManager().GetCurrentProject()
    project.SetCurrentTimeline(timeline)


def main_gui():
    resolve = GetResolve()
    if resolve is not None:
        window = tk.Tk(className="Create source sequence")
        interface = Interface(window, resolve)
        interface.mainloop()
    else:
        print("Cannot connect to resolve API")
        print("Please check help to solve this issue")


if __name__ == '__main__':
    main_gui()
