from uitools.qt import QtGui, QtCore

from . import setup



class RenderSetupDialog(QtGui.QWidget):

    def __init__(self):
        super(RenderSetupDialog, self).__init__()
        self._setup_ui()
      
    def _setup_ui(self):

        layout = QtGui.QVBoxLayout()

        self.steps = []

        for func in setup.steps:
            button = QtGui.QCheckBox(func.__name__.replace('_', ' ').title())
            button.setChecked(True)
            layout.addWidget(button)
            self.steps.append((func, button))

        toggle_layout = QtGui.QHBoxLayout()

        on_button = QtGui.QPushButton('All On')
        on_button.clicked.connect(lambda: self.check_all(True))
        toggle_layout.addWidget(on_button)

        off_button = QtGui.QPushButton('All Off')
        off_button.clicked.connect(lambda: self.check_all(False))
        toggle_layout.addWidget(off_button)

        layout.addLayout(toggle_layout)

        self.button = QtGui.QPushButton("Setup Render")
        self.button.clicked.connect(self.run_setup)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle("Setup Render")

    def check_all(self, value):
        for func, button in self.steps:
            button.setChecked(value)

    def run_setup(self):
        for func, button in self.steps:
            if button.isChecked():
                print '>>>', func.__name__
                func()


dialog = None

def run():
    
    # Hold onto a reference so that it doesn't automatically close.
    global dialog
    
    if dialog:
        dialog.close()
    
    dialog = RenderSetupDialog()
    dialog.show()
