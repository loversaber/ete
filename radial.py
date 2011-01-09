#!/usr/bin/env python

import math
import sys
import random
import colorsys
from PyQt4 import QtCore, QtGui
from ete2 import Tree

def random_color(base=0.25):
    s = 0.5#random.random()
    v = 0.5+random.random()/2
    R, G, B = map(lambda x: int(100*x), colorsys.hsv_to_rgb(base, s, v))
    return "#%s%s%s" %(hex(R)[2:], hex(G)[2:], hex(B)[2:])

class ArcPartition(QtGui.QGraphicsPathItem):
    def depict_partition(self, cxdist, cydist, r1, r2, angle_start, angle_end):
        # Precalculate values
        d1 = r1 * 2
        d2 = r2 * 2
        r1_xstart = -r1 - cxdist
        r1_ystart = -r1 + cydist
        r2_xstart = -r2 - cxdist
        r2_ystart = -r2 + cydist
        angle_span = angle_end + angle_start

        path = QtGui.QPainterPath()
        # Calculate start and end points of inner arc
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, -angle_start)
        i1 = path.currentPosition()
        path.arcMoveTo(r1_xstart, r1_ystart, d1, d1, angle_end)
        i2 = path.currentPosition()
        # Moves to outer arc start position
        path.arcMoveTo(r2_xstart, r2_ystart , d2, d2, -angle_start)
        o1 = path.currentPosition()
        # Draws outer arc
        path.arcTo(r2_xstart, r2_ystart, d2, d2, -angle_start, angle_span)
        o2 = path.currentPosition()
        # Draws line to the end point in inner arc (straight line)
        path.lineTo(i2)
        # Draws inner arc from end point to to start 
        path.arcTo(r1_xstart, r1_ystart, d1, d1, angle_end, -angle_span)
        # Draws line to the start point of outer arc (straight line)
        path.lineTo(o1)
        self.setPath(path)

        color = "#DDE8C4"
        color = random_color()
        self.setPen(QtGui.QPen(QtGui.QColor("green")))
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))

def rotate_and_displace(item, rotation, height, offset):
    """ Rotates and item of a given height over its own axis and moves
    the item offset units in the rotated x axis """
    t = QtGui.QTransform()
    t.rotate(rotation)
    t.translate(0, - (height / 2))
    t.translate(offset, 0)
    item.setTransform(t)

def get_min_radius(w, h, a, xoffset):
    """ returns the radius and X-displacement required to render a
    rectangle (w,h) within and given angle (a)."""

    angle = (a * math.pi)/180 # converts to radians
    # optimal_angle = angle fitting provided offset and item
    # dimensions
    if xoffset:
        optimal_angle = math.atan((h/2) / xoffset) 
    else:
        optimal_angle = 0#(45 * math.pi)/180

    # If available angle is >=180, I don't need to calculate extra
    # offset. Any item will fit
    if a/2>=180: # a/2 ??
        min_offset = xoffset
        print "Oops"
    else:
        min_offset = (h/2) / math.tan(angle / 2)
   
    # Returns the optimal angle and x_offset 
    if optimal_angle < angle and xoffset>min_offset:
        off = xoffset
        r = (w + off) / math.cos(optimal_angle) 
        an = optimal_angle * 2
        print "opp", r, a, off
    elif optimal_angle < angle:
        off = min_offset
        r = (w + off) / math.cos(optimal_angle) 
        an = optimal_angle * 2
        print "special", r, a, off, optimal_angle
    else:
        off = min_offset
        r = (w + off) / math.cos(angle / 2) 
        an = angle
        print "min", r, a, off, optimal_angle
    return r, off, (an*180)/math.pi

