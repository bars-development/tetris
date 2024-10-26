from Polyomino import Polyomino, extractClasses, RotationClass, CompleteClass, PolyominoClass
import numpy as np
# import matplotlib.pyplot as plt
import sys
# import pygame
import random
# from PIL import Image



def generateColors(n:int):
    colors = []
    for _ in range(n):
        # Generate random values for Red, Green, and Blue components
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
        # Append the color as a tuple to the list
        colors.append([red, green, blue])

    return colors

class Game:
    def __init__(self, n:int, m:int):
        self.height = n
        self.width = m
        self.data = np.zeros((n, m))
        self.prev_poly = Polyomino([[1]])
        self.prev_move = Position(self.data, self.prev_poly, 0, 0)
        self.special = set()
        self.c = 0
    def clear(self):
        self.data=np.zeros_like(self.data)
        self.c = 0
    def set_allowed(self, allowed, group_by:str="n"):
        #Set polyominos that could be used
        self.allowed = allowed
        self.group_by=group_by
        classes =  extractClasses(allowed)
        if(group_by=="r"):
            self.classe = classes[0]
        elif(group_by=="c"):
            self.classe = classes[2]
        else:
            self.classe = [PolyominoClass(p) for p in allowed]
            for i in range(len(self.classe)):
                self.classe[i].polyominos = [allowed[i]]
                self.classe[i].getDims()
        self.colors = generateColors(len(self.classe))
    def set_ai_params(self, h:int=20, blank_spaces:int=100, blank_line:int=100, line_cleared:int=30, uniformity:int=20):
        self.ai_params = {
            "h": h,
            "blank_spaces":blank_spaces,
            "blank_line":blank_line,
            "line_cleared":line_cleared,
            "uniformity":uniformity
        }
    def _identify(self, p:Polyomino):
        #give an id to a polyomino based on group_by
        if p not in self.allowed:
            return 0
        if(self.group_by=='n'):
            for i in range(len(self.allowed)):
                if(self.allowed[i]==p):
                    return i+1
        for index, c in enumerate(self.classe):
            if(p in c.polyominos):
                return index+1
        return 1
    def possibilities(self, p:Polyomino):
        pos = [p]
        if(self.group_by=='r'):
            pos = RotationClass(p).polyominos
        if(self.group_by=='c'):
            pos = CompleteClass(p).polyominos
        res = []
        for poly in pos:
            for i in range(self.width-poly.width+1):
                if(poly not in self.allowed):
                    continue
                move = Position(self.data, poly, i, self._identify(poly))
                if(move.possible):
                    res.append(move)
        return res
    def predict_move(self, p:Polyomino):
        moves = self.possibilities(p)
        if(len(moves)==0):
            return False
        scores = list()
        mn = 0
        for i, move in enumerate(moves):
            assert(move is not None)
            scores.append(move.evaluateMove(self.ai_params))
        for i in range(len(scores)):
            if(scores[i]<scores[mn]):
                mn = i
        if(len(moves)<mn+1):
            print(len(scores), len(moves), mn)
        self.prev_poly = Polyomino(p.data)
        self.prev_move = Position(self.data, self.prev_poly, 0, 0)
       
        self.data = moves[mn].data
        self.special = moves[mn].special
        self.c+=moves[mn].c
        return True
    def play_game(self):
        while(True):
            p = self.allowed[random.randint(0, len(self.allowed)-1)]
            if not self.predict_move(p):
                break
        return self.c
    def _getColor(self, v):
        if(v==0):
            return [255, 255, 255]
        if(v>len(self.classe)):
            raise RuntimeError("not correct value")
        return self.colors[int(v)-1]
    def draw(self, width):
        drawable = np.zeros((self.height*width, self.width*width, 3), dtype=np.uint8)
        for i in range(self.height):
            for j in range(self.width):
                
                color  =self._getColor(self.data[i, j])
                drawable[i*width:i*width+width, j*width: j*width+width] = color
                size = (width-2)//2
                if((i, j) in [tuple(x) for x in self.special]):

                    drawable[i*width+size:i*width+width-size, j*width+size: j*width+width-size] = [0,0,0]
        #gridlines,
        drawable[width::width, :] = [0,0,0]
        drawable[:,width::width] = [0,0,0]

        return drawable
    def __repr__(self):
        return str(self.data)

