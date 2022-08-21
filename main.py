# Main function to call for Classfication
# Charles Hill
# 06/05/19

# Python Standard Libraries
import sys

# Site-packages
from PyQt5 import QtWidgets

# User Functions
from ManualClassification import UI_classification

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_win = UI_classification(test=True)
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()