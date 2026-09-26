from __future__ import annotations
import sys
from PyQt6.QtWidgets import QApplication
from desktop.reference_window import ReferenceWindow as Window

def main():
    app=QApplication(sys.argv);app.setApplicationName('Ember');app.setOrganizationName('Cyber Pulse')
    window=Window()
    if window.store.get('start_minimized'):window.showMinimized()
    else:window.show()
    return app.exec()

if __name__=='__main__':raise SystemExit(main())
