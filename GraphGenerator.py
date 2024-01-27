# Imports
from collections import defaultdict
from functools import partial
import random
from pyvis.network import Network
import tkinter as Tk
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import webbrowser
import os

# Global Variables
n = 30
k = int(n * 1.5)
d = 4
edges = {}
types = {}
node_map = defaultdict(dict)
node_coords = {}

directions = [[1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1]]

color_map = {0: 'gold', 1: 'purple', 2: 'green', 3: 'red', 4: 'blue', 5: 'orange', 6: 'gray', 7: 'black'}
label_map = {0: 'START', 1: 'END', 2: 'GOOD', 3: 'BAD', 4: 'SHOP', 5: 'TP', 6: 'VS', 7: ''}
space_map = {v: k for k, v in label_map.items()}
count_map = {'GOOD': 3, 'BAD': 3, 'SHOP': 4, 'TP': 3, 'VS': 3}

def generate_graph():
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
    global edges
    global types
    global node_map
    global node_coords
    e = 0
    edges = {}
    node_map = defaultdict(dict)
    node_map[0][0] = 0
    node_coords = {0: [0, 0]}
    
    for i in range(n):
        edges[i] = []
        if (i != 0):
            v = random.randrange(0, i)
            c = node_coords[v]
            dir = random.choice(directions)
            while (c[0]+dir[0]) in node_map and (c[1]+dir[1]) in node_map[c[0]+dir[0]]:
                v = random.randrange(0, i)
                c = node_coords[v]
                dir = random.choice(directions)
            edges[i].append(v)
            edges[v].append(i)
            node_map[c[0]+dir[0]][c[1]+dir[1]] = i
            node_coords[i] = [c[0]+dir[0], c[1]+dir[1]]
            e += 1
            
    while e < k:
        u = random.randrange(0, n)
        c = node_coords[u]
        dir = random.choice(directions)
        while len(edges[u]) >= d or (c[0]+dir[0]) not in node_map or (c[1]+dir[1]) not in node_map[c[0]+dir[0]] or len(edges[node_map[c[0]+dir[0]][c[1]+dir[1]]]) >= d or node_map[c[0]+dir[0]][c[1]+dir[1]] in edges[u]:
            u = random.randrange(0, n)
            c = node_coords[u]
            dir = random.choice(directions)
        edges[u].append(node_map[c[0]+dir[0]][c[1]+dir[1]])
        edges[node_map[c[0]+dir[0]][c[1]+dir[1]]].append(u)
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
    types[0] = 0
    # Now set random end node as a random dead end node
    types[min(edges, key=lambda x: len(edges[x]))] = 1
    # Want 3 good & bad, 4 shops, 1 vs, 3 teleports
    for type in count_map:
        setRandNodes(space_map[type], count_map[type])
        
    for i in range(n):
        if i not in types:
            types[i] = space_map['']
    
def visualize_pyviz():
    # Use pyviz to visualize it
    net = Network()

    # Add nodes
    for node in edges:
        net.add_node(node, label=label_map[types[node]], color=color_map[types[node]], shape='box')

    # Add edges
    for node in edges:
        for edge in edges[node]:
            net.add_edge(node, edge)

    # html = net.generate_html('graph.html')
    net.save_graph('graph.html')
    # print(os.path)
    # print(os.getcwd())
    url = 'file://' + os.getcwd() + '/graph.html'
    webbrowser.open(url, new=2)
    
    # return net

def visualize_nx():
    graph = nx.Graph()
    node_colors = []
    node_labels = {}
    for node in edges:
        graph.add_node(node)
        if node in types:
            node_colors.append(color_map[types[node]])
            node_labels[node] = label_map[types[node]]
        else:
            node_colors.append(color_map[7])
            node_labels[node] = label_map[7]
    for node in edges:
        for dest in edges[node]:
            graph.add_edge(node, dest)
    return graph, node_colors, node_labels

def draw_graph_window(a):
    graph, node_colors, node_labels = visualize_nx()
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, node_color=node_colors, labels=node_labels, with_labels=True, node_size=1500, node_shape='h', ax=a)
    # font_size
    # https://matplotlib.org/3.1.1/api/markers_api.html#module-matplotlib.markers
    # bbox=dict(facecolor='none', edgecolor='blue', pad=10.0))
    # https://www.geeksforgeeks.org/python-visualize-graphs-generated-in-networkx-using-matplotlib/

def draw_grid_graph(a):
    graph, node_colors, node_labels = visualize_nx()
    pos = nx.spring_layout(graph)
    for p in node_coords:
        pos[p] = node_coords[p]
    nx.draw(graph, pos, node_color=node_colors, labels=node_labels, with_labels=True, node_size=1500, node_shape='8', ax=a)

    
def new_graph(a, canvas):
    generate_graph()
    a.cla()
    draw_graph_window(a)
    canvas.draw()
    
def new_grid_graph(a, canvas):
    generate_grid_graph()
    a.cla()
    draw_grid_graph(a)
    canvas.draw()

root = Tk.Tk()
root.wm_title = 'Blind Board Game Map Generator'

controls = Tk.Frame(root)
controls.pack(side=Tk.TOP)

f = Figure(figsize=(5, 4), dpi=100)
a = f.add_subplot(111)
nx.draw(nx.complete_graph(0), ax=a)

canvas = FigureCanvasTkAgg(f, master=root)
new_graph_btn = Tk.Button(master=root, command=partial(new_graph, a, canvas), text='New Board')
new_graph_btn.pack(in_=controls, side=Tk.LEFT)

new_grid_graph_btn = Tk.Button(master=root, command=partial(new_grid_graph, a, canvas), text='New Grid Board')
new_grid_graph_btn.pack(in_=controls, side=Tk.LEFT)

save_html_btn = Tk.Button(master=root, command=visualize_pyviz, text='Open HTML Version')
save_html_btn.pack(in_=controls, side=Tk.LEFT)

canvas.draw()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

root.mainloop()

# Visualize the graph
# net.save_graph('graph.html')



# https://www.tutorialspoint.com/how-do-i-create-a-popup-window-in-tkinter
# https://www.geeksforgeeks.org/how-to-create-a-pop-up-message-when-a-button-is-pressed-in-python-tkinter/
# https://docs.python.org/3/library/tkinter.html
# https://stackoverflow.com/questions/37084313/how-to-display-rendered-html-content-in-text-widget-of-tkinter-in-python-3-4-x

# %%