class Position:
    def __init__(self, data, piece, offset, polyId):
        self.data = data+0
        self.height, self.width = data.shape
        self.piece = piece
        self.offset = offset
        self.k = polyId
        self.c = 0 
        self.possible = False
        self.special = set()
        self._drop(self.piece, offset)
    def _drop(self, p:Polyomino, position:int=0):
        if(position+p.width>self.width):
            return 
        for j in range(self.height-p.height+1):
            tmp = np.zeros_like(p.data) 
            if(j!=0):
                tmp = self.data[j-1: j+p.height-1, position: position+p.width]/1
                self.data[j-1: j+p.height-1, position: position+p.width][p.data>0] = 0   
            chunk = self.data[j: j+p.height, position: position+p.width]>0

            if(np.sum(p.data[chunk])>0):
                if(j==0):
                    return
                self.data[j-1: j+p.height-1, position: position+p.width] = tmp
                break
            self.polyPosition = (j, position)
            self.data[j: j+p.height, position: position+p.width] += p.data*self.k     
        self.possible = True
    def evaluateMove(self, ai_params):
        #coefficient
        self._refresh()
        s = 0
        mins = list()
        ##punish for height
        for i in range(len(self.data)):
            if(np.sum(self.data[i])>0):
                s+= (len(self.data)-i) * np.sum(self.data[i]>0)*ai_params["h"]
        #punish for closed holes
        for i in range(self.width):
            column = self.data[:, i]
            m = self.height
            for j in range(self.height):
                if(column[j]>0):
                    m = j
                    break
            mins.append(m)
            s+=(np.sum(column==0)-m) * ai_params["blank_spaces"]
        #punish for more than 3 height blank column 
        mins = [0]+mins+[0]
        for i in range(1, len(mins)-1):
            f = min(max(mins[i]-mins[i-1]-2, 0), max(mins[i]-mins[i+1]-2, 0))
            s+=f*ai_params["blank_line"]
        #punish for not uniformity
        s+=(max(mins)-min(mins))*ai_params["uniformity"]
        return s-self.c*ai_params["line_cleared"]
    def draw(self, width, color=[0, 255, 0]):
        print(self.special)
        drawable = np.zeros((self.height*width, self.width*width, 3), dtype=np.uint8)
        for i in range(self.height):
            for j in range(self.width):
                
                if(self.data[i, j]==0):
                        drawable[i*width:i*width+width, j*width: j*width+width] =255
                        continue
                if((i, j) in [tuple(x) for x in self.special]):
                    drawable[i*width:i*width+width, j*width: j*width+width] = [255,0,0]
                    continue 
                # color  =self.getColor(self.data[i, j])
                # for k in range(3):
                    
                drawable[i*width:i*width+width, j*width: j*width+width] = color  
        for i in range(self.height):
            if((self.data[i]==0).sum()==0):
                drawable[i*width:i*width+width, :] = [0,0,255]
        # print(drawable//1)
        drawable[width::width, :] = [0,0,0]
        drawable[:,width::width] = [0,0,0]

        # img = Image.fromarray(drawable)

        return drawable
    def _refresh(self):
        i = self.height-1
        while(i>0):
            if((self.data[i]==0).sum()==0):
                # print(i)
                self.c+=1
                self.data[1:i+1] = self.data[:i]
                self.data[0] = np.zeros(self.width)
                for j in range(len(self.special)):
                    if(self.special[j][0]==i):
                        self.special[j][0] = np.inf
                    if(self.special[j][0]<i):
                        self.special[j][0]+=1
                i+=1
            i-=1


class Grid:
    def __init__(self, width=0, height=0, data=None):
        if(data is None):
            self.data = np.zeros((height, width))
            self.width = width
            self.height = height
        else:
            self.data = data
            self.height, self.width = data.shape
    
    def possibilities(self, poly, polyId):
        res = list()
        for i in range(self.width-poly.width+1):
            move = Position(self.data, poly, i, polyId)
            if(move.possible):
                res.append(move)
        return res
    
    def fill(self, allowed_shapes, index=1):
        if(np.sum(self.data==np.zeros_like(self.data))==0):
            self.colors = list(np.random.random_integers(10, 255, (3)))
            return [self]
        res = list()
        for i in range(len(allowed_shapes)):
            for pos in self.possibilities(allowed_shapes[i], index):
                if(no_gap(pos)):
                    res.append(pos)
        # for r in res:
                    g = Grid(data = pos.data)
                    f = g.fill(allowed_shapes, index=index+1)
                    if(not isinstance(f, bool)):
                        self.colors = f[-1].colors
                        self.colors.append(np.random.random_integers(10, 255, (3)))
                        return f + [g]
        return False
    def _getColor(self, v):
        if(v==0):
            return [255, 255, 255]
        return self.colors[int(v)-1]
    def draw(self, width):
        # c = int(np.max(self.data))
        # self.colors = generateColors(c)
        drawable = np.zeros((self.height*width, self.width*width, 3), dtype=np.uint8)
        for i in range(self.height):
            for j in range(self.width):
                
                color  =self._getColor(self.data[i, j])
                drawable[i*width:i*width+width, j*width: j*width+width] = color
                # size = (width-2)//2
                # if((i, j) in [tuple(x) for x in self.special]):

                    # drawable[i*width+size:i*width+width-size, j*width+size: j*width+width-size] = [0,0,0]
        #gridlines,
        drawable[width::width, :] = [0,0,0]
        drawable[:,width::width] = [0,0,0]

        return drawable   
            
def no_gap(position):
    for i in range(position.width):
        column = position.data[:, i]
        m = position.height
        for j in range(position.height):
            if(column[j]>0):
                m = j
                break
        if((np.sum(column==0)-m)>0):
            return False
    return True      
            