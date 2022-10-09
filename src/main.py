import os
import sys
import time

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QShortcut
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from about import AboutDialog


def about():
    dlg = AboutDialog()
    dlg.exec_()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.tabs.setStyleSheet("""
            QTabBar {
                background: #F0F0F0;          
            }
            QTabBar::tab {
                background: #F0F0F0;
                color: #3b3b3b;
                height: 20px;
                margin-left: 5px;
            }
            QTabBar::tab::after {
                content: "|";
            }
            QTabBar::tab:selected {
                background-color:  #c2c2c2;
                color: #000000;
                border: 1px solid #a3a0a3;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom-left-radius: -4px;
                border-bottom-right-radius: -4px;
                padding-left: 5px;
                padding-right: 5px;

            }
            QTabBar::close-button {
                image: url('data/images/close.svg');
                subcontrol-position: right;
            }
            QTabBar::close-button:hover {
                image: url('data/images/close.svg');
            }
            QLabel {
                background-color: #23272a;
                font-size: 22px;
                padding-left: 5px;
                color: white;
            }
        """)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(18, 18))
        navtb.setAllowedAreas(Qt.TopToolBarArea)
        navtb.setFloatable(False)
        navtb.setMovable(False)
        self.addToolBar(navtb)

        navtb.setStyleSheet("""
            QToolButton {
                border: 2px;
                padding: 1px 4px;
                background: transparent;
                border-radius: 4px;

            }
            QToolButton:hover{
                border: 1px;
                background: #c2c2c2;
            }
            QToolButton:selected { /* when selected using mouse or keyboard */
                background: #a8a8a8;
            }
            QToolButton:pressed {
                background: #888888;
            }
        """)

        back_btn = QAction(QIcon(os.path.join('data/images', 'back.svg')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(os.path.join('data/images', 'forward.svg')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(QIcon(os.path.join('data/images', 'refresh.svg')), "reload", self)
        reload_btn.setStatusTip("reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        stop_btn = QAction(QIcon(os.path.join('data/images', 'stop.svg')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()
        self.httpsicon.setPixmap(QPixmap(os.path.join('data/images', 'ssloff.svg')))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        self.urlbar.setStyleSheet("""
            border: 1px;
            border-radius: 10px;
            padding: 3;
            background: #fff;
            selection-background-color: darkgray;
            left: 5px;
            right: 5px;
            font: 12px/14px sans-serif
        """)

        home_btn = QAction(QIcon(os.path.join('data/images', 'home.svg')), "Home", self)
        home_btn.setStatusTip("Go Home")
        home_btn.triggered.connect(lambda: self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        # Right menubar

        self.menu_bar = QMenuBar()

        self.menu_bar.setMinimumSize(18, 18)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                border: 2px;
                padding: 10px 2px;
                max-width: 50px;
            }
            QMenuBar::item {
                border: 2px;
                padding: 1px 4px;
                background: transparent;
                border-radius: 4px;
                height: 24px;
            }
            QMenuBar::item:selected { /* when selected using mouse or keyboard */
                background: #c2c2c2;
            }
            QMenuBar::item:pressed {
                background: #c2c2c2;
            }
        """)
        self.file_menu = QMenu('MENU', self)
        self.file_menu.setIcon(QIcon(os.path.join('data/images', 'menu.svg')))

        bookmarks_action = QAction(QIcon(os.path.join('data/images', 'bookmarkmenu.svg')), "Bookmarks", self)
        bookmarks_action.setStatusTip("Open all bookmarks")
        bookmarks_action.triggered.connect(lambda _: self.bookmarks())
        self.file_menu.addAction(bookmarks_action)

        new_tab_action = QAction(QIcon(os.path.join('data/images', 'newtab.svg')), "New Tab", self)
        new_tab_action.setStatusTip("Open new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        self.file_menu.addAction(new_tab_action)

        open_file_action = QAction(QIcon(os.path.join('data/images', 'open.svg')), "Open file", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        self.file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('data/images', 'save.svg')), "Save page to file", self)
        save_file_action.setStatusTip("Open from file")
        save_file_action.triggered.connect(self.save_file)
        self.file_menu.addAction(save_file_action)

        about_action = QAction(QIcon(os.path.join('data/images', 'info.svg')), "About", self)
        about_action.setStatusTip("Find out more about Solenox Project")
        about_action.triggered.connect(about)
        self.file_menu.addAction(about_action)

        self.menu_bar.addMenu(self.file_menu)

        navtb.addWidget(self.menu_bar)

        self.add_new_tab(QUrl('https://www.google.com/'), 'HomePage')

        '''Shortcuts'''

        self.shortcut_open = QShortcut(QKeySequence('F5'), self)
        self.shortcut_open.activated.connect(lambda: self.tabs.currentWidget().reload())

        ''' Progress bar '''
        self.progressBar = QProgressBar()
        self.progressBar.setGeometry(0, 0, 50, 25)
        self.progressBar.setFont(QFont('Times', 7))
        self.progressBar.setStyleSheet("""
            QProgressBar {
                max-width: 200px;
                height: 15px;
                padding: 0;
                text-align: center;

            }
            QProgressBar::chunk{
                border: 2px;
                border-radius: 4px;
                background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #49D697, stop: 1 white);
            }
        """)
        self.statusBar().addPermanentWidget(self.progressBar)

        self.show()

        self.setWindowIcon(QIcon(os.path.join('data/images', 'icon.svg')))

    @QtCore.pyqtSlot()
    def loadStartedHandler(self):
        print(time.time(), ": load started")

    @QtCore.pyqtSlot(int)
    def loadProgressHandler(self, prog):
        print(time.time(), ":load progress", prog)
        # self.statusBar().showMessage(str(prog) + '%')
        self.progressBar.setValue(prog)

    @QtCore.pyqtSlot()
    def loadFinishedHandler(self):
        print(time.time(), ": load finished")
        self.statusBar().showMessage('Ready')

    @QtCore.pyqtSlot("QWebEngineDownloadItem*")
    def on_downloadRequested(self, download):
        old_path = download.url().path()  # download.path()
        suffix = QtCore.QFileInfo(old_path).suffix()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*." + suffix
        )
        if path:
            download.setPath(path)
            download.accept()

    def bookmarks(self):
        pass

    def mycontextMenuEvent(self, event):
        url = 'view-source:' + self.urlbar.text()
        menu = QtWidgets.QMenu(self)
        reloadAction = menu.addAction(QIcon(os.path.join('data/images', 'refresh.svg')), "Reload page")
        reloadAction.triggered.connect(lambda: self.tabs.currentWidget().reload())

        innewtabAction = menu.addAction(QIcon(os.path.join('data/images', 'newtab.svg')), "Open in new tab")
        innewtabAction.triggered.connect(lambda: self.add_new_tab())

        sourceAction = menu.addAction(QIcon(os.path.join('data/images', 'pgsrc.svg')), "View page source")
        sourceAction.triggered.connect(lambda: self.add_new_tab(qurl=QUrl(url)))
        menu.exec_(event.globalPos())

    def actionClicked(self):
        action = self.sender()
        print(action.text())
        print(action.data())

    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl.fromLocalFile(os.path.dirname(os.path.realpath(__file__)) + '/data/files/blank/index.html')

        browser = QWebEngineView()
        browser.settings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        browser.page().fullScreenRequested.connect(lambda request: request.accept())
        browser.setUrl(qurl)
        QtWebEngineWidgets.QWebEngineProfile.defaultProfile().downloadRequested.connect(
            self.on_downloadRequested
        )

        browser.loadStarted.connect(self.loadStartedHandler)
        browser.loadProgress.connect(self.loadProgressHandler)
        browser.loadFinished.connect(self.loadFinishedHandler)

        browser.contextMenuEvent = self.mycontextMenuEvent
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def view(self):
        url = self.urlbar.text()
        url = f"view-source:{url}"
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        self.setWindowTitle("Solenox Browser")

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "*.htm *.html"
                                                  "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "save page as", "",
                                                  "*.htm *.html"
                                                  "All files (*.*)")
        if filename:
            html = self.tabs.currentWidget().page().toHtml()
            with open(filename, 'w') as f:
                f.write(html)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("/data/files/blanks/index.html"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            return

        if q.scheme() == 'https':
            self.httpsicon.setPixmap(QPixmap(os.path.join('data/images', 'sslon.svg')))
        else:
            self.httpsicon.setPixmap(QPixmap(os.path.join('data/images', 'ssloff.svg')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(999)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
