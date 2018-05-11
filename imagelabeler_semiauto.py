# -*- coding:utf-8 -*-  
#----------------------------------------------------------------------------------#  
# Name:       A simple image labeling tool-method_semiauto                         #
# Coder:      Zhengyu Liang at Central South Univ.                                 #
# Date:       May, 11, 2018                                                        #
# Git:        https://github.com/LiangZhengyuCSU/A-simple-image-label-tool-for-ML  #    
#----------------------------------------------------------------------------------# 

### ---------------- Import pkgs ---------------- ###
import os
import re
import tkinter as tk
import numpy as np 
from PIL import Image,ImageTk
import tkinter.filedialog as tkfd
import tkinter.messagebox as messagebox
from queue import Queue
from tkinter.filedialog import askdirectory
import glob
### ---------------- Import pkgs ---------------- ###

class imagelabeler_semiauto(object):

    def __init__(self):
        '''
        Constructed function, initiate  arguments.
        '''
        # source image arguments
        self.source_img = None
        self.source_img_size = None
        self.source_img_show = None
        self.show_img_size = [800,600]
        self.boundingbox_tank = []
        self.BBrect_id_tank = []
        self.BBmarker_id_tank = []
        self.source_img_path = 'None'
        self.Current_boundingbox = [None,None,None,None] # recording the BBdata
        self.Current_BBrectangle = None # recording the canvas rectangle of currentBB

        # config arguments
        self.src_imported = False
        self.wait = False # busy flag
        self.work_dir = None
        self.Mouse_status = {'IsClicked': False,'X': None,'Y': None}
        # other arguments
        pass # 2018年5月11日20:02:31
        # launch the UI
        self.init_UI()
    
    
    
    def init_UI(self):
        '''
        Initiate the UI.
        '''
        # the window
        self.window = tk.Tk()
        self.window.title('Labeler')
        self.window.resizable(False,False)
        # The filename reminder
        self.img_name_label = tk.Label(self.window,text=self.source_img_path)
        self.img_name_label.grid(row = 0, column = 0, sticky = 'w')
        # The import button
        self.Import_button = tk.Button(self.window,command=self.import_image,text='Import source image'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised')
        self.Import_button.grid(row = 0, column = 1)
        # The img canvas  
        self.img_canvas = tk.Canvas(self.window, cursor='circle',width=800,height=600,bg='black')  
        self.img_canvas.bind("<Button-1>", self.Click_mouse_incanvas)  
        self.img_canvas.bind("<Motion>", self.MouseMove)  
        self.img_canvas.grid(row = 1, column = 0, rowspan = 8, sticky = 'nw')
        # The mouse position reminder
        self.mouse_position_label = tk.Label(self.window,text='Cursor position\nX:null,Y:null')
        self.mouse_position_label.grid(row = 9, column = 1)

        # frame that contains both the list box and the scrollbar
        self.listbox_frame=tk.LabelFrame(self.window,text='Bounding boxes',font=('Times New Roman',12))
        self.listbox_frame.grid(row=1,column=1, rowspan = 5)
        # the scrollbar attach to the bb browser
        self.list_scrollbar = tk.Scrollbar(self.listbox_frame) 
        self.list_scrollbar.pack(side='right', fill='y')
        self.boundingbox_browser = tk.Listbox(self.listbox_frame,listvariable=None
            ,yscrollcommand=self.list_scrollbar.set, height = 24)
        self.boundingbox_browser.pack(side='left', fill='y')
        self.list_scrollbar.config(command=self.boundingbox_browser.yview)

    # arguments functions
    def init_img(self):
        '''
        initiate all image arguments
        '''
        # source image arguments
        self.source_img = None
        self.source_img_show = None
        self.source_img_size = None
        self.show_img_size = [800,600]
        self.boundingbox_tank = []
        self.BBrect_id_tank = []
        self.BBmarker_id_tank = []
        self.source_img_path = 'None'
        self.Current_boundingbox = [None,None,None,None] # recording the BBdata
        self.Current_BBrectangle = None # recording the canvas rectangle of currentBB
        # config arguments
        self.src_imported = False
        self.wait = False # busy flag
        self.work_dir = None
        self.Mouse_status = {'IsClicked': False,'X': None,'Y': None}

    ### functions for menus ###
    def import_image(self):
        '''
        Import imgfile as the source img.
        '''
        if self.wait:
            return        
        answer = 'yes'
        if len(self.boundingbox_tank)>0:
            answer=messagebox.askquestion(title='Attention please',
            message='Importing a new source image will delete all unsaved images\n, are you still want to import another image?')
        if  answer == 'yes':
            filetypes =[("jpg", '*.jpg',),  
                    ("PNG", '*.png',),  
                    ("tif", '*.tif',)]  
            filename = tkfd.askopenfilename(filetypes=filetypes)
            if filename == '':
                return
            self.init_img() 
            self.source_img = Image.open(filename)
            self.source_img_size = [self.source_img.width,self.source_img.height]
            self.source_img_show = self.source_img.resize((self.show_img_size[0],
                self.show_img_size[1]))
            self.src_imported = True
            self.Show_source_img()
            self.img_name_label.config(text=filename)
        elif answer == 'no':
            return

    # event function
    def Click_mouse_incanvas(self, event):
        '''
        launch when mouse clicked in canvas
        '''
        # multipliers tha helps convert boundingbox box to the source img size

        if not self.src_imported:
            messagebox.showwarning(title='warning',message='Please import the source image first')
            return
        xmultiplier = self.source_img_size[0]/self.show_img_size[0]
        ymultiplier = self.source_img_size[1]/self.show_img_size[1]  
        if not self.Mouse_status['IsClicked']:  
            self.Mouse_status['X'], self.Mouse_status['Y'] = event.x, event.y
            self.Mouse_status['IsClicked'] = not self.Mouse_status['IsClicked']
        else:  
            x1, x2 = min(self.Mouse_status['X'], event.x), max(self.Mouse_status['X'], event.x)  
            y1, y2 = min(self.Mouse_status['Y'], event.y), max(self.Mouse_status['Y'], event.y)

            self.BBrect_id_tank.append(self.Current_BBrectangle)
            self.Current_boundingbox = [int(x1*xmultiplier),int(x2*xmultiplier)
                ,int(y1*ymultiplier),int(y2*ymultiplier)]
            self.boundingbox_tank.append(self.Current_boundingbox)
            self.BBmarker_id_tank.append(self.img_canvas.create_text((x1+x2)/2,(y1+y2)/2,
                text='[%d]'%(len(self.BBmarker_id_tank)+1),fill='yellow'))


            #reset the status
            self.Mouse_status['X'], self.Mouse_status['Y'] = None, None
            self.Mouse_status['IsClicked'] = not self.Mouse_status['IsClicked']
            self.Current_BBrectangle = None
            self.Current_boundingbox = [None,None,None,None]

    
    def MouseMove(self,event):
        if not self.src_imported:
            return        
        #update mouse position
        self.mouse_position_label.config(text='Cursor position\nX:%.4f,Y:%.4f'%(event.x,event.y))

        if not self.Mouse_status['X'] is None:
            self.Update_current_boundingbox(event.x,event.y)


    

    # other functions
    def Show_source_img(self):
        self.tkimg = ImageTk.PhotoImage(self.source_img_show)
        self.img_canvas.delete('all')
        self.img_canvas.create_image(0, 0, image=self.tkimg, anchor='nw')

    def Update_current_boundingbox(self,cur_mouse_x,cur_mouse_y):
        if not self.Current_BBrectangle is None:
            self.img_canvas.delete(self.Current_BBrectangle)
        x1, x2 = min(self.Mouse_status['X'], cur_mouse_x), max(self.Mouse_status['X'], cur_mouse_x)  
        y1, y2 = min(self.Mouse_status['Y'], cur_mouse_y), max(self.Mouse_status['Y'], cur_mouse_y)
        self.Current_BBrectangle = self.img_canvas.create_rectangle(x1,y1,x2,y2,width=2,outline='yellow')

