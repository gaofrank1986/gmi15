import numpy as np
import json
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
import pandas as pd
from utility import extract_name2,run_thru,pandasModel

from PyQt5.QtWidgets import QApplication,QTableView,QMainWindow,QTableWidgetItem
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("test.ui",self)
        
        self.btn_run.clicked.connect(self.run) 
        self.btn_load_wp.clicked.connect(self.load_info) 
        self.cb_name.currentIndexChanged.connect(self.reset)
        
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._data = data      
        
        self._wdata = {}
        
        self._loaded = False
        
        
        self.cb_name.addItems(list(self._data.keys()))
  
    def reset(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self.label.setText("")

        self._loaded = False       


    def load_info(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self._loaded = True
        self.label.setText("")

        wkind = self._data[self.cb_name.currentText()]['w']
        path = "./data/weapon/"+wkind+".json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        ans = []        
        for wp in data: 
            self._wdata[data[wp]['name']] = wp         
            ans.append(data[wp]['name'])
        self.cb_wp.addItems(ans)
        self.cb_cnum.addItems(self._data[self.cb_name.currentText()]['c'])
    
    def run(self):
        os.remove("./tmp/main.log")
        logger = logging.getLogger()
        logger.setLevel(level=logging.DEBUG)
        fh = logging.FileHandler('./tmp/main.log','w+')
        fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s",datefmt='%m-%d,%H:%M')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.propagate = False
        # self.label.setText("开始计算")                
        # time.sleep(1)
               
        try:
            if self._loaded:


                skill_level = int(self.cb_skill.currentText())
                constellation = int(self.cb_cnum.currentText())
                character = self._data[self.cb_name.currentText()]['name']
                weapon = self._wdata[self.cb_wp.currentText()]
                refine = int(self.cb_refine.currentText())

    
                self.label.setText("{} {} {} {} {}".format(character,constellation,skill_level,weapon,refine))
                
                c = Character(skill_level,constellation,logger)
                c.load_from_json("./data/character/"+character+".json")
                c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,refine)


                rls = Articraft()
                rls.load_json("./data/sub.json")

                save = run_thru("./data/main_run_list.json",c,rls,logger)
                                
                test = OrderedDict(sorted(save.items(),reverse=True))
                N=0
                limit = 4
                # tmp2 = dict()
                for i in test:
                    tmp = test[i]
                    item =  QTableWidgetItem(str(round(i/10000,1))+'万')
                    item.setTextAlignment(Qt.AlignRight)
                    self.tbl_2.setItem(0, N,item)
                    item =  QTableWidgetItem(extract_name2(tmp['head']))
                    item.setTextAlignment(Qt.AlignRight)
                    self.tbl_2.setItem(1, N,item)
                    item =  QTableWidgetItem(extract_name2(tmp['glass']))
                    item.setTextAlignment(Qt.AlignRight)
                    self.tbl_2.setItem(2, N,item)
                    item =  QTableWidgetItem(extract_name2(tmp['cup']))
                    item.setTextAlignment(Qt.AlignRight)
                    self.tbl_2.setItem(3, N,item)
                    N+=1

                    if N==limit:
                        break
                # table = pd.DataFrame(tmp2)
                # table.index =  ['damage','head','glass','cup']
                # table.column = ['first','second','third','fourth']

                # self.label.setText("{}".format(c.name))
                # print(table)
                # model = pandasModel(table)
                # self.tb_rsl.setHorizontalHeaderLabels(['Name', 'Age', 'Sex', 'Add'])

                # self.tb_rsl.setModel(model)
                self.label.setText("计算成功")

            else:
                self.label.setText("请加载数据")
        except:
            self.label.setText("计算失败")

        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
        



# class QTextEditLogger(logging.Handler):
#     def __init__(self, parent):
#         super().__init__()
#         self.widget = QtWidgets.QPlainTextEdit(parent)
#         self.widget.setReadOnly(True)

#     def emit(self, record):
#         msg = self.format(record)
#         self.widget.appendPlainText(msg)


# class MyText(QtWidgets.QPlainTextEdit):
#     def __init__(self, parent=None):
#         super().__init__(parent)

#         logTextBox = QTextEditLogger(self)
#         # You can format what is printed to text box
#         logTextBox.setFormatter(logging.Formatter("%(asctime)s — %(levelname)s — %(message)s",datefmt='%m-%d,%H:%M'))
#         logging.getLogger().addHandler(logTextBox)
#         # You can control the logging level
#         logging.getLogger().setLevel(logging.DEBUG)


#     def test(self):
#         logging.debug('damn, a bug')
#         logging.info('something to remember')
#         logging.warning('that\'s not right')
#         logging.error('foobar')


if __name__ == "__main__":
    


    
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()

    win.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
        logger = logging.getLogger()
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
    
    # app = QtWidgets.QApplication(sys.argv)
    # dlg = MyDialog()
    # dlg.show()
    # dlg.raise_()
    # sys.exit(app.exec_())