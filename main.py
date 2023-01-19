from tkinter import *
import sqlite3
import ast
import os

# Constants for GUI dimensions. Should rarely be changed.
SCREEN_X = 1280 
SCREEN_Y = 760
WINDOW_TITLE = 'Graphing Utility'
LOGO_PATH = 'GraphingUtility-main/icon.ico'


global root
root = Tk()
root.geometry('{X}x{Y}'.format(X=SCREEN_X, Y=SCREEN_Y)) 
root.resizable(False,False) # Make it unable to resize, important for the code to work as relies on absolute values.
root.title(WINDOW_TITLE)
root.wm_iconbitmap(LOGO_PATH)

canvas = Canvas()   
main_area = canvas.create_rectangle(50,50,700,700,outline="black", fill="white", width=2) # Create area for graph creation.
canvas.pack(fill=BOTH,expand=1)

modes = [
            'Add Nodes',
            'Add Connections',
            'Add Weights',
        ]

# Get X coordinate of mouse cursor
def getX(e):
    return e.x

# Get Y coordinate of mouse cursor
def getY(e):
    return e.y


class Graph():
    def __init__(self, title, type='Normal'):

        # Create title input area above node creation zone.
        self.title_label = Label(root, text="Title: ").place(x=200, y=25) 
        self.title_input = Entry(root, width=40)
        self.title_input.place(x=240, y=25)

        self.title = title
        self.canPlaceNodes = True
        self.type = type
        self.nodes = []
        self.adjacency_matrix = []
        self.adjacency_list = {}
        self.hasConnections = False
        self.directed_checkbox = Button()
        self.confirm_connection = Button()
        self.enter_weight, self.confirm_weight, self.weight_prompt = Entry(), Button(), Label()
        self.connection_head, self.connection_tail = Entry(), Entry()
        self.connection_prompt = Label()
        self.weight_head, self.weight_tail = Entry(), Entry()
        self.to = Label()
        self.weight_labels = []
        self.node_circles, self.node_labels = [], []
        self.display_matrix_button = Button(text='Display Matrix', command=lambda: self.showAdjacencyMatrix(root, self.adjacency_list))
        self.display_matrix_button.place(x=750, y=650)

        self.depth_first_search = Button(root, text='Depth First Search', command=lambda: self.search(graph=self.adjacency_list, search_type='DFS'))
        self.depth_first_search.place(x=750, y=400)
        self.breadth_first_search = Button(root, text='Breadth First Search', command=lambda: self.search(graph=self.adjacency_list, search_type='BFS'))
        self.breadth_first_search.place(x=750, y=450)

        self.title_confirm = Button(root, text="Confirm Title", command=lambda: self.setTitle(self.title_input.get()))
        self.title_confirm.place(x=475, y=21)

        self.rename_node_prompt = Label(root, text="Rename node")
        self.rename_node_prompt.place(x=900, y=550)
        self.node_rename_entry = Entry(root, width=7)
        self.node_rename_entry.place(x=820, y=550)
        self.which_node = Entry(root, width=3, bg='gray')
        self.which_node.place(x=875, y=550)
        self.node_rename_button = Button(root, text='Confirm', command=lambda: self.renameNode(self.which_node.get(), self.node_rename_entry.get()))
        self.node_rename_button.place(x=750, y=550)

        self.source_node = Entry(root, width=3, bg='gray')
        self.source_node.place(x=875,y=600)
        self.source_node_prompt = Label(root, text="Source Node")
        self.source_node_prompt.place(x=900, y=600)
        self.djikstras_button = Button(root, text="Djikstra's Algorithm", command=lambda: self.dijkstra(r=root, adj_list=self.adjacency_list, source=self.source_node.get()))
        self.djikstras_button.place(x=750, y=600)

        self.value_inside = StringVar(root)
        self.value_inside.set("Mode")
        self.mode_menu = OptionMenu(root, self.value_inside, *modes, command=lambda e: self.getOption(e))
        self.mode_menu.place(x=750, y=100)

        self.reset_button = Button(root, text="Reset all", command=lambda: self.reset())
        self.reset_button.place(x=1150, y=600)

        self.save_to_database_button = Button(root, text="Save to database", command=lambda: self.saveToDatabase())
        self.save_to_database_button.place(x=1150, y=650)

        self.imported = False

        # Connect to the database
        conn = sqlite3.connect('graphs.db')

        # Create a cursor
        cursor = conn.cursor()

        # Select all the rows from the table
        cursor.execute('SELECT * FROM graphs')

        # Get the rows from the database
        self.rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Create the dropdown menu
        self.ImportVar = StringVar(root)
        self.dropdown = OptionMenu(root, self.ImportVar, *[row[-1] for row in self.rows])
        self.dropdown.place(x=1150, y=400)

        self.confirm_import = Button(root, text='Confirm Import', command=lambda: self.importGraph(self.ImportVar.get()))
        self.confirm_import.place(x=1150, y=450)

    def importGraph(self, name):

        self.reset()

        self.imported = True

        index = 0
        for row in self.rows:
            if name in row:
                index = self.rows.index(row)

        this_graph = self.rows[index]
        print('RIESNTIRNTIAREIARN', (this_graph[0]), type(this_graph[0]))
        print("THIS GRAPH:", this_graph)
        print("THIS TITLE TITLE", this_graph[-1])
        self.adjacency_list = ast.literal_eval(this_graph[1])

        self.title = this_graph[-1]
        self.nodes = ast.literal_eval(this_graph[2])
        print(self.nodes)

        print('adjacency list = ', self.adjacency_list, type(self.adjacency_list))
        print('title = ', self.title, type(self.title))
        print('nodes = ', self.nodes, type(self.nodes))

        count = len(self.nodes)
        print("count:", count)

        for i in range(count):
            self.addNode(x=self.nodes[i][0], y=self.nodes[i][1])

        self.nodes = self.nodes[:count]

        print(self.nodes)

        for i in range(len(self.nodes)-1):
            print("NODE COUNT:", len(self.nodes))
            print(self.nodes)
            self.renameNode(i+1, self.nodes[i][2]) 

        for k,v in self.adjacency_list.items():
            for node in v:
                self.addConnection(k[0], node[0])

        for k,v in self.adjacency_list.items():
            for node in v:
                if isinstance(node, list) and len(node) == 2:
                    self.addWeight(k[0], node[0], node[1])
                    print(k[0], node[0], node[1])
                    print('weight added')



    def reset(self):

        for label in self.node_labels:
            label.destroy()

        for weight in self.weight_labels:
            weight.destroy()

        # Create title input area above node creation zone.
        self.title_label = Label(root, text="Title: ").place(x=200, y=25) 
        self.title_input = Entry(root, width=40)
        self.title_input.place(x=240, y=25)

        self.canPlaceNodes = True
        self.type = type
        self.nodes = []
        self.adjacency_matrix = []
        self.adjacency_list = {}
        self.hasConnections = False
        self.directed_checkbox = Button()
        self.confirm_connection = Button()
        self.enter_weight, self.confirm_weight, self.weight_prompt = Entry(), Button(), Label()
        self.connection_head, self.connection_tail = Entry(), Entry()
        self.connection_prompt = Label()
        self.weight_head, self.weight_tail = Entry(), Entry()
        self.to = Label()
        self.weight_labels = []
        self.node_circles, self.node_labels = [], []
        self.display_matrix_button = Button(text='Display Matrix', command=lambda: self.showAdjacencyMatrix(root, self.adjacency_list))
        self.display_matrix_button.place(x=750, y=650)

        self.depth_first_search = Button(root, text='Depth First Search', command=lambda: self.search(graph=self.adjacency_list, search_type='DFS'))
        self.depth_first_search.place(x=750, y=400)
        self.breadth_first_search = Button(root, text='Breadth First Search', command=lambda: self.search(graph=self.adjacency_list, search_type='BFS'))
        self.breadth_first_search.place(x=750, y=450)

        self.title_confirm = Button(root, text="Confirm Title", command=lambda: self.setTitle())
        self.title_confirm.place(x=475, y=21)

        self.rename_node_prompt = Label(root, text="Rename node")
        self.rename_node_prompt.place(x=900, y=550)
        self.node_rename_entry = Entry(root, width=7)
        self.node_rename_entry.place(x=820, y=550)
        self.which_node = Entry(root, width=3, bg='gray')
        self.which_node.place(x=875, y=550)
        self.node_rename_button = Button(root, text='Confirm', command=lambda: self.renameNode(self.which_node.get(), self.node_rename_entry.get()))
        self.node_rename_button.place(x=750, y=550)

        self.source_node = Entry(root, width=3, bg='gray')
        self.source_node.place(x=875,y=600)
        self.source_node_prompt = Label(root, text="Source Node")
        self.source_node_prompt.place(x=900, y=600)
        self.djikstras_button = Button(root, text="Djikstra's Algorithm", command=lambda: self.dijkstra(r=root, adj_list=self.adjacency_list, source=self.source_node.get()))
        self.djikstras_button.place(x=750, y=600)

        self.value_inside = StringVar(root)
        self.value_inside.set("Mode")
        self.mode_menu = OptionMenu(root, self.value_inside, *modes, command=lambda e: self.getOption(e))
        self.mode_menu.place(x=750, y=100)

        self.reset_button = Button(root, text="Reset all", command=lambda: self.reset())
        self.reset_button.place(x=1150, y=600)

        self.save_to_database_button = Button(root, text="Save to database", command=lambda: self.saveToDatabase())
        self.save_to_database_button.place(x=1150, y=650)

        self.imported = False

                # Connect to the database
        conn = sqlite3.connect('graphs.db')

        # Create a cursor
        cursor = conn.cursor()

        # Select all the rows from the table
        cursor.execute('SELECT * FROM graphs')

        # Get the rows from the database
        self.rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Create the dropdown menu
        self.ImportVar = StringVar(root)
        self.dropdown = OptionMenu(root, self.ImportVar, *[row[2] for row in self.rows])
        self.dropdown.place(x=1150, y=400)

        self.confirm_import = Button(root, text='Confirm Import', command=lambda: self.importGraph(self.ImportVar.get()))
        self.confirm_import.place(x=1150, y=450)

        canvas.delete(ALL)

        main_area = canvas.create_rectangle(50,50,700,700,outline="black", fill="white", width=2) # Create area for graph creation.

    def saveToDatabase(self):

        conn = sqlite3.connect('graphs.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM graphs")
        result = cursor.fetchone()
        print('RESULTSETNSETNTEN', result)

        cursor.execute('''INSERT INTO users (userId, graphId) VALUES (?, ?)''', (os.getlogin(), str(result[0])))
        cursor.execute('''INSERT INTO graphs (data, position, name, graphId) VALUES (?, ?, ?, ?)''', (str(self.adjacency_list), str(self.nodes), self.getTitle(), str(result[0])))

        

        conn.commit()
        conn.close()

        self.viewDatabase()


    def viewDatabase(self):
        # Connect to the database
        conn = sqlite3.connect('graphs.db')

        # Create a cursor
        cursor = conn.cursor()

        # Select all rows from the "table" table
        cursor.execute('''SELECT * FROM graphs''')

        # Fetch the rows
        rows = cursor.fetchall()

        # Print the rows
        for row in rows:
            print(row)

        # Close the connection
        conn.close()

    def dfs(self, graph, start):
        """Perform depth-first search on a graph, starting at the given node."""
        # Create a stack to store the nodes to visit
        stack = [start]

        # Create a set to store the visited nodes
        visited = set()

        # While there are nodes in the stack:
        while stack:
            # Pop the top node from the stack
            node = stack.pop()

            # If the node has not been visited:
            if node not in visited:
                # Mark the node as visited
                visited.add(node)

                # Add all unvisited neighbors of the node to the stack
                for neighbor in graph[node]:
                    if neighbor[0] not in visited:
                        stack.append(neighbor[0])

        return visited

    def bfs(self, graph, start):
        """Perform breadth-first search on a graph, starting at the given node."""
        # Create a queue to store the nodes to visit
        queue = [start]

        # Create a set to store the visited nodes
        visited = set()

        # While there are nodes in the queue:
        while queue:
            # Pop the first node from the queue
            node = queue.pop(0)

            # If the node has not been visited:
            if node not in visited:
                # Mark the node as visited
                visited.add(node)

                # Add all unvisited neighbors of the node to the queue
                for neighbor in graph[node]:
                    if neighbor[0] not in visited:
                        queue.append(neighbor[0])

        return visited


    def search(self, graph, search_type):
        """Perform the specified search type on the given graph and display the results in a pop-up window."""
        # Get the starting node
        start = list(graph.keys())[0]

        # Perform the specified search type
        if search_type == 'DFS':
            visited = self.dfs(graph, start)
        elif search_type == 'BFS':
            visited = self.bfs(graph, start)

        # Create a pop-up window to display the results
        child = Toplevel(root)
        child.title(f"{search_type} Results")

        Label(child, text=f"Visited nodes: {visited}").pack()

    def setTitle(self, t):
        self.title = t

    def renameNode(self, node, name):
        print(len(self.node_labels), 'NODE LABELS')
        print(int(node)-1, 'NODE-1')
        label = self.node_labels[int(node) - 1]
        label.config(text=("{index}: {name}".format(index=int(node), name=name)))

    def showAdjacencyMatrix(self, parent_window, adjacency_list,):
        # Create a Tkinter window as a child of the parent window
        window = Toplevel(parent_window)
        window.title("Adjacency Matrix")

        # Get the list of nodes from the adjacency list
        nodes = list(adjacency_list.keys())

        # Create the matrix
        matrix = []
        for i in range(len(nodes)):
            matrix.append([])
            for j in range(len(nodes)):
                matrix[i].append(Label(window, text="0", width=10))

        # Populate the matrix with the weights from the adjacency list
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                for neighbor in adjacency_list[nodes[i]]:
                    if neighbor[0] == nodes[j]:
                        if len(neighbor) > 1:
                            matrix[i][j].config(text=neighbor[1])
                        else:
                            matrix[i][j].config(text='inf')

        # Add some space between the second column
        matrix[0][1].config(padx=20)

        # Add the matrix to the window
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                matrix[i][j].grid(row=i+1, column=j+1)

        # Add titles to the rows and columns
        for i, node in enumerate(nodes):
            Label(window, text=node).grid(row=i+1, column=0)
            Label(window, text=node).grid(row=0, column=i+1)

    def dijkstra(self, r, adj_list, source):
        
        can = True

        for key, value in self.adjacency_list.items():
            for connection in value:
                if not isinstance(value, list) or not len(connection) == 2:
                    print("Invald graph to perform Djikstra's")
                    can = False
        
        if can:

            # Create a dictionary to store the distances from the source node to all other nodes.
            # Set the distance for the source node to 0, and the distance for all other nodes to infinity.
            distances = {node: float('inf') if node != source else 0 for node in adj_list.keys()}

            # Create a set to store the unvisited nodes
            unvisited = set(adj_list.keys())

            # Create a dictionary to store the previous node in the shortest path for each node
            previous = {}

            # While there are still unvisited nodes:
            while unvisited:
                # Find the node with the smallest distance in the unvisited set
                current = min(unvisited, key=distances.get)

                # Mark the current node as visited
                unvisited.remove(current)

                # Update the distances to all unvisited neighbors of the current node
                for neighbor, weight in adj_list[current]:
                    if neighbor in unvisited:
                        # Calculate the tentative distance to the neighbor
                        tentative_distance = distances[current] + weight

                        # If the tentative distance is shorter than the current distance, update the distance and set the previous node for the neighbor
                        if tentative_distance < distances[neighbor]:
                            distances[neighbor] = tentative_distance
                            previous[neighbor] = current

            # Create a pop-up window to display the results
            child = Toplevel(r)
            child.title("Dijkstra's Algorithm Results")

            # Create a frame to hold the labels for the shortest paths
            path_frame = Frame(child)
            path_frame.pack()

            # Iterate through the nodes and build the shortest path for each node
            for node in adj_list.keys():
                path = []
                current = node
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(source)
                path.reverse()

                # Create a label for the shortest path for the current node
                Label(path_frame, text=f"Fastest path to node {node}: {' -> '.join(path)}").pack()

            Label(child, text="Shortest distances:").pack()
            Label(child, text=distances).pack()
        else:
            print("Invald graph to perform Djikstra's")

                  
    def getTitle(self):
        return self.title


    def getOption(self, option):
        print("OPTION=", option)
        if option == 'Add Nodes':
            self.connection_head.place_forget()
            self.connection_tail.place_forget()
            self.directed_checkbox.place_forget()
            self.confirm_connection.place_forget()
            self.connection_prompt.place_forget()
            self.weight_prompt.place_forget()
            self.enter_weight.place_forget()
            self.confirm_weight.place_forget()
            self.weight_head.place_forget()
            self.weight_tail.place_forget()
            self.to.place_forget()
            self.startCreatingNodes()
            print(option in modes) # bool
        elif option == 'Add Connections':
            self.weight_prompt.place_forget()
            self.enter_weight.place_forget()
            self.confirm_weight.place_forget()
            self.weight_head.place_forget()
            self.weight_tail.place_forget()
            self.to.place_forget()
            self.finishCreatingNodes()
            self.startConnection()
        elif option == 'Add Weights':
            self.connection_head.place_forget()
            self.connection_tail.place_forget()
            self.directed_checkbox.place_forget()
            self.confirm_connection.place_forget()
            self.connection_prompt.place_forget()
            self.startAddingWeights()

    def startAddingWeights(self):
        self.enter_weight = Entry(root, width=7)
        self.enter_weight.place(x=750, y=150)
        self.weight_prompt = Label(text='Enter Weight')
        self.weight_prompt.place(x=800, y=150)

        self.weight_head = Entry(root, width=3)
        self.weight_head.place(x=750, y=175)
        self.weight_tail = Entry(root, width=3)
        self.weight_tail.place(x=800, y=175)
        self.to = Label(root, text='to')
        self.to.place(x=775, y=175)

        self.confirm_weight = Button(root, text='Confirm Weight', command=lambda: self.addWeight(head=self.weight_head.get(), tail=self.weight_tail.get(), weight=self.enter_weight.get()))
        self.confirm_weight.place(x=750, y=200)

    def getMidpoint(self, x1,y1,x2,y2):
                # calculate the midpoint coordinates
                x_mid = (x1 + x2) / 2
                y_mid = (y1 + y2) / 2

                # return the midpoint as a tuple
                return (x_mid, y_mid)

    def addWeight(self, head, tail, weight):
        head, tail = str(head), str(tail)

        # if it is not directed
        if not self.imported:
            if tail in self.adjacency_list[head] and head in self.adjacency_list[tail]:
                self.adjacency_list[head][self.adjacency_list[head].index(tail)] = [tail, int(weight)]
                self.adjacency_list[tail][self.adjacency_list[tail].index(head)] = [head, int(weight)]


                x1, y1, x2, y2 = self.nodes[int(head)-1][0], self.nodes[int(head)-1][1], self.nodes[int(tail)-1][0], self.nodes[int(tail)-1][1]
                mid = self.getMidpoint(x1,y1,x2,y2)

                weight_label = Label(root, text=weight, font=("Helvetica", 16, "bold"), fg="blue")
                weight_label.place(x=mid[0], y=mid[1])
                self.weight_labels.append(weight_label)

        else:
            x1, y1, x2, y2 = self.nodes[int(head)-1][0], self.nodes[int(head)-1][1], self.nodes[int(tail)-1][0], self.nodes[int(tail)-1][1]
            mid = self.getMidpoint(x1,y1,x2,y2)

            weight_label = Label(root, text=weight, font=("Helvetica", 16, "bold"), fg="blue")
            weight_label.place(x=mid[0], y=mid[1])
            self.weight_labels.append(weight_label)


        print(self.adjacency_list)

    def startConnection(self):
        self.connection_head = Entry(root, width=7)
        self.connection_head.place(x=750, y=150)
        self.connection_tail = Entry(root, width=7)
        self.connection_tail.place(x=750, y=200)
        self.connection_prompt = Label(root, text='Connect ↑ to ↓')
        self.connection_prompt.place(x=750, y=175)
        d = IntVar()
        self.directed_checkbox = Checkbutton(root, text='Directed', variable=d)
        self.directed_checkbox.place(x=750, y=225)
        self.confirm_connection = Button(root, text='Confirm', command=lambda: self.addConnection(self.connection_head.get(), self.connection_tail.get(), directed=d.get()))
        self.confirm_connection.place(x=750, y=250)

    def addConnection(self, start, end, directed=False):

        if not self.imported:
            # adds connections to adjacency list
            if str(start) in self.adjacency_list.keys():
                self.adjacency_list[start].append(end)
            else:
                self.adjacency_list[start] = [end]
            
            if not directed:
                if str(end) in self.adjacency_list.keys():
                    self.adjacency_list[end].append(start)
                else:
                    self.adjacency_list[end] = [start]

            # remove duplicate entries 
            for k,v in self.adjacency_list.items():
                self.adjacency_list[k] = list(set(v))

        print(self.adjacency_list)

        hPointer = int(start) - 1
        tPointer = int(end) - 1
        head = self.nodes[hPointer]
        tail = self.nodes[tPointer]

        if directed:
            canvas.create_line(head[0], head[1], tail[0], tail[1], width=3)
            
            mid_x = self.getMidpoint(head[0], head[1], tail[0], tail[1])[0]
            mid_y = self.getMidpoint(head[0], head[1], tail[0], tail[1])[1]

            canvas.create_line(head[0], head[1], mid_x, mid_y, arrow=LAST, arrowshape=(20, 20, 10))    

        else:
            canvas.create_line(head[0], head[1], tail[0], tail[1], width=3)

        self.hasConnections = True
        canvas.pack()


    def addNode(self, x, y):
        n = 'Node ' + str(len(self.nodes)+1)
        new_node = Node(x,y, name=n)
        new_node_node = new_node.node
        if new_node_node != []:
            self.nodes.append(new_node_node)
            self.node_labels.append(new_node.getLabel())
            self.node_circles.append(new_node.getCircle())
        #print(self.nodes)

    def startCreatingNodes(self):
        root.bind('<Button-1>', lambda e: self.addNode(getX(e), getY(e)))

    def finishCreatingNodes(self):
        root.unbind('<Button-1>')
    
    def delete(self):
        del self




class Node():
    def __init__(self, x, y, name='Node'):
        self.x = x
        self.y = y
        self.name = name        
        self.node = []
        self.circle = ''
        self.label = Label()

        self._radius = 30

        self.createNode(self.name)
    
    def getCircle(self):
        return self.circle

    def getLabel(self):
        return self.label

    def getRadius(self):
        return self._radius

    def createNode(self,name):
        if self.x < 700 and self.x > 50 and self.y < 700 and self.y > 50:
            self.circle = canvas.create_oval(self.x - self.getRadius(), self.y - self.getRadius(), self.x + self.getRadius(), self.y + self.getRadius(), outline='black', fill='yellow', width=2)
            canvas.pack()
            #self.label = canvas.create_text(self.x,self.y,text=name)
            self.label = Label(root, text=name, bg="yellow")
            self.label.place(x=self.x, y=self.y, anchor="center")
            self.node = (self.x, self.y, self.name)
            

canvas.pack()

def main():
    graph1 = Graph(title='Graph 1')

# Connect to the database
conn = sqlite3.connect('graphs.db')

# Create a cursor
cursor = conn.cursor()

# Select all the rows from the table
cursor.execute('SELECT * FROM graphs')

# Print the rows
print(cursor.fetchall())

# Close the connection
conn.close()




create_graph_button = Button(root, text='Create Graph', command=main)
create_graph_button.place(x=750, y=50)

root.mainloop()


