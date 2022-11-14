import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap

from design import design
from recognition.main import response, graph_usage

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.browse_folder)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)

    def browse_folder(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open File', './', "Image (*.png *.jpg *jpeg)")
        if file:
            print(file)
        pixmap = QPixmap(file)
        'pixmap.scaled(width=self.label.width(), height=self.label.height())'

        self.label.setPixmap(pixmap)

        self.label.setScaledContents(True)

        self.add_info(file)

    def add_info(self, path):
        _, recog_num = response(path)
        self.label_2.setText(recog_num)
        if graph_usage.find_and_choose(recog_num):
            dict_driver = graph_usage.find_and_choose(recog_num)
            self.label_3.setText(dict_driver["FIRST_NAME"])
            self.label_4.setText(dict_driver["LAST_NAME"])
        else:
            self.label_3.setText("Нет информации")
            self.label_4.setText("Нет информации")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()