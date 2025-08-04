# timeline_utils.py
import os
import pprint
import pprint
from kitsu_home_pipeline.integrations.resolve.project_utils import get_current_project
from kitsu_home_pipeline. utils.file_utils import get_unique_filename
resolve_timeline_name = None

def get_timeline(project):
    """Get the current timeline of the project."""
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("Error: No current timeline found.")
        return None
    return timeline

def get_timeline_name(project):
    """Get the timeline name prefixed by the project name."""
    timeline = get_timeline(project)
    if timeline:
        resolve_timeline_name = timeline.GetName()
        return f"{project.GetName()}_{timeline.GetName()}"
    return None

def get_clips_from_timeline(project):
    """Get clips from the current timeline."""
    timeline = get_timeline(project)
    if timeline:
        return timeline.GetItemListInTrack("video", 1)
    return []

def get_timeline_markers(project):
    timeline = get_timeline(project)
    if timeline:
        pprint.pprint(timeline.GetMarkers())
        return timeline.GetMarkers()
    return []

def get_timeline_markInOut(project):
    """Get and store the full cut frame range from the timeline."""

    timeline = get_timeline(project)
    if not timeline:
        print("No current timeline found.") 
        return []

    MarkInOut = timeline.GetMarkInOut()
    full_cut_markIn = MarkInOut.get("video", {}).get("in", 0)
    full_cut_markOut = MarkInOut.get("video", {}).get("out", 0)


    return full_cut_markIn, full_cut_markOut

def export_edl(project, export_directory):
    """Export an EDL file with a unique filename."""
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("No current timeline found.")
        return False
    
    edl_name = get_timeline_name(project)
    if not edl_name:
        return None
    
    edlFilePath, _ = get_unique_filename(edl_name, export_directory, "edl")
    if not edlFilePath:
        return
    
    try:
        if timeline.Export(edlFilePath, project.EXPORT_EDL):
            print(f"Timeline exported to {edlFilePath} successfully.")
        else:
            print("Timeline export failed.")
    except Exception as e:
        print(f"Error exporting timeline: {e}")
    return edlFilePath


def export_otio(project, export_directory):
    """Export an OTIO file with a unique filename"""
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("No current timeline found.")
        return False
    
    otio_name = get_timeline_name(project)
    if not otio_name:
        return None
    
    otioFilePath, _ = get_unique_filename(otio_name, export_directory, "otio")
    if not otioFilePath:
        return
    
    try:
        if timeline.Export(otioFilePath, project.EXPORT_OTIO):
            print(f"SUCCESFULLY EXPORTED TIMELINE TO: {otioFilePath}")
        else:
            print("Timeline export failed.")
    except Exception as e:
        print(f"Error exporting timeline: {e}")
    return otioFilePath
