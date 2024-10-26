import numpy as np
import matplotlib.pyplot as plt
import pygame

class Polyomino:
    """Un Polyomino est une figure plane composée de carrés unitaires ayant au moins un côté commun"""
    def __init__(self, data:list)->None:
        self.data = np.array(data)
        self.id = np.max(self.data)
        assert(self.id!=0)
        self.data=self.data/self.id
        self.shape = self.data.shape
        self.height, self.width = self.shape
    def rotate(self):
        """Returns the Polyomino rotated 90 degrees"""
        new = self.data.T[:, ::-1]
        #new = np.rotate90(self.data, k=1)
        return Polyomino(new)
    
    def reflectH(self):
        """Returns the Polyomino reflected horizontally"""
        return Polyomino(self.data[:, ::-1])

    def reflectV(self):
        """Returns the Polyomino reflected vertically"""
        return Polyomino(self.data[::-1, :])
    def multiply(self, k):
        # self.data = self.data/np.max(self.data)
        self.data = self.data*k
    def drawPygame(self, window, coord: tuple, width:int=10, color:tuple=(0, 0, 255))->None:
        for i in range(self.height):
            for j in range(self.width):
                if(self.data[i, j] == 1):
                    pygame.draw.rect(window, color, (coord[0]+j*width, coord[1]+i*width, width, width))
    def draw(self, width, color, offset:int=0):
        drawable = np.zeros((np.sum(self.data!=0)*width, 10*width, 3), dtype=np.uint8)+255
        for i in range(self.height):
            for j in range(self.width):
                if(self.data[i, j]==0):
                        # drawable[i*width:i*width+width, (j+offset)*width: (j+offset)*width+width] =255
                        continue
                # color  =self.getColor(self.data[i, j])
                # for k in range(3):
                    
                drawable[i*width:i*width+width, (j+offset)*width: (j+offset)*width+width] = color    
        return drawable
    def __hash__(self):
        """Simple hashing method for a Polyomino"""
        return int(sum(self.data[i, j] * (i*100+j*10) for i in range(self.shape[0]) for j in range(self.shape[1]) ))
    
    def __eq__(self, other):
        """== Operator for 2 Polyominos"""
        if(self.shape!=other.shape): return False
        return (self.data==other.data).sum() == self.data.size
        
    def __repr__(self):
        """The text representation of the Polyomino to be displayed in console"""
        return str(self)
    def __str__(self):
        s = "\n"
        for line in self.data:
            for i in line:
                if(i==1):
                    s+="■ "
                else:
                    s+="  "
            s+="\n"
        return s

class PolyominoClass:
    """Abstraction class for a polyomino class"""
    def __init__(self, P:Polyomino)->None:
        self.initial = P
        self.polyominos = self.getMembers()
        self.getDims();
    def getDims(self):
        if(len(self.polyominos)==-0):
            self.maxh=5
            self.maxw=5
            return
        self.maxw = max([p.width for p in self.polyominos])
        self.maxh = max([p.height for p in self.polyominos])
    def getMembers(self)->list():
        return list()
    def draw(self, screen, coord:tuple, width:int=10, vertical:bool=True):
        w, h = pygame.display.get_surface().get_size()
        curj, curi = coord
        for poly in self.polyominos:
            poly.drawPygame(screen, (curj, curi), width)
            if(vertical):
                curi+=self.maxh*width+width
                if(curi+self.maxh*width+width>h):
                    curi = coord[1]
                    curj += self.maxw*width+width
        
            else:
                curj+=self.maxw*width+width
                if(curj+self.maxw*width+width>w):
                    curj = coord[0]
                    curi += self.maxh*width+width
        
class RotationClass(PolyominoClass):
    """La classe de rotation d’un polyomino P est l’ensemble des polyominos que l’on obtient par rotations successives de 90 degrés de P ."""
    def __init__(self, P:Polyomino)->None:
        PolyominoClass.__init__(self, P)
    def getMembers(self)->set: 
        p = self.initial
        res = list()
        for i in range(4):
            if(p not in res):
                res.append(p)
            p = p.rotate()
           
        return res
    
    def __repr__(self):
        return "La classe de rotation de \n"+str(self.initial)

