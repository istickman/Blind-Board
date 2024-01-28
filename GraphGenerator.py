# Imports
from collections import defaultdict
import random
import networkx as nx
import tkinter as Tk
import customtkinter
import webbrowser
import os
from functools import partial
from pyvis.network import Network

# global variables
n = 30 # number of node in graph
k = int(n * 1.5) # total number of edges in graph
d = 4 # max edges node can have
edges = {} # mapping of node to list of edges
types = {} # mapping of node id to node type
node_map = defaultdict(dict) # double mapping of x,y to node id
node_coords = {} # mapping from node id to coordinates

directions = [[1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1]] # the 8 directions nodes can randomly connect to/from

color_map = {0: 'gold', 1: 'purple', 2: 'green', 3: 'red', 4: 'blue', 5: 'orange', 6: 'gray', 7: 'black'} # map from type id to color string
label_map = {0: 'START', 1: 'END', 2: 'GOOD', 3: 'BAD', 4: 'SHOP', 5: 'TP', 6: 'VS', 7: ''} # map from type id to label string
space_map = {v: k for k, v in label_map.items()} # reverse of label map for easy defining of type ids based on type
count_map = {'GOOD': 3, 'BAD': 3, 'SHOP': 4, 'TP': 3, 'VS': 3} # mapping of count of each type of specialty node

# the various options for each type of wheel
good_wheel = ['+3 gold', 'Battle another player', '+2 gold', 'Spin bad wheel', 'Double gold', '+5 gold', 'Gain compass', 'Send player to shadow realm']
bad_wheel = ['Spin the good wheel', 'Go to shadow realm', 'Teleport', 'Swap places', 'Give away all gold', 'Change board', 'Return home', 'Give away 3 gold', 'Give away an item', 'Spin x2']
vs_wheel = ['Number off', 'Another player decides', 'Joke battle', 'Losing player wins', 'Fact battle', 'Improv']

size = 10 # size of node in canvas object
color_index = 0 # index representing next color to pick from when making a player object
player_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'] # the different colors player circles can be generated as
players = [] # list of player object ids for easy removal
player_texts = [] # list of player text frame ids for easy removal

class playerCircle:
    # this is the class the lets me spawn and move circles on top of the graph/board

    def __init__(self, canvas, text):
        global color_index
        self.canvas = canvas
        self.window = canvas.master
        # spawn the circle for the new player
        self.circle = canvas.create_oval(20, 20, 20+size/2, 20+size/2, fill=player_colors[color_index], outline='white', width=2)
        # keep track of its id
        players.append(self.circle)
        # bind movement functions
        self.window.bind("<ButtonPress-1>", self.start_move)
        self.window.bind("<B1-Motion>", self.move)
        # create a frame to store color identifier box and text box for the new player
        self.textElems = Tk.Frame(text)
        self.textElems.pack(in_=text, side=Tk.LEFT, padx=5)
        self.textSquare = Tk.Text(height=1, width=1, bg=player_colors[color_index], state='disabled')
        self.textSquare.pack(in_=self.textElems, side=Tk.LEFT)
        self.text = Tk.Text(height=1, width=15, font='Helvetica 15')
        self.text.pack(in_=self.textElems, side=Tk.LEFT, anchor='center')
        # store the frame id as we can delete the frame all at once to be simple
        player_texts.append(self.textElems)
        # move the color forward by 1
        color_index = (color_index + 1) % len(player_colors)

    def start_move(self, event):
        # move function when dragging using the mouse
        self._x = event.x
        self._y = event.y

    def move(self, event):
        # secondary component to move function when dragging using the mouse
        deltax = event.x - self._x
        deltay = event.y - self._y
        self._x = event.x
        self._y = event.y
        self.canvas.move("current", deltax, deltay)

def generate_graph():
    # this function is no longer used, for comments look at the below function, the only significant difference is how nodes are generated next to each other instead of randomly like this one
    global edges
    global types
    # Generate the graph
    e = 0
    edges = {}

    for i in range(n):
        edges[i] = []
        if (i != 0):
            v = random.randrange(0, i)
            edges[i].append(v)
            edges[v].append(i)
            e += 1
            
    while e < k:
        u = random.randrange(0, n)
        v = random.randrange(0, n)
        while u == v or v in edges[u] or len(edges[u]) >= d or len(edges[v]) >= d:
            u = random.randrange(0, n)
            v = random.randrange(0, n)
        edges[u].append(v)
        edges[v].append(u)
        e += 1

    # Create speciality nodes
    types = {}
    def setRandNodes(type, amt):
        t = 0
        while (t < amt):
            r = random.randrange(0, n)
            while (r in types):
                r = random.randrange(0, n)
            types[r] = type
            t += 1
    # Make the most connected node the start/gold node
    types[max(edges, key=lambda x: len(edges[x]))] = 0
    # Now set random end node as a random dead end node
    types[min(edges, key=lambda x: len(edges[x]))] = 1
    # Want 3 good & bad, 4 shops, 1 vs, 3 teleports

    for type in count_map:
        setRandNodes(space_map[type], count_map[type])
        
    for i in range(n):
        if i not in types:
            types[i] = space_map['']

