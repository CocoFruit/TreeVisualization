import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QSlider, QLineEdit, QFrame
from PyQt5.QtGui import QPainter, QColor, QBrush, QPixmap, QFont, QPen, QPainterPath,QFontDatabase
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QSize
from PyQt5 import QtTest

import random
import qdarktheme
import numpy as np
import math

def update_tree(node,treeWidget,timer):
    treeWidget.update()
    QCoreApplication.processEvents()
    QtTest.QTest.qWait(timer)

GLOBAL_ROOT = None


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1
        self.highlighted = False

    def update_height(self):
        l = self.left.height if self.left else 0
        r = self.right.height if self.right else 0
        self.height = 1 + max(l, r)

    def get_height(self):
        return self.height
    

    def balance_factor(self):
        l = self.left.height if self.left else 0
        r = self.right.height if self.right else 0
        return l - r

    def rotate_right(self,treeWidget=None,timer=1000):
        new_root = self.left
        self.left = new_root.right
        new_root.right = self
        self.update_height()
        new_root.update_height()
        # if treeWidget:
            # update_tree(self, treeWidget, timer)
            # update_tree(new_root, treeWidget, timer)
        return new_root

    def rotate_left(self,treeWidget=None,timer=1000):
        new_root = self.right
        self.right = new_root.left
        new_root.left = self
        self.update_height()
        new_root.update_height()
        # if treeWidget:
        #     update_tree(self, treeWidget, timer)
        #     update_tree(new_root, treeWidget, timer)
        return new_root

    def rebalance(self,treeWidget=None,timer=1000):
        balance = self.balance_factor()
        if balance > 1:
            if self.left.balance_factor() < 0:
                self.left = self.left.rotate_left(treeWidget=treeWidget,timer=timer)
            return self.rotate_right()
        if balance < -1:
            if self.right.balance_factor() > 0:
                self.right = self.right.rotate_right(treeWidget=treeWidget,timer=timer)
            return self.rotate_left()
        return self

    def insert(self, value,treeWidget=None,root=None,timer=1000):
        self.highlighted = True
        if treeWidget:
            update_tree(self, treeWidget, timer)
            
        if value < self.value:
            if self.left is None:
                self.highlighted = False
                self.left = TreeNode(value)
                self.left.highlighted = True
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                self.left.highlighted = False
            else:
                self.highlighted = False
                self.left = self.left.insert(value,treeWidget,root,timer)
                self.left.highlighted = False
                
        elif value > self.value:
            if self.right is None:
                self.highlighted = False
                self.right = TreeNode(value)
                self.right.highlighted = True
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                self.right.highlighted = False
            else:
                self.highlighted = False
                self.right = self.right.insert(value,treeWidget,root,timer)
                self.right.highlighted = False
        else:
            self.highlighted = False
            return self

        self.update_height()
        self.highlighted = False

        rebalanced = self.rebalance(treeWidget,timer)
        # set tree
        treeWidget.set_tree(rebalanced)
        root = rebalanced
        if treeWidget:
            update_tree(root, treeWidget, 0)

        return rebalanced
    
    def find(self, value):
        if value == self.value:
            return self
        if value < self.value and self.left:
            return self.left.find(value)
        if value > self.value and self.right:
            return self.right.find(value)
        return None
    
    def delete(self, value,treeWidget=None,timer=1000):
        self.highlighted = True
        if treeWidget:
            update_tree(self, treeWidget, timer)

        if value < self.value:
            if self.left:
                self.highlighted = False
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                self.left = self.left.delete(value,treeWidget,timer)
        elif value > self.value:
            if self.right:
                self.highlighted = False
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                self.right = self.right.delete(value,treeWidget,timer)
        else:
            if self.left is None:
                self.highlighted = False
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                return self.right
            if self.right is None:
                self.highlighted = False
                if treeWidget:
                    update_tree(self, treeWidget, timer)
                return self.left
            min_node = self.right.find_min()
            self.value = min_node.value
            self.right = self.right.delete(min_node.value,treeWidget,timer)

        self.update_height()
        self.highlighted = False
        rebalanced = self.rebalance(treeWidget,timer)
        root = rebalanced
        if treeWidget:
            update_tree(root, treeWidget, 0)
        return rebalanced

    def inorder_traversal(self):
        result = []
        if self.left:
            result += self.left.inorder_traversal()
        result.append(self.value)
        if self.right:
            result += self.right.inorder_traversal()
        return result
    
    def get_width_of_subtree(self):
        # use bfs to get the width of the tree
        q = [(self, 0)]
        width = 0
        while q:
            node, index = q.pop(0)
            if node is None:
                continue
            width = max(width, index)
            q.append((node.left, index*2))
            q.append((node.right, index*2 + 1))
        return width
   

