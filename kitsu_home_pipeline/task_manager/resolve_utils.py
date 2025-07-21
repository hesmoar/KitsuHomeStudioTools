import sys
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
#import DaVinciResolveScript as dvr

def setup_resolve():
    try:
        # Attempt to import the DaVinci Resolve scripting module
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if not resolve:
            print("Unable to connect to DaVinci Resolve.")
            return
    except Exception as e:
        print(f"Error setting up DaVinci Resolve: {e}")
    
    project_manager = resolve.GetProjectManager()
    new_project = project_manager.CreateProject("PipeTesting")