def generate_grid_graph():
    # function to generate the graph
    global edges
    global types
    global node_map
    global node_coords
    e = 0 # number of edges in the graph
    edges = {}
    node_map = defaultdict(dict)
    node_map[0][0] = 0 # set origin as the start node
    node_coords = {0: [0, 0]}
    
    # spawn n nodes in the graph, randomly connecting it to an already spawned node to ensure connectivity
    for i in range(n):
        edges[i] = []
        if (i != 0):
            v = random.randrange(0, i)
            c = node_coords[v]
            dir = random.choice(directions)
            while (c[0]+dir[0]) in node_map and (c[1]+dir[1]) in node_map[c[0]+dir[0]]:
                # keep randomizing until a direction with a node is spawned
                v = random.randrange(0, i)
                c = node_coords[v]
                dir = random.choice(directions)
            edges[i].append(v)
            edges[v].append(i)
            node_map[c[0]+dir[0]][c[1]+dir[1]] = i
            node_coords[i] = [c[0]+dir[0], c[1]+dir[1]]
            e += 1
            
    # randomly generate the rest of the edges until we have k
    while e < k:
        u = random.randrange(0, n)
        c = node_coords[u]
        dir = random.choice(directions)
        while len(edges[u]) >= d or (c[0]+dir[0]) not in node_map or (c[1]+dir[1]) not in node_map[c[0]+dir[0]] or len(edges[node_map[c[0]+dir[0]][c[1]+dir[1]]]) >= d or node_map[c[0]+dir[0]][c[1]+dir[1]] in edges[u]:
            # keep randomizing until we have a new edge
            u = random.randrange(0, n)
            c = node_coords[u]
            dir = random.choice(directions)
        edges[u].append(node_map[c[0]+dir[0]][c[1]+dir[1]])
        edges[node_map[c[0]+dir[0]][c[1]+dir[1]]].append(u)
        e += 1

    # create speciality nodes
    types = {}
    def setRandNodes(type, amt):
        # simple function to randomly set amt nodes in the graph to be type
        t = 0
        while (t < amt):
            r = random.randrange(0, n)
            while (r in types):
                r = random.randrange(0, n)
            types[r] = type
            t += 1
    # mark the start/gold node
    types[0] = 0
    # now set random end node as a random dead end node
    # note: this could end up being a node that has 2 edges, but even then, that will be the node with the least connections
    types[min(edges, key=lambda x: len(edges[x]))] = 1
    for type in count_map:
        setRandNodes(space_map[type], count_map[type])
    # set the remaining nodes as blank nodes
    for i in range(n):
        if i not in types:
            types[i] = space_map['']
    
def visualize_pyviz():
    # use pyviz to visualize the graph
    net = Network()

    # add nodes
    for node in edges:
        net.add_node(node, label=label_map[types[node]], color=color_map[types[node]], shape='box')

    # add edges
    for node in edges:
        for edge in edges[node]:
            net.add_edge(node, edge)

    # save the html into the same directory as this is running
    net.save_graph('graph.html')
    # compute url and open link to show graph in browser
    url = 'file://' + os.getcwd() + '/graph.html'
    webbrowser.open(url, new=2)

def update_window(canvas, text):
    # this is the command function for the 'new graph' button, which generates and draws the graph onto the window canvas
    global edges
    global types
    global node_coords
    global size
    # generate a new graph
    generate_grid_graph()
    # delete all old objects from the screen (the old graph nodes and players)
    canvas.delete('all')
    # delete player circles and text boxes
    while len(players) > 0:
        delete_player(canvas, text)
    # calculate the best ratio in which the graph can fit and still look like circle nodes
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    # have to add 1 to each side to give room for nodes to full fit on screen (otherwise half the top nodes would be cut off)
    minx = node_coords[min(node_coords, key=lambda x: node_coords[x][0])][0]-1
    miny = node_coords[min(node_coords, key=lambda x: node_coords[x][1])][1]-1
    maxx = node_coords[max(node_coords, key=lambda x: node_coords[x][0])][0]+1
    maxy = node_coords[max(node_coords, key=lambda x: node_coords[x][1])][1]+1
    numx = maxx - minx
    numy = maxy - miny
    
    hscale = height / numy
    wscale = width / numx
    # scale size of node to be based on dimensions of canvas
    size = min(hscale, wscale) / 2
    node_dist = size * 2
    # draw edges first so they are underneath the nodes
    for node in edges:
        # draw edges first
        for v in edges[node]:
            c1 = node_coords[node]
            c1 = [c1[0]*node_dist, c1[1]*node_dist]
            c2 = node_coords[v]
            c2 = [c2[0]*node_dist, c2[1]*node_dist]
            canvas.create_line(c1[0], c1[1], c2[0], c2[1])
    # draw all nodes on top of the edge map
    for node in edges:
        c = node_coords[node]
        # offset coordinates by node dist so it is spaced properly
        c = [c[0]*node_dist, c[1]*node_dist]
        canvas.create_oval(c[0]-size/2, c[1]-size/2, c[0]+size/2, c[1]+size/2, fill=color_map[types[node]])
        canvas.create_text(c[0], c[1], text=label_map[types[node]], fill='white', font=('Helvetica 12 bold'))
    # offset all objects in canvas to be centered on screen
    for x in canvas.find_all():
        canvas.move(x, width/2-node_dist*(numx/2+minx), height/2-node_dist*(numy/2+miny))

