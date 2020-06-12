from Painting_Download import Painting_download
from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog, QTextBrowser
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Signal, QObject
from threading import Thread

class MySignals(QObject):
    text_print = Signal(QTextBrowser, str)
    progress_update = Signal(int)

MS = MySignals()
PD = Painting_download()

class Pixiv_painting:

    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        #可批量下载，如:111111,222222(逗号用英文)
        self.ui.lineEdit.setPlaceholderText('可批量下载，如:111111,222222(逗号用英文)')
        self.ui.pushButton.clicked.connect(self.get_paint)
        self.ui.pushButton_2.clicked.connect(self.get_path)
        MS.progress_update.connect(self.setProgress)
        MS.text_print.connect(self.printPace)

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.lineEdit_2.setText(path)

    def setProgress(self, value):
        self.ui.progressBar.setValue(value)

    def printPace(self, element, text):
        element.append(text)
        element.ensureCursorVisible()

    def get_paint(self):
        def State():
            state = True
            if self.ui.lineEdit.text() == '' or self.ui.lineEdit_2.text() == '':
                QMessageBox.warning(self.ui, '警告', 'ID与路径不能为空！！！')
                state = False
            return state

        def paint_thread():
            self.ui.textBrowser.setPlainText('======开始爬取======')
            PD.painting_id(self.ui.lineEdit.text())
            PD.run_download(self.ui.lineEdit_2.text())
            self.ui.progressBar.setRange(PD.urls())
            MS.text_print.emit(self.ui.textBrowser, PD.download[1])
            MS.progress_update.emit(PD.download[0])
        # if State():
        #     paint_thread()
        try:
            if State():
                thread = Thread(target=paint_thread)
                thread.setDaemon(False)
                thread.start()
                # thread.join()
                # thread.run()
        except:
            QMessageBox.critical(self.ui, '错误', '爬取失败，连接超时！！！')

app = QApplication([])
pixiv_painting = Pixiv_painting()
pixiv_painting.ui.show()
app.exec_()