def distribute_tree(root_node, parent, scale, arc_span):
    n2i = node2item = {}
    last_rotation = -90 # starts rotation from 12 o'clock
    rot_step = float(arc_span) / len(root_node)
    max_r = 0
    # :::: Precalculate rotations and node regions. Creates QGitems ::::
    for node in root_node.traverse("postorder"): # Children first. This will be blind to draw descendents
        # Creates a semi-ring partition that will contain all node's
        # related QItems
        item = n2i[node] = ArcPartition(parent)
        if _leaf(node):
            item.rotation = last_rotation
            item.full_start = last_rotation - (rot_step / 2)
            item.full_end = last_rotation + (rot_step / 2)
            last_rotation += rot_step
        else:
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            rot_end = last_c.rotation
            rot_start = first_c.rotation
            item.angle_span = (rot_end - rot_start)
            item.rotation = rot_start + ((rot_end - rot_start) / 2)

            item.full_start = first_c.full_start
            item.full_end = last_c.full_end

    # :::: RENDER :::::
    for node in root_node.traverse("preorder"):
        item = n2i[node]

        # Branch length converted to pixels
        node.dist_xoffset = float(node.dist * scale)
        # Creates items (faces, node, etc.)
        if _leaf(node):
            iw = 10#int(random.random()*20)
            ih = 20#int(random.random()*20)
        else:
            iw = 1
            ih = 1
        #iw = int(random.random()*20)
        #ih = int(random.random()*20)

        w = node.dist_xoffset + iw
        h = ih 

        # Node region 
        node.nodeRegion = QtCore.QRectF(0, 0, w, h)
        # This is the node total region covered by the node
        node.fullRegion = QtCore.QRectF(0, 0, w, h)

        if node.up:
            parent_radius = n2i[node.up].radius
        else:
            parent_radius = 0

        if _leaf(node):
            angle = rot_step
        else:
            angle = item.angle_span

        r, xoffset, best_a = get_min_radius(w, h, angle, parent_radius)
        rotate_and_displace(item, item.rotation, h, parent_radius)
        item.radius = r

        if r > max_r:
            max_r = r

        if not _leaf(node):
            first_c = n2i[node.children[0]]
            last_c = n2i[node.children[-1]]
            # BG
            full_angle = last_c.full_end - first_c.full_start
            angle_start = last_c.full_end - item.rotation
            angle_end = item.rotation - first_c.full_start
            item.depict_partition(parent_radius, h/2, parent_radius, r, angle_start, angle_end)
            # Vertical arc Line
            rot_end = n2i[node.children[-1]].rotation
            rot_start = n2i[node.children[0]].rotation
            C = QtGui.QGraphicsPathItem(parent)
            path = QtGui.QPainterPath()
            path.arcMoveTo(-r,-r, r * 2, r * 2, 360-rot_start-angle)
            path.arcTo(-r,-r, r*2, r * 2, 360 - rot_start - angle, angle)
            # Faces
            C.setPath(path)
            faces = new_node(w-node.dist_xoffset, h, item, "red", "" )
        else:
            faces = new_node(w-node.dist_xoffset, h, item, "blue", "" )
        faces.moveBy(xoffset - parent_radius+node.dist_xoffset, 0)

        # horizontal line
        branch = QtGui.QGraphicsLineItem(0, h/2, node.dist_xoffset, h/2)
        branch.setParentItem(item)
        if parent_radius < xoffset:
            branch_guide = QtGui.QGraphicsLineItem(node.dist_xoffset, h/2, xoffset-parent_radius+node.dist_xoffset, h/2)
            branch_guide.setPen(QtGui.QPen(QtGui.QColor("orange")))
            branch_guide.setParentItem(item)        
        #rrr = QtGui.QGraphicsRectItem(item.boundingRect())
        #rrr.setParentItem(item)
    return max_r


def _leaf(node):
    return node.is_leaf()

# TEST AND TRASH

def new_node(w, h, parent, color="red", label=1):
    rect = QtGui.QGraphicsRectItem(0, 0, w, h)
    rect.setParentItem(parent)
    rect.setPen(QtGui.QPen(QtGui.QColor(color)))
    #e = QtGui.QGraphicsEllipseItem()
    #e.setParentItem(rect)
    #e.setRect(0,0, w, h)
    t = QtGui.QGraphicsSimpleTextItem(str(label))
    t.moveBy(5,0)
    t.setParentItem(rect)
    return rect

def rotate_and_translate(item, rotation, a, length):
    radian = (a * math.pi)/180
    height = item.rect().height()
    min_length = (height/2) / math.tan(radian/2)
    if min_length > length:
        length = min_length

    t = QtGui.QTransform()
    t.rotate(rotation)
    t.translate(0, -(item.rect().height()/2))        
    item.setTransform(t)
    t.translate(length, 0)
    item.setTransform(t)
    return length

def distribute(n, parent):
    # Distribute n items along a circumference 
    angle_start = 0
    angle_end = 360.0
    current_rotation = angle_start
    angle_step = angle_end/n
    offset = 0
    while current_rotation < angle_end:
        w = int(random.random()*100)
        h = int(random.random()*100)
        item = new_node(w, h, parent, "red")
        r, min_offset = get_min_radius(w, h, angle_step, offset)
        rotate(item, current_rotation, min_offset)
        current_rotation += angle_step

if __name__ == '__main__':
    n = float(sys.argv[1])
    try:
        scale = float(sys.argv[2])
    except Exception:
        print "Default scale"
        scale = 40
    try:
        arc_span = float(sys.argv[3])
    except Exception:
        print "Default scale"
        arc_span = 360

    t = Tree()
    node = t
    #for i in xrange(n):
    #    node.add_child(Tree())
    #    x = Tree()
    #    node.add_child(x)
    #    node = x
    t.populate(n, names_library="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", reuse_names=False)
    # Random node distances 
    for n in t.traverse():
        n.dist = 1#random.random()
    print t.get_ascii(show_internal=True)
        
    # Basic QtApplication
    app = QtGui.QApplication(sys.argv)
    scene = QtGui.QGraphicsScene()

    parent = QtGui.QGraphicsRectItem(0, 0, 0, 0)
    #distribute(n, parent)
    r = distribute_tree(t, parent, scale, arc_span) + 50
    scene.setSceneRect(-r, -r, r*2, r*2)
    scene.addItem(parent)
    view = QtGui.QGraphicsView(scene)
    view.setRenderHints(QtGui.QPainter.Antialiasing or QtGui.QPainter.SmoothPixmapTransform )
    view.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)

    view.show()
    sys.exit(app.exec_())
