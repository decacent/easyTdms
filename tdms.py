# -*- coding: utf-8 -*-
"""


@author: Wnight
"""
import sys
import scipy.io as sio
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox,QApplication
from nptdms import TdmsFile
import numpy as np
from tdms_ui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import gc

def read_tdms(fn):
    tdms_file = TdmsFile(fn)
    t1 = tdms_file.groups()
    t2 = tdms_file.group_channels(t1[0])
    t2_0 = t2[0].channel
    t2_1 = t2[1].channel
    channel1 = tdms_file.object(t1[0], t2_0)
    channel2 = tdms_file.object(t1[0], t2_1)
    sam=channel1.property('wf_samples')

    current = channel1.data
    voltage = channel2.data
    time = channel1.time_track()
    data = np.array((time, current * 500, voltage))
    return data,sam

def abf_to_mat(fn):
    pass

class Tdms_read(QMainWindow, Ui_Read_Tdms):
    def __init__(self, parent=None):
        super(Tdms_read, self).__init__(parent)
        self.setupUi(self)

        self.tdms_data=None

        self.figure_tdms = plt.figure(5)
        self.ax_tdms = self.figure_tdms.add_subplot(111)
        self.figure_tdms.subplots_adjust(left=0.1, right=0.9)
        self.canvas_tdms = FigureCanvas(self.figure_tdms)
        self.toolbar_tdms = NavigationToolbar(self.canvas_tdms, self)
        self.verticalLayout_tdms.addWidget(self.toolbar_tdms)
        self.verticalLayout_tdms.addWidget(self.canvas_tdms)
        self.tdms_is_view = False
        self.axs_tdms = self.ax_tdms.twinx()

        self.openfile.clicked.connect(self.loadtdms)
        self.plotdata.clicked.connect(self.plottdms)
        self.savedata.clicked.connect(self.savetdms)
        self.tdms_span = SpanSelector(self.axs_tdms, self.tdms_onselect, 'horizontal', useblit=True, button=3,
                                      rectprops=dict(alpha=0.3, facecolor='g'))


    def tdms_onselect(self,xmin, xmax):
        if self.tdms_is_view:
            self.checkBox_5_tdms.setChecked(True)
            self.spinBox_8_tdms.setValue(int(xmin))
            self.spinBox_9_tdms.setValue(int(xmax))
            self.plottdms()

    def loadtdms(self):
        self.statusBar().showMessage("打开tdms文件")
        self.tdms_fn = QFileDialog.getOpenFileName(filter='TDMS Files (*.tdms)')[0]
        if self.tdms_fn == '':
            self.statusBar().showMessage("未选择文件")
            pass
        else:
            self.statusBar().showMessage("正在读取Tdms数据..")
            self.tdms_data,self.tdms_sam=read_tdms(self.tdms_fn)
            self.statusBar().showMessage('Tdms数据读取完成..' + os.path.basename(self.tdms_fn))
            self.plottdms()
            QMessageBox.information(self, "标题", "数据读取完成", QMessageBox.Ok)



    def plottdms(self):
        if self.tdms_data is None:
            self.statusBar().showMessage('无Tdms数据')
            QMessageBox.information(self, "标题", "无Tdms数据", QMessageBox.Ok)
        else:
            if self.checkBox_5_tdms.isChecked():
                self.start = self.spinBox_8_tdms.value() * self.tdms_sam
                self.end = self.spinBox_9_tdms.value() * self.tdms_sam
                if self.start >= self.end:
                    QMessageBox.information(self, "标题", "请正确设置时间范围", QMessageBox.Ok)
                    pass
                else:
                    self.ax_tdms.cla()
                    self.axs_tdms.cla()
                    gc.collect()
                    self.ax_tdms.plot(self.tdms_data[0, self.start:self.end], self.tdms_data[1, self.start:self.end], 'k')
                    self.ax_tdms.set_xlabel('Time/s')
                    self.ax_tdms.set_ylabel('Current/nA')

                    self.axs_tdms.plot(self.tdms_data[0, self.start:self.end], self.tdms_data[2, self.start:self.end], 'r')
                    self.axs_tdms.set_ylabel('Voltage/V')
                    self.canvas_tdms.draw()
                    self.statusBar().showMessage('绘制TDMS')
                    self.tdms_is_view = True
            else:
                self.ax_tdms.cla()
                self.axs_tdms.cla()
                self.ax_tdms.plot(self.tdms_data[0, :], self.tdms_data[1, :], 'k')
                self.ax_tdms.set_xlabel('Time/s')
                self.ax_tdms.set_ylabel('Current/nA')
                self.axs_tdms.plot(self.tdms_data[0, :], self.tdms_data[2, :], 'r')
                self.axs_tdms.set_ylabel('Voltage/V')
                self.canvas_tdms.draw()
                self.statusBar().showMessage('绘制TDMS')
                self.tdms_is_view=True

    def savetdms(self):
        if self.tdms_data is None:
            self.statusBar().showMessage('无Tdms数据')
            QMessageBox.information(self, "标题", "无Tdms数据", QMessageBox.Ok)
            return None
        file_choices = "mat (*.mat);;CSV (*.csv)"
        path = QFileDialog.getSaveFileName(self, 'Save file', '', file_choices)
        if path:
            if self.checkBox_5_tdms.isChecked():
                self.start = self.spinBox_8_tdms.value() * self.tdms_sam
                self.end = self.spinBox_9_tdms.value() * self.tdms_sam
                if self.start >= self.end:
                    QMessageBox.information(self, "标题", "请正确设置时间范围", QMessageBox.Ok)
                    return  None
                else:
                    self.part_tdms=self.tdms_data[:,self.start:self.end]
                    if path[1] == 'mat (*.mat)':
                        sio.savemat(path[0], {'f': self.part_tdms.T})
                        self.statusBar().showMessage('Saved to %s' % path[0])
                        self.statusBar().showMessage('数据保存完成')
                        QMessageBox.information(self, "标题", "数据保存完成", QMessageBox.Ok)
                    elif path[1] == 'CSV (*.csv)':
                        np.savetxt(path[0], self.part_tdms.T, delimiter=',',header='time (ms),current (nA),Voltage (V)')
                        self.statusBar().showMessage('Saved to %s' % path[0])
                        self.statusBar().showMessage('数据保存完成')
                        QMessageBox.information(self, "标题", "数据保存完成", QMessageBox.Ok)
            else:
                if path[1] == 'mat (*.mat)':
                    sio.savemat(path[0], {'f': self.tdms_data.T})
                    self.statusBar().showMessage('Saved to %s' % path[0])
                    self.statusBar().showMessage('数据保存完成')
                    QMessageBox.information(self, "标题", "数据保存完成", QMessageBox.Ok)
                elif path[1] == 'CSV (*.csv)':
                    np.savetxt(path[0], self.tdms_data.T, delimiter=',',header='time (ms),current (nA),Voltage (V)')
                    self.statusBar().showMessage('Saved to %s' % path[0])
                    self.statusBar().showMessage('数据保存完成')
                    QMessageBox.information(self, "标题", "数据保存完成", QMessageBox.Ok)

        else:
            self.statusBar().showMessage('请选择保存文件位置')
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Tdms_read()
    mainWindow.show()
    sys.exit(app.exec_())