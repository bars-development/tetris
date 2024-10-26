from Polyomino import *
from Game import  Game, Position
from random import randint

# %gui qt
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer
import numpy as np
# import time

class TetrisUI(QWidget):
    def __init__(self, game:Game):
        super().__init__()
        self.g  = game
        self.current_random_number = randint(0, len(self.g.allowed)-1)
        self.current_piece = self.g.allowed[self.current_random_number]
        self.current_index=0
        self.prev = False
        self.animation_running = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('Tetris')
        self.score = QLabel(self)

        self.moveScore = QLabel(self)
        self.image_label = QLabel(self)
        self.piece_label = QLabel(self)
        # self.load_next_image()
        # self.load_next_image()
        self.display_image(self.g.draw(20), self.current_piece.draw(20, self.g._getColor(self.g._identify(self.current_piece))))
        self.current_index=0

        self.next_button = QPushButton('Next Move', self)
        self.prev_button = QPushButton('Toggle Previous Move', self)
        self.pos_button = QPushButton('Posibilities', self)
        self.start_button = QPushButton('Start Animation', self)
        self.stop_button = QPushButton('Stop Animation', self)
        self.reset = QPushButton('Reset', self)

        self.start_button.clicked.connect(self.start_animation)
        self.stop_button.clicked.connect(self.stop_animation)
        self.next_button.clicked.connect(self.load_next_image)
        self.prev_button.clicked.connect(self.load_prev_state)
        self.pos_button.clicked.connect(self.load_next_pos)
        self.reset.clicked.connect(self.reset_pos)
        
        layout = QVBoxLayout()
        layout.addWidget(self.moveScore)
        layout.addWidget(self.score)
        layout.addWidget(self.piece_label)

        layout.addWidget(self.image_label)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.pos_button)
        layout.addWidget(self.reset)


        self.setLayout(layout)
    def reset_pos(self):
        self.g.clear()
        self.load_next_image()
    def generate_image(self, random_number):
        
        self.current_random_number = randint(0, len(self.g.allowed)-1)
        if not self.g.predict_move(self.current_piece):
            self.stop_animation()
        self.current_piece = self.g.allowed[random_number]
        self.score.setText(f"{self.g.c} Lines cleared")
        s = 0
        for i in range(self.g.width):
            column = self.g.data[:, i]
            m = self.g.height
            for j in range(self.g.height):
                if(column[j]>0):
                    m = j
                    break
            s+=(np.sum(column==0)-m)
        return self.g.draw(20), self.current_piece.draw(20, self.g._getColor(self.g._identify(self.current_piece)))
    def play_animation(self):
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(10) 
    def start_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.animation_timer.start(10) 

    def stop_animation(self):
        if self.animation_running:
            self.animation_running = False
            self.animation_timer.stop()

    def update_animation(self):
        self.load_next_image()


    def load_next_image(self):

        self.moveScore.setText(f"Badness Score: {Position(self.g.data, Polyomino([[1]]), 0, 0).evaluateMove(self.g.ai_params):.4f}");
        image, poly = self.generate_image(self.current_random_number)
        self.display_image(image, poly)
        self.current_index=0

    def load_next_pos(self):
        pos = self.g.possibilities(self.current_piece)
        self.display_image(pos[self.current_index].draw(20), pos[self.current_index].piece.draw(20, [255,0,255], offset=pos[self.current_index].offset))
        self.moveScore.setText(f"Badness Score: {pos[self.current_index].evaluateMove(self.g.ai_params):.4f}");

        self.current_index+=1
        if(self.current_index==len(pos)):
            self.current_index=0
    def load_prev_state(self):
        self.prev = not self.prev
        if(not self.prev):
            board, poly = self.g.draw(20), self.current_piece.draw(20, self.g._getColor(self.g._identify(self.current_piece)))
            self.display_image(board, poly)
            return
        pos = self.g.prev_move
        self.display_image(pos.draw(20), pos.piece.draw(20, [255,0,255], offset=pos.offset))
        self.moveScore.setText(f"Badness Score: {pos.evaluateMove(self.g.ai_params)}");
        
        
    def display_image(self, image, poly):
        height, width = image.shape[:2]  # Extract height and width
        q_image = QImage(image.data, width, height, image.strides[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        self.image_label.setPixmap(pixmap)
        height, width = poly.shape[:2]  # Extract height and width
        q_image = QImage(poly.data, width, height, poly.strides[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.piece_label.setPixmap(pixmap)


