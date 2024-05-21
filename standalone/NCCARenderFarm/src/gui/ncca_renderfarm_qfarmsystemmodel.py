from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os, shutil

from gui.ncca_qmessagebox import NCCA_QMessageBox
from gui.ncca_qinputdialog import NCCA_QInputDialog
from ncca_qimageviewer import NCCA_QImageViewer
from ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qprogressdialog import NCCA_QProgressDialog
from styles import *

import paramiko
import stat

import socket

class NCCA_Error(Exception):
    pass

class NCCA_RenderfarmConnectionFailed(NCCA_Error):
    pass

class NCCA_RenderfarmIncorrectLogin(NCCA_Error):
    pass

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
import paramiko

class NCCA_RenderFarm_QFarmSystemModel(QAbstractItemModel):
    def __init__(self, username, password, parent=None):
        super().__init__(parent)
        self.renderfarm = None
        self.root_path = "/"
        self.root_item = None
        self.username = username
        self.password = password
        self.setup_sftp_connection()
        self.setupModelData()

    def setup_sftp_connection(self):
        # Setup your SFTP connection here
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("tete.bournemouth.ac.uk", port=22, username=self.username, password=self.password)
            self.renderfarm = ssh.open_sftp()
            print("CONNECTED")
        except socket.gaierror as e:
            raise NCCA_RenderfarmConnectionFailed()

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if parent_item:
            child_item = parent_item.child(row)
            if child_item:
                return self.createIndex(row, column, child_item)

        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data()

        return None

    def setupModelData(self, parent):
        self.root_item = SFTPItem(self.root_path, parent, self.renderfarm)

    def fetchMore(self, parent=QModelIndex()):
        self.setupModelData(parent)

    def setupModelData(self):
        self.root_item = SFTPItem(self.root_path, None, self.renderfarm)

class SFTPItem:
    def __init__(self, path, parent=None, sftp=None):
        self.path = path
        self.parent_item = parent
        self.renderfarm = sftp
        self.child_items = []
        self.populate_children()

    def populate_children(self):
        if self.renderfarm is None:
            return

        try:
            files = self.renderfarm.listdir(self.path)
            for file in files:
                full_path = f"{self.path}/{file}"
                if self.renderfarm.isdir(full_path):
                    self.child_items.append(SFTPItem(full_path, self, self.renderfarm))
                else:
                    self.child_items.append(SFTPItemLeaf(full_path, self))
        except FileNotFoundError:
            # Handle non-existent directory
            pass

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)

    def data(self):
        return self.path

class SFTPItemLeaf:
    def __init__(self, path, parent=None):
        self.path = path
        self.parent_item = parent

    def data(self):
        return self.path
