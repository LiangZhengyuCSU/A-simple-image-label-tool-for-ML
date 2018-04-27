import tkinter as tk
import imagelabeler
import numpy as np 
import threading
from queue import Queue
## import an open source selctive search package avaliable on https://github.com/AlpacaDB/selectivesearch ##
import selectivesearch 
## ------------ one can also use "pip install selectivesearch" to install this package ------------------ ##

class selective_search_window(tk.Toplevel):


    def __init__(self, parent):
        '''
        Constructed function, initiate  arguments and UI.
        '''
        super().__init__()
        self.title('Selective search')
        self.geometry('380x80')
        self.resizable(False,False)
        self.parent = parent # the parent window
        # convey parameters from parent window
        self.scale = parent.scale
        self.sigma = parent.sigma
        self.min_size = parent.min_size
        self.minmum_elongation = parent.minmum_elongation
        self.maximum_box_size = parent.maximum_box_size
        self.minimum_box_size = parent.minimum_box_size
        # config parameters
        self.search_performing = False
        # Frame
        frame = tk.Frame(self)
        frame.pack(fill="x")
        # generate the status label
        self.status_label=tk.Label(frame,text='This process will take you several minutes...',
        width=10,height=2,font=('Times New Roman',11))
        self.status_label.pack(fill='x')
        self.run_button = tk.Button(frame, text="Run", command=self.run_searchthread,
        relief='raised',font=('Times New Roman',12),width=10,height=1)
        self.run_button.pack(padx=0)
        # prevent user from quiting the window after the algorithm is performed
        self.protocol('WM_DELETE_WINDOW', self.closeWindow)

    def run_searchthread(self):
        self.search_performing = True # if the search is being performed
        self.status_label.config(text = 'Performing the selective search algorithm',fg='red')
        self.run_button.config(state='disabled')
        data_queue = Queue() #getting data from the selective search thread
        source_img = self.parent.source_img
        scale = self.scale
        sigma = self.sigma
        min_size = self.min_size
        maximum_box_size = self.maximum_box_size
        minimum_box_size = self.minimum_box_size
        minmum_elongation = self.minmum_elongation
        # launch the selective search Thread
        Process_thread = threading.Thread(target=self.run_selective_search,args=(data_queue,
        source_img,scale,sigma,min_size,maximum_box_size,minimum_box_size,minmum_elongation))
        Process_thread.setDaemon(True) # guard the thread and kill it if the window is destroied
        Process_thread.start() #start the thread
        while data_queue.empty():
            self.update()
 
        self.parent.boundingbox_tank = data_queue.get()
        self.search_performing = False
        self.destroy()

        


        
    def run_selective_search(self,data_queue,source_img,scale,sigma,min_size,maximum_box_size,
    minimum_box_size,minmum_elongation):
        '''run the selective search'''
        boundingbox_tank = [] # tank that contains the boundingbox
        # run the procedure
        img = np.asanyarray(source_img) # transfer the PIL image in the parent window to array
        # perform the selective search
        _, bounding_Boxes = selectivesearch.selective_search(img,
        scale=scale, sigma=sigma, min_size=min_size)
        # exclude unwanted boxes
        candidates = set()
        for r in bounding_Boxes:
            # excluding same rectangle (with different segments)
            if r['rect'] in candidates:
                continue
            # excluding regions that are too small or too large
            if r['size'] > maximum_box_size:
                continue
            if r['size'] < minimum_box_size:
                continue
            # excluding too elongated boxes
            _, _, w, h = r['rect']
            if w*h == 0:
                continue
            if w / h < minmum_elongation or h / w < minmum_elongation:
                continue
            candidates.add(r['rect'])
            # convey to the main window
        for x, y, w, h in candidates:
            boundingbox_tank.append([x,y,x+w,y+h])
        
        data_queue.put(boundingbox_tank)


            

    def change_text(self,text,fg = 'black'):
        '''change the text of the warning label'''
        self.status_label.config(text=text,fg=fg)
        self.status_label.text = text
        self.status_label.fg = fg

    def closeWindow(self):
        if self.search_performing:
            self.status_label.config(text = 'Cannot exit when performing the selective search',fg='red')
            return
        else:
            self.destroy()
