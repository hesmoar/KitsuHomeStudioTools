from krita import *
import traceback

print("[KITSU] Krita script started.")

def create_new_document():
    """Create a new Krita document with 1920x1080 resolution"""
    try:
        # Get the Krita application instance
        app = Krita.instance()
        
        # Create a new document
        doc = app.createDocument(
            1920,  # width
            1080,  # height
            "KitsuTask",  # name
            "RGBA",  # color model
            "U8",  # color depth
            "sRGB-elle-V2-srgbtrc.icc",  # color profile
            72.0  # resolution
        )
        
        # Add the document to the application
        app.activeWindow().addView(doc)
        
        print("[KITSU] Document created successfully.")
        return True
    except Exception as e:
        print(f"[KITSU] Error creating document: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("[KITSU] __main__ block running.")
    create_new_document()
else:
    print("[KITSU] Script imported, not run as main.")