"""AutoCPD — CPD Diary & Automation Tool.

Entry point: run this file to launch the application.
"""

from ui.app import AutoCPDApp


def main():
    app = AutoCPDApp()
    app.mainloop()


if __name__ == "__main__":
    main()