class SymmetryClass(PolyominoClass):
    """La classe de symétrie est l’ensemble des polyominos que l’on obtient par symétries successives de P"""
    def __init__(self, P:Polyomino)->None:
        PolyominoClass.__init__(self, P)
    def getMembers(self)->None: 
        p = self.initial
        res = set()
        for _ in range(2):
            p = p.reflectH()
            res.add(p)
            p = p.reflectV()
            res.add(p)
        return list(res)
    def __repr__(self):
        return "La classe de symétrie de \n"+str(self.initial)

class CompleteClass(PolyominoClass):
    """La classe complète est l’ensemble des polyominos obtenus par rotations ou symétries successive de P"""
    def __init__(self, P:Polyomino)->None:
        PolyominoClass.__init__(self,P)
    def getMembers(self)->set: 
        p = self.initial
        res = set()
        for rot_poly in RotationClass(p).polyominos[:2]:
            for poly in SymmetryClass(rot_poly).polyominos:
                res.add(poly)
        return list(res)
    def __repr__(self):
        return "La classe complète de \n"+str(self.initial)


def neighboringOne(data, i:int, j:int):
    if(i!=0):
        if(data[i-1, j]==1): return True
    if(j!=0):
        if(data[i, j-1]==1): return True
    if(i!=data.shape[0]-1):
        if(data[i+1, j]==1): return True
    if(j!=data.shape[1]-1):
        if(data[i, j+1]==1): return True
    return False

def surround(n):
    z = np.zeros((n.shape[0]+2, n.shape[1]+2))
    z[1:-1, 1:-1] = n
    return z

def deleteNotUsed(p):
    if(p[0,:].sum()==0):
        p = p[1:,:]
    if(p[:, 0].sum()==0):
        p = p[:,1:]
    if(p[-1,:].sum()==0):
        p = p[:-1,:]
    if(p[:, -1].sum()==0):
        p = p[:,:-1]
    return p
    
def constructPolyominos(n:int=4):
    if(n==1):
        return [Polyomino([[1]]),]

    res = set()
    for pos in constructPolyominos(n-1):
        p = surround(pos.data)
        for i in range(len(p)):
            for j in range(p.shape[1]):
                if (p[i, j] ==0 and neighboringOne(p, i, j)):
                    p[i, j] = 1 
                    res.add(Polyomino(deleteNotUsed(p)))
                    p[i, j] = 0
    return list(res)

def extractClasses(data)->tuple:
    rot = np.ones(len(data))
    sym = np.ones(len(data))
    com = np.ones(len(data))
    r = list() #rotations
    s = list() #symmetries
    c = list() #completes
    for i in range(len(data)):
        d = data[i]
        if(rot[i]==1):
            r.append(RotationClass(d))
            seen = r[-1].polyominos
            for j in range(i, len(data)):
                if(data[j] in seen):
                    rot[j]=0
        if(sym[i]==1):
            s.append(SymmetryClass(d))
            seen = s[-1].polyominos
            for j in range(i, len(data)):
                if(data[j] in seen):
                    sym[j]=0
        if(com[i]==1):
            c.append(CompleteClass(d))
            seen = c[-1].polyominos
            for j in range(i, len(data)):
                if(data[j] in seen):
                    com[j]=0
    return r, s, c
            

#old code
def show_grid(data: set, cols = 3):
    data = list(data)
    img_count = 0
    rows = len(data)//cols+1
    print(rows, cols)
    # return 
    fig, axes = plt.subplots(nrows=rows, ncols=cols)
    for i in range(rows):
        for j in range(cols):        
            if img_count < len(data):
                if(rows==1):
                    axes[j].imshow(data[img_count].data, cmap="Blues", vmin=0, vmax=1)
                    img_count+=1
                else:
                    axes[i, j].imshow(data[img_count].data, cmap="Blues", vmin=0, vmax=1)
                    img_count+=1


def fillProblem(n:int):
    assert(n>0)
    if(n==1):
        return 1
    if(n==2):
        return 2
    return fillProblem(n-1)+fillProblem(n-2)
