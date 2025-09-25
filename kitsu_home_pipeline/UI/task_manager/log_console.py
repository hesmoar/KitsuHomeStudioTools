import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton

class EmittingStream:
    def __init__(self, text_edit, original_stream):
        self.text_edit = text_edit
        self.original_stream = original_stream

    def write(self, text):
        if text.strip():  # avoid empty newlines
            #self.text_edit.moveCursor(self.text_edit.textCursor().End)
            self.text_edit.append(text)
        self.original_stream.write(text)

    def flush(self):
        self.original_stream.flush()

class LogConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Integrated Console")
        self.setGeometry(750, 250, 700, 300)

        layout = QVBoxLayout(self)

        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        btn = QPushButton("Test Print", self)
        btn.clicked.connect(lambda: print("Hello from inside the GUI!"))
        layout.addWidget(btn)

        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # Redirect stdout and stderr
        sys.stdout = EmittingStream(self.console, self._original_stdout)
        sys.stderr = EmittingStream(self.console, self._original_stderr)

        sys.stdout = EmittingStream(self.console, self._original_stdout)
        sys.stderr = EmittingStream(self.console, self._original_stderr)
"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ConsoleDemo()
    win.show()
    sys.exit(app.exec())
"""