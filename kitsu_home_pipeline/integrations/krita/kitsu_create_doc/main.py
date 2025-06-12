from krita import *

class KitsuCreateDocExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "kitsu_create_1920x1080_doc",
            "Create 1920x1080 Kitsu Document",
            "tools/scripts"
        )
        action.triggered.connect(self.create_doc)

    def create_doc(self):
        app = Krita.instance()
        doc = app.createDocument(
            1920, 1080, "KitsuTask", "RGBA", "U8", "sRGB-elle-V2-srgbtrc.icc", 72.0
        )
        app.activeWindow().addView(doc)

Krita.instance().addExtension(KitsuCreateDocExtension(Krita.instance())) 