def pretty_print_tree(root, prefix="", is_left=True):
    if root is not None:
        pretty_print_tree(root.right, prefix + ("│   " if is_left else "    "), False)
        print(prefix + ("└── " if is_left else "┌── ") + str(root.value))
        pretty_print_tree(root.left, prefix + ("    " if is_left else "│   "), True)


def LCA(node, v1, v2):
    """
    precondition is that v1 and v2 exist in the tree
    """
    if node is None:
        return None

    if node.value > v1 and node.value > v2:
        return LCA(node.left, v1, v2)
    elif node.value < v1 and node.value < v2:
        return LCA(node.right, v1, v2)
    else:
        return node




class TreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.node_outline_color = QColor(0,0,255)
        self.node_color = QColor(51,255,255,210)
        self.transparent_color = QColor(0,0,0,0)
        self.highlighted_color = QColor(255,255,51)
        self.outline_width = 3
        self.highlighted_width = 3

        self.root = None

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle("Binary Tree")

    def set_tree(self, root):
        self.root = root
        self.update()

    def draw_node(self, painter, node, x, y, width, height):
        if node is None:
            return
        
        painter.setPen(QPen(self.node_outline_color, 3, Qt.SolidLine))  
        painter.setBrush(QBrush(self.node_color, Qt.SolidPattern))

        painter.drawEllipse(x, y, width, height)
        painter.setPen(QPen(self.node_outline_color, 1, Qt.SolidLine))
        painter.setFont(QFont('Arial', 12))

        # Calculate the center of the circle
        center_x = x + width // 2
        center_y = y + height // 2

        # Calculate the position to center the text
        text_width = painter.fontMetrics().width(str(node.value))
        text_height = painter.fontMetrics().height()
        text_x = center_x - text_width // 2
        text_y = center_y + text_height // 2 - 5 # 5 is a magic number to center the text

        painter.drawText(text_x, text_y, str(node.value))

    def draw_highlighted_node(self, painter, node, x, y, width, height):
        if node is None:
            return
        painter.setPen(QPen(self.highlighted_color, self.highlighted_width, Qt.SolidLine))  

        painter.setBrush(QBrush(self.node_color, Qt.SolidPattern))

        painter.drawEllipse(x, y, width, height)
        painter.setPen(QPen(self.node_outline_color, 1, Qt.SolidLine))
        painter.setFont(QFont('Arial', 12))

        # Calculate the center of the circle
        center_x = x + width // 2
        center_y = y + height // 2

        # Calculate the position to center the text
        text_width = painter.fontMetrics().width(str(node.value))
        text_height = painter.fontMetrics().height()
        text_x = center_x - text_width // 2
        text_y = center_y + text_height // 2 - 5

        painter.drawText(text_x, text_y, str(node.value))
        

    def draw_edge(self, painter, x1, y1, x2, y2,r):
        c = 3
        if x1 > x2:
            c *= -1

        # find bottom of the first node
        x1 = x1 + r//2 + c
        y1 = y1 + r + self.outline_width

        # find top of the second node
        x2 = x2 + r//2
        y2 = y2 - self.outline_width

        painter.setPen(QPen(self.node_outline_color, self.outline_width, Qt.SolidLine))
        painter.setBrush(QBrush(self.transparent_color, Qt.SolidPattern))
        painter.setRenderHint(QPainter.Antialiasing)

        constant1 = 20
        constant2 = -20
        first_point = (x1, y1)
        first_control_point = (x1,y1+constant1)
        second_control_point = (x2,y2+constant2)
        second_point = (x2, y2)

        path = QPainterPath()
        path.moveTo(*first_point)
        path.cubicTo(*first_control_point, *second_control_point, *second_point)

        painter.drawPath(path)

    def draw_tree(self, painter, node, x, y, width, height):
        if node is None:
            return

        # Draw the current node
        if node.highlighted == False:
            self.draw_node(painter, node, x, y, width, height)
        else:
            self.draw_highlighted_node(painter, node, x, y, width, height)
        # Calculate the width of the subtree rooted at the current node
        
        # subtree_width = width * (node.get_height() -1)*2

        r = 0
        l = 0
        if node.left:
            l = node.left.get_width_of_subtree()
        if node.right:
            r = node.right.get_width_of_subtree()

        subtree_width = width * (l + r + 1)

        c = 3

        # Calculate the x coordinate of the left child
        left_child_x = x - subtree_width//2 - c

        # Calculate the x coordinate of the right child
        right_child_x = x + subtree_width//2 + c

        # Calculate the y coordinate of the children
        child_y = y + 100

        # Draw the left child
        self.draw_tree(painter, node.left, left_child_x, child_y, width, height)

        # Draw the right child
        self.draw_tree(painter, node.right, right_child_x, child_y, width, height)

        # Draw the edge between the current node and the left child
        if node.left:
            self.draw_edge(painter, x, y, left_child_x, child_y, width)

        # Draw the edge between the current node and the right child
        if node.right:
            self.draw_edge(painter, x, y, right_child_x, child_y, width)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.root is not None:
            self.draw_tree(painter, self.root, self.width() // 2, 50, 50, 50)
            
        painter.end()
        
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = 200
        self.timer_max = 1000
        self.timer_min = 0
        self.button_size = (300,75)
        self.font_size = 20
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Binary Tree GUI")
        self.setGeometry(100, 100, 800, 600)

        add_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Node")
        self.add_button.clicked.connect(self.add_node)
        self.add_button.setFixedSize(*self.button_size)
        self.add_button.setFont(QFont('Arial', self.font_size))

        self.add_text = QLineEdit()
        self.add_text.setFixedSize(*self.button_size)
        self.add_text.setFont(QFont('Arial', self.font_size))

        add_layout.addWidget(self.add_button)
        add_layout.addWidget(self.add_text)

        # Remove button

        remove_layout = QHBoxLayout()

        self.remove_button = QPushButton("Remove Node")
        self.remove_button.clicked.connect(self.remove_node)
        self.remove_button.setFixedSize(*self.button_size)
        self.remove_button.setFont(QFont('Arial', self.font_size))

        self.remove_text = QLineEdit()
        self.remove_text.setFixedSize(*self.button_size)
        self.remove_text.setFont(QFont('Arial', self.font_size))

        remove_layout.addWidget(self.remove_button)
        remove_layout.addWidget(self.remove_text)


        # Timer label
        self.timer_label = QLabel("Speed")
        self.timer_label.setFixedSize(*self.button_size)
        self.timer_label.setFont(QFont('Arial', self.font_size))
        self.timer_label.setAlignment(Qt.AlignCenter)

        # Timer slider
        self.timer_input = QSlider(Qt.Horizontal)
        self.timer_input.setMinimum(self.timer_min)
        self.timer_input.setMaximum(self.timer_max)
        self.timer_input.setValue(self.timer_max - self.timer)
        self.timer_input.setTickInterval(100)
        self.timer_input.setTickPosition(QSlider.TicksBelow)
        self.timer_input.valueChanged.connect(self.update_timer)
        self.timer_input.setFixedSize(*self.button_size)
        self.timer_input.setFont(QFont('Arial', self.font_size))

        # Horizontal layout for timer label and slider
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(self.timer_label)
        timer_layout.addWidget(self.timer_input)

        # Vertical layout for buttons and timer
        vBox = QVBoxLayout()
        vBox.addLayout(timer_layout)
        vBox.addLayout(add_layout)
        vBox.addLayout(remove_layout)


        # make the vbox stretch
        vBox.addStretch(1)

        hBox = QHBoxLayout()

        self.treeWidget = TreeWidget()
        hBox.addWidget(self.treeWidget)
        hBox.addLayout(vBox)
        self.setLayout(hBox)

        self.showMaximized()

        self.root = TreeNode(100)
        self.treeWidget.set_tree(self.root)

    def update_timer(self):
        self.timer = self.timer_max - int(self.timer_input.value())


    def add_node(self):
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        try:
            value = int(self.add_text.text())
        except:
            value = ""
        if value == "":
            self.enable_buttons()
            return

        self.root = self.root.insert(value, self.treeWidget, self.root, self.timer)

        QTimer.singleShot(200, self.enable_buttons)

    def enable_buttons(self):
        self.add_button.setEnabled(True)
        self.remove_button.setEnabled(True)

    def remove_node(self):
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        try:
            value = int(self.remove_text.text())
        except:
            value = ""
        if value == "":
            self.enable_buttons()
            return
        
        self.root = self.root.delete(value, self.treeWidget, self.timer)
        QTimer.singleShot(250, self.enable_buttons)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()