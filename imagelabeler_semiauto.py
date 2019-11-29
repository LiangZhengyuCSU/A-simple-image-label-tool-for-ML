# -*- coding:utf-8 -*-  
#----------------------------------------------------------------------------------#  
# Name:       A simple image labeling tool-method_semiauto                         #
# Coder:      Zhengyu Liang at Central South Univ.                                 #
# Date:       May, 14, 2018                                                        #
# Git:        https://github.com/LiangZhengyuCSU/A-simple-image-label-tool-for-ML  #    
#----------------------------------------------------------------------------------# 

### ---------------- Import pkgs ---------------- ###
import os
import re
import tkinter as tk
import numpy as np 
from PIL import Image,ImageTk,ImageDraw
import tkinter.filedialog as tkfd
import tkinter.messagebox as messagebox
from queue import Queue
from tkinter.filedialog import askdirectory
import glob
import time
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
        self.BB_ishide = []
        self.source_img_path = 'None'
        self.Current_boundingbox = [None,None,None,None] # recording the BBdata
        self.Current_BBrectangle = None # recording the canvas rectangle of currentBB
        self.Currnet_guideline = [None,None]
        # config arguments
        self.src_imported = False
        self.wait = False # busy flag
        self.work_dir = None
        self.Mouse_status = {'IsClicked': False,'X': None,'Y': None}
        # other arguments
        self.guideline = True
        self.BBcolor = 'Yellow'
        self.BBcolortank = ['Yellow','Blue','Cyan','Green','White','Red']        
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
        self.img_name_label = tk.Label(self.window,text=self.source_img_path, width = 100)
        self.img_name_label.grid(row = 0, column = 0, sticky = 'w', columnspan = 4)
        # The import button
        self.Import_button = tk.Button(self.window,command=self.import_image,text='Import source image'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised')
        self.Import_button.grid(row = 0, column = 4)
        # The img canvas  
        self.img_canvas = tk.Canvas(self.window, cursor='circle',width=800,height=600,bg='black')  
        self.img_canvas.bind("<Button-1>", self.LClick_mouse_incanvas)
        self.img_canvas.bind("<Button-2>", self.MClick_mouse_incanvas)
        self.img_canvas.bind("<Button-3>", self.RClick_mouse_incanvas)  
        self.img_canvas.bind("<Motion>", self.MouseMove)  
        self.img_canvas.grid(row = 1, column = 0, rowspan = 8, columnspan = 4, sticky = 'nw')
        # The mouse position reminder
        self.mouse_position_label = tk.Label(self.window,text='Cursor position\nX:null,Y:null')
        self.mouse_position_label.grid(row = 9, column = 4)

        # frame that contains both the list box and the scrollbar
        self.listbox_frame=tk.LabelFrame(self.window,text='Bounding boxes',font=('Times New Roman',12))
        self.listbox_frame.grid(row=1,column=4, rowspan = 4)
        # the scrollbar attach to the bb browser
        self.list_scrollbar = tk.Scrollbar(self.listbox_frame) 
        self.list_scrollbar.pack(side='right', fill='y')
        self.boundingbox_browser = tk.Listbox(self.listbox_frame,listvariable=None
            ,yscrollcommand=self.list_scrollbar.set, height = 24)
        self.boundingbox_browser.pack(side='left', fill='y')
        self.list_scrollbar.config(command=self.boundingbox_browser.yview)
        # the delete button
        self.Delete_button = tk.Button(self.window,command=self.delete_BB,text='Delete'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised', width = 15)
        self.Delete_button.grid(row = 6, column = 4)
        # the hide button
        self.Hide_button = tk.Button(self.window,command=self.Hide_Show_BB,text='Hide | Show'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised', width = 15)
        self.Hide_button.grid(row = 7, column = 4)
        # the Change BBcolor button
        self.Changecolor_button = tk.Button(self.window,command=self.changeBB_color,text='Change Color'
        ,font=('Times New Roman',12),bg=self.BBcolor ,state='normal', width = 15)
        self.Changecolor_button.grid(row = 8, column = 4)
        # the save button
        self.Save_button= tk.Button(self.window,command=self.save_func,text='Save'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised', width = 15)
        self.Save_button.grid(row = 9, column = 0, sticky = 'w')
        # the load button
        self.Load_button= tk.Button(self.window,command=self.load_func,text='Load'
        ,font=('Times New Roman',12),bg='white',state='normal',relief='raised', width = 15)
        self.Load_button.grid(row = 9, column = 1, sticky = 'w')

    # arguments functions
    def init_img(self):
        '''
        initiate all image arguments
        '''
        # source image arguments
        self.source_img = None
        self.source_img_size = None
        self.source_img_show = None
        self.show_img_size = [800,600]
        self.boundingbox_tank = []
        self.BBrect_id_tank = []
        self.BBmarker_id_tank = []
        self.BB_ishide = []
        self.source_img_path = 'None'
        self.Current_boundingbox = [None,None,None,None] # recording the BBdata
        self.Current_BBrectangle = None # recording the canvas rectangle of currentBB
        self.Currnet_guideline = [None,None]
        # config arguments
        self.src_imported = False
        self.wait = False # busy flag
        self.work_dir = None
        self.Mouse_status = {'IsClicked': False,'X': None,'Y': None}
        self.img_name_label.config(text=self.source_img_path)


    # event function
    def LClick_mouse_incanvas(self, event):
        '''
        launch when mouse clicked in canvas
        '''
        if not self.src_imported:
            messagebox.showwarning(title='warning',message='Please import the source image first')
            return
        if not self.Mouse_status['IsClicked']:  
            self.Mouse_status['X'], self.Mouse_status['Y'] = event.x, event.y
            self.Mouse_status['IsClicked'] = True
        else:  
            x1, x2 = min(self.Mouse_status['X'], event.x), max(self.Mouse_status['X'], event.x)  
            y1, y2 = min(self.Mouse_status['Y'], event.y), max(self.Mouse_status['Y'], event.y)
            # create the BB
            self.Current_boundingbox = [x1/self.show_img_size[0],y1/self.show_img_size[1]
                ,x2/self.show_img_size[0],y2/self.show_img_size[1]]
            # the bounding boxes ,stored as relative coordinate (left top right bottom)
            self.BBrect_id_tank.append(self.Current_BBrectangle)
            self.boundingbox_tank.append(self.Current_boundingbox)
            self.BB_ishide.append(False)
            self.BBmarker_id_tank.append(self.img_canvas.create_text((x1+x2)/2,(y1+y2)/2,
                text='[%d]'%(len(self.BBmarker_id_tank)+1),fill=self.BBcolor))
            self.insert_to_BBbrowser(len(self.boundingbox_tank))
            #reset the status
            self.Mouse_status['X'], self.Mouse_status['Y'] = None, None
            self.Mouse_status['IsClicked'] = False
            self.Current_BBrectangle = None
            self.Current_boundingbox = [None,None,None,None]

    def RClick_mouse_incanvas(self, event):
        '''
        launch when mouse right_clicked in canvas
        '''
        if not self.src_imported or not self.Mouse_status['IsClicked']:
            return
        else:
            # delete the Current_BBrectangle
            self.img_canvas.delete(self.Current_BBrectangle)
            #reset the status
            self.Mouse_status['X'], self.Mouse_status['Y'] = None, None
            self.Mouse_status['IsClicked'] = False
            self.Current_BBrectangle = None
            self.Current_boundingbox = [None,None,None,None]   
    def MClick_mouse_incanvas(self, event):
        '''
        launch when middle mouse button clicked in canvas
        '''
        self.guideline = not self.guideline
    
    def MouseMove(self,event):
        '''
        The mouse Move func
        '''
        if not self.src_imported:
            return        
        #update mouse position
        self.mouse_position_label.config(text='Cursor position\nX:%d,Y:%d'%(event.x,event.y))
        #update guide line
        self.Update_current_guideline(event.x,event.y)

        if not self.Mouse_status['X'] is None:
            self.Update_current_boundingbox(event.x,event.y)


    # button function
    def delete_BB(self):
        '''
        delete_boundingbox
        '''        
        def delete(li, index):# defining an delete function
            li = li[:index] + li[index+1:]
            return li
        
        if not self.src_imported :
            messagebox.showwarning(title='warning',message='Please import some image first')
        else:
            try:
                target = self.boundingbox_browser.get(self.boundingbox_browser.curselection())
            except:
                return
            # find the first N number
            mode = re.compile(r'\d+')
            target = mode.findall(target)[0]
            target = int(target)
            self.boundingbox_tank = delete(self.boundingbox_tank,target-1)
            self.BB_ishide = delete(self.BB_ishide,target-1)
            self.BBmarker_id_tank = []
            self.BBrect_id_tank = []
            self.refresh_BB()   
        
    def Hide_Show_BB(self):
        if not self.src_imported :
            messagebox.showwarning(title='warning',message='Please import some image first')
        else:
            try:
                target = self.boundingbox_browser.get(self.boundingbox_browser.curselection())
            except:
                return
        mode = re.compile(r'\d+')
        target = mode.findall(target)[0]
        target = int(target)
        self.BB_ishide[target-1] = not self.BB_ishide[target-1]
        if self.BB_ishide[target-1]:
            state = 'hidden'
            textcolor = 'gray'
        else:
            state = 'normal'
            textcolor = 'black'
        BBid = self.BBrect_id_tank[target-1]
        Markerid = self.BBmarker_id_tank[target-1]
        self.img_canvas.itemconfig(BBid,state=state)
        self.img_canvas.itemconfig(Markerid,state=state)
        self.boundingbox_browser.itemconfig(target-1,fg=textcolor)

    def changeBB_color(self):
        Colorindex = self.BBcolortank.index(self.BBcolor)
        Colorindex += 1
        if Colorindex > len(self.BBcolortank)-1:
            Colorindex = 0
        self.BBcolor = self.BBcolortank[Colorindex]
        self.refresh_BB()
        self.Changecolor_button.config(bg = self.BBcolor)
        


    def import_image(self):
        '''
        Import imgfile as the source img.
        '''       
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
    def load_func(self):
        '''
        Load the source img and boundingboxes
        '''
        answer = 'yes'
        if len(self.boundingbox_tank)>0:
            answer=messagebox.askquestion(title='Attention please',
            message='Importing a new source image will delete all unsaved images\n, are you still want to import another image?')
        if  answer == 'yes':
            # find sourceimg and boundingboxfile
            filetypes =[("jpg", '*.jpg',),  
                    ("PNG", '*.png',),  
                    ("tif", '*.tif',)]  
            img_filename = tkfd.askopenfilename(filetypes=filetypes)
            if img_filename == '':
                return
            filetypes =[("BoundingBox", '*.BBX')] 
            BB_filename = tkfd.askopenfilename(filetypes=filetypes)
            if BB_filename == '':
                return

            self.init_img() 
            try: #load image file
                self.source_img = Image.open(img_filename)
            except:
                messagebox.showwarning(title='warning',message='Error encounted when opening the source image')
                self.init_img() 
                return
            self.source_img_size = [self.source_img.width,self.source_img.height]
            self.source_img_show = self.source_img.resize((self.show_img_size[0],
                self.show_img_size[1]))
            self.src_imported = True
            self.Show_source_img()
            self.source_img_path = img_filename
            self.img_name_label.config(text=self.source_img_path)
            
            try:#load the bounding box
                bb = self.load_BB(BB_filename)
                self.boundingbox_tank = bb
            except:
                messagebox.showwarning(title='warning',message='Error encounted when importing the bounding box')
                self.init_img() 
                return
            # initiate the hidden status
            for _ in range(0,len(self.boundingbox_tank)):
                self.BB_ishide.append(False)
            self.refresh_BB()




        elif answer == 'no':
            return
        
    
    def save_func(self):
        '''
        Save the source img with boundingboxes
        '''
        if not self.src_imported:
            messagebox.showwarning(title='warning',message='Please import the source image first')
            return
        if not self.boundingbox_tank:
            messagebox.showwarning(title='warning',message='The bounding box tank is empty')
            return
        workdir = askdirectory() # ask an directory
        if workdir == '':
            return      
        save_path = workdir + '\\Boundingboxes'
        cur_time = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))  
        self.mkdir(save_path)
        # save the source img
        save_name = os.path.join(save_path, 'Source'+cur_time+'.jpg')
        self.source_img.save(save_name)
        # save the bounding box
        save_name = os.path.join(save_path, 'Boundingboxes'+cur_time+'.BBX')
        self.save_BB(save_name)
        messagebox.showinfo(title='information',message='%d Bonding boxes has been saved'%(len(self.boundingbox_tank)))  
        self.init_img()
        self.refresh_BB()
        self.img_canvas.delete('all')
         

    

    # operation functions
    def Show_source_img(self):
        self.tkimg = ImageTk.PhotoImage(self.source_img_show)
        self.img_canvas.delete('all')
        self.img_canvas.create_image(0, 0, image=self.tkimg, anchor='nw')

    def Update_current_boundingbox(self,cur_mouse_x,cur_mouse_y):
        if not self.Current_BBrectangle is None:
            self.img_canvas.delete(self.Current_BBrectangle)
        x1, x2 = min(self.Mouse_status['X'], cur_mouse_x), max(self.Mouse_status['X'], cur_mouse_x)  
        y1, y2 = min(self.Mouse_status['Y'], cur_mouse_y), max(self.Mouse_status['Y'], cur_mouse_y)
        self.Current_BBrectangle = self.img_canvas.create_rectangle(x1,y1,x2,y2,width=2,outline=self.BBcolor)

    def Update_current_guideline(self,cur_mouse_x,cur_mouse_y):
        if not self.Currnet_guideline[0] is None:
            self.img_canvas.delete(self.Currnet_guideline[0])
            self.img_canvas.delete(self.Currnet_guideline[1])
        
        if self.guideline:
            state = 'normal'
        else:
            state = 'hidden'
        self.Currnet_guideline[0] = self.img_canvas.create_line(0,cur_mouse_y,self.show_img_size[0],cur_mouse_y,
           fill = self.BBcolor,dash=(4, 4),state = state)
        self.Currnet_guideline[1] = self.img_canvas.create_line(cur_mouse_x,0,cur_mouse_x,self.show_img_size[1],
           fill = self.BBcolor,dash=(4, 4),state = state)        


    
    def insert_to_BBbrowser(self,BBindex):
        '''
        insert_boundingbox to browser
        '''
        label = '[%d]-Bounding box'%(BBindex) 
        self.boundingbox_browser.insert(BBindex-1,label)


    def refresh_BB(self):
        '''
        refresh the Bounding boxes in both canvas and browser,by delete all elements and reconstruct them
        '''
        # refresh browser
        if not self.boundingbox_tank:
            self.boundingbox_browser.delete(0,'end')
        else:
            self.boundingbox_browser.delete(0,'end')
            for i in range(0,len(self.boundingbox_tank)):
                label = '[%d]-Bounding box'%(i+1) 
                self.boundingbox_browser.insert(i,label)
        # refresh canvas 
        if not self.src_imported:
            return
        self.img_canvas.delete('all')
        self.BBrect_id_tank = []
        self.BBmarker_id_tank = []
        self.img_canvas.create_image(0, 0, image=self.tkimg, anchor='nw')
        if  self.boundingbox_tank:
            for i in range(0,len(self.boundingbox_tank)):
                x1,y1,x2,y2 = self.show_img_size[0]*self.boundingbox_tank[i][0],self.show_img_size[1]*self.boundingbox_tank[i][1],\
                self.show_img_size[0]*self.boundingbox_tank[i][2],self.show_img_size[1]*self.boundingbox_tank[i][3]
                
                if self.BB_ishide[i]:# see if the bounding box has been hidden
                    self.Current_BBrectangle = self.img_canvas.create_rectangle(x1,y1,x2,y2,
                        width=2,outline=self.BBcolor,state='hidden')
                    self.BBmarker_id_tank.append(self.img_canvas.create_text((x1+x2)/2,(y1+y2)/2,
                    text='[%d]'%(i+1),fill=self.BBcolor,state='hidden'))
                else:
                    self.Current_BBrectangle = self.img_canvas.create_rectangle(x1,y1,x2,y2,
                        width=2,outline=self.BBcolor)
                    self.BBmarker_id_tank.append(self.img_canvas.create_text((x1+x2)/2,(y1+y2)/2,
                    text='[%d]'%(i+1),fill=self.BBcolor))

                self.BBrect_id_tank.append(self.Current_BBrectangle)

                # set the color as gray if the bb is hidden 
                if self.BB_ishide[i]:
                    self.boundingbox_browser.itemconfig(i,fg='gray')
        #reset the status
        self.Mouse_status['X'], self.Mouse_status['Y'] = None, None
        self.Mouse_status['IsClicked'] = False
        self.Current_BBrectangle = None
        self.Current_boundingbox = [None,None,None,None]
        
    def mkdir(self,path):
        '''Check if the path exist, if not, make the path'''
        # exclude the space 
        path = path.strip()
        # exclude the '\' mark in the end of the path 
        path = path.rstrip("\\")
        # see if the path exist
        isExists = os.path.exists(path)
        if not isExists:
            # create the path if not exist
            os.makedirs(path) 
            return True
        else:
            # do nothing if the path exist
            return False

    def save_BB(self,filename):
        '''Save Bounding box into ASCII file'''
        f = open(filename, 'w')
        for i in self.boundingbox_tank:
            for j in i:
                f.write('%f '%j)
            f.write('\n')
        f.close()
    
    def load_BB(self,filename):
        '''Load Bounding boxes from ASCII file'''
        bb=[]
        f = open(filename)
        line = f.readline() 
        while line:
            bb.append(list(map(float,line.strip().split(' '))))
            line = f.readline()
        f.close()
        return bb







        

        