def spin_wheel(wheel):
    # get random choice from wheel array passed in
    outcome = random.choice(wheel)
    # make popup window
    popup = Tk.Toplevel()
    # set focus to the new window
    popup.focus_set()
    popup.geometry('250x50')
    popup.title('Wheel Result')
    Tk.Label(popup, text=outcome, font='Helvetica 20').pack(side=Tk.TOP)
    def destroy(pop, event):
        pop.destroy()
    # after clicking away / losing focus, destroy the window
    popup.bind("<FocusOut>", partial(destroy, popup))
    
def add_player(canvas, text):
    # spawn new player circle
    playerCircle(canvas, text)
    
def delete_player(canvas, text):
    # delete player circle and text box group
    if len(players) > 0:
        canvas.delete(players.pop(0))
    if len(player_texts) > 0:
        player_texts.pop(0).destroy()
    
def scalen(v):
    # temporary function that allows control of node count in graph when generating
    global n
    global k
    n = int(v)
    k = n*1.5

# make root of tkinter window
root = Tk.Tk()
root.title('Blind Board Game Map Generator')
root.minsize(width=root.winfo_screenwidth()-200, height=root.winfo_screenheight()-200)

# sub-frame to store all the controls at the top of the window
controls = Tk.Frame(root)
controls.pack(side=Tk.TOP)

# canvas area to draw and display the graph and player circles
graph = Tk.Canvas(bg='light gray')
graph.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# sub-frame to store the player text boxes at the bottom of the screen
text_boxes = Tk.Frame(root)
text_boxes.pack(side=Tk.BOTTOM, padx=20)

# button to generate/display a new graph
new_graph_btn = Tk.Button(master=root, command=partial(update_window, graph, text_boxes), text='New Board')
new_graph_btn.pack(in_=controls, side=Tk.LEFT)

# temporarly scale to control the amount of nodes in the graph
nnodes_slider = Tk.Scale(master=root, command=scalen, from_=sum(count_map.values())+2, to=50, orient=Tk.HORIZONTAL)
nnodes_slider.pack(in_=controls, side=Tk.LEFT)

# button to take the currently generated graph, generate it in pyvis, and display it in the browser using html
save_html_btn = Tk.Button(master=root, command=visualize_pyviz, text='Open HTML Version')
save_html_btn.pack(in_=controls, side=Tk.LEFT)

# a simple spacer to give a break between control groups
spacer = Tk.Frame(root)
spacer.pack(in_=controls, side=Tk.LEFT, padx=35)

# a sub-frame within controls to store all of the wheel-related buttons
wheels = Tk.Frame(root)
wheels.pack(in_=controls, side=Tk.LEFT)

# a second spacer to give another break before player spawn controls
spacer2 = Tk.Frame(root)
spacer2.pack(in_=controls, side=Tk.LEFT, padx=35)

# buttons for each of the different wheels
good_wheel_btn = Tk.Button(master=root, command=partial(spin_wheel, good_wheel), text='Good Wheel')
good_wheel_btn.pack(in_=wheels, side=Tk.LEFT)
bad_wheel_btn = Tk.Button(master=root, command=partial(spin_wheel, bad_wheel), text='Bad Wheel')
bad_wheel_btn.pack(in_=wheels, side=Tk.LEFT)
vs_wheel_btn = Tk.Button(master=root, command=partial(spin_wheel, vs_wheel), text='VS Wheel')
vs_wheel_btn.pack(in_=wheels, side=Tk.LEFT)

# buttons for spawning or deleting player circles on the map
add_player_btn = Tk.Button(master=root, command=partial(add_player, graph, text_boxes), text='Add Player')
add_player_btn.pack(in_=controls, side=Tk.LEFT)
delete_player_btn = Tk.Button(master=root, command=partial(delete_player, graph, text_boxes), text='Delete Player')
delete_player_btn.pack(in_=controls, side=Tk.LEFT)

# start the window
root.mainloop()