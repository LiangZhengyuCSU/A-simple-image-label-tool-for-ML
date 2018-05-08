import tkinter as tk
import imagelabeler
import numpy as np
from PIL import Image,ImageTk
import math

class imagecalibration_window(tk.Toplevel):


    def __init__(self, parent):
        '''
        Constructed function, initiate  arguments and UI.
        '''
        super().__init__()
        self.parent = parent # the parent window
        self.source_img = self.parent.source_img
        self.boundingbox = self.parent.boundingbox_tank [self.parent.img_pointer-1][0:5]
        self.img = self.parent.img_tank[self.parent.img_pointer-1]
        self.expand_step = tk.IntVar(value=10)
        self.move_step = tk.IntVar(value=10)
        # initiate arguments
        self.title('Selective search')
        self.geometry('760x380')
        self.resizable(False,False)
        ### components used to show the image ###
        # the label frame
        self.labelframe = tk.LabelFrame(self, text="Image to be calibrated")
        self.labelframe.grid(row=0,column=0,padx=15,pady=0)
        # the picture label
        tkimg = ImageTk.PhotoImage(self.img.resize((200,200)))
        self.pic_label = tk.Label(self.labelframe,bg='black',image=tkimg,width=200,height=200,compound = 'center')
        self.pic_label.pack()
        self.refresh_img()
        # the warning label
        self.warning_label = tk.Label(self.labelframe,text='Calibrate the image',
        width=40,height=1,font=('Times New Roman',10))
        self.warning_label.pack()
        # the confirm or cancel button
        tk.Button(self.labelframe,command=self.ok,text='Confirm',width=20,height=2
        ,font=('Times New Roman',12),relief='raised').pack(pady=5)
        tk.Button(self.labelframe,command=self.cancel,text='Cancel',width=20,height=2
        ,font=('Times New Roman',12),relief='raised').pack(pady=5)
        ### expanding button frame ###
        # the frame
        self.expand_frame = tk.LabelFrame(self, text="Expand")
        self.expand_frame.grid(row=0,column=1,padx=15,pady=0)
        # left button
        tk.Button(self.expand_frame, text="+", command=self.left_expand_plus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#C71585').grid(row=2,column=0)
        tk.Button(self.expand_frame, text="-", command=self.left_expand_minus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=2,column=1)
        # right button
        tk.Button(self.expand_frame, text="-", command=self.right_expand_minus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=2,column=3)
        tk.Button(self.expand_frame, text="+", command=self.right_expand_plus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#C71585').grid(row=2,column=4)
        # up button
        tk.Button(self.expand_frame, text="+", command=self.up_expand_plus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#C71585').grid(row=0,column=2)
        tk.Button(self.expand_frame, text="-", command=self.up_expand_minus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=1,column=2)
        # down button
        tk.Button(self.expand_frame, text="-", command=self.down_expand_minus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=3,column=2)
        tk.Button(self.expand_frame, text="+", command=self.down_expand_plus,width=3,height=2,
        relief='raised',font=('Times New Roman',12),bg='#C71585').grid(row=4,column=2)
        # step setter
        self.expand_step_frame=tk.Frame(self.expand_frame)
        self.expand_step_frame.grid(row=5,column=0,columnspan=5)
        tk.Label(self.expand_step_frame, text='Step(pixels):', width=10,height=2,
        font=('Times New Roman',12)).pack()
        tk.Entry(self.expand_step_frame, textvariable=self.expand_step, width=10).pack()
        ### moving button frame ###
        # the frame
        self.move_frame = tk.LabelFrame(self, text="Move")
        self.move_frame.grid(row=0,column=2,padx=15,pady=0)
        # left button
        tk.Button(self.move_frame, text="←", command=self.left_move,width=6,height=3,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=1,column=0)
        # right button
        tk.Button(self.move_frame, text="→", command=self.right_move,width=6,height=3,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=1,column=3)
        # up button
        tk.Button(self.move_frame, text="↑", command=self.up_move,width=6,height=4,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=0,column=2)
        # down button
        tk.Button(self.move_frame, text="↓", command=self.down_move,width=6,height=4,
        relief='raised',font=('Times New Roman',12),bg='#87CEEB').grid(row=2,column=2)
        # step setter
        self.move_step_frame=tk.Frame(self.move_frame)
        self.move_step_frame.grid(row=5,column=0,columnspan=5)
        tk.Label(self.move_step_frame, text='Step(pixels):', width=10,height=2,
        font=('Times New Roman',12)).pack()
        tk.Entry(self.move_step_frame, textvariable=self.move_step, width=10).pack()
        

        
        
    # button functions
    def left_expand_plus(self):
        self.expand_box(left=self.expand_step.get())
    def left_expand_minus(self):
        self.expand_box(left=-self.expand_step.get())
    def right_expand_plus(self):
        self.expand_box(right=self.expand_step.get())
    def right_expand_minus(self):
        self.expand_box(right=-self.expand_step.get())
    def up_expand_plus(self):
        self.expand_box(up=self.expand_step.get())
    def up_expand_minus(self):
        self.expand_box(up=-self.expand_step.get())
    def down_expand_plus(self):
        self.expand_box(low=self.expand_step.get())
    def down_expand_minus(self):
        self.expand_box(low=-self.expand_step.get())

    def up_move(self):
        self.move_box(vertical=-self.move_step.get())
    def down_move(self):
        self.move_box(vertical=+self.move_step.get())
    def left_move(self):
        self.move_box(horizontal=-self.move_step.get())
    def right_move(self):
        self.move_box(horizontal=self.move_step.get())

    # processor functions
    def expand_box(self,left=0,up=0,right=0,low=0):

        box = self.boundingbox[0:5]
        box[0] = box[0] -left
        box[1] = box[1] -up
        box[2] = box[2] +right
        box[3] = box[3] +low
        # if the bounding box exceed the boundary
        if box[0] < 0 or box[1] < 0 or box[2] > self.source_img.width\
        or box[3] > self.source_img.height:
            self.warning_label.config(text="Exceed the boundary",fg='red')
        else:
            self.warning_label.config(text="Calibrate the image",fg='black')
            self.boundingbox[0] = min(box[0],box[2]) #left
            self.boundingbox[2] = max(box[0],box[2]) #right
            self.boundingbox[1] = min(box[1],box[3]) #up
            self.boundingbox[3] = max(box[1],box[3]) #down
            self.img = self.source_img.crop((self.boundingbox[0],self.boundingbox[1],
                                            self.boundingbox[2],self.boundingbox[3]))
            self.refresh_img()

    def move_box(self,horizontal=0,vertical=0):
        box = self.boundingbox[0:5]
        # right and down as positive
        box[0] += horizontal
        box[2] += horizontal
        box[1] += vertical
        box[3] += vertical
        # if the bounding box exceed the boundary
        if box[0] < 0 or box[1] < 0 or box[2] > self.source_img.width\
        or box[3] > self.source_img.height:
            self.warning_label.config(text="Exceed the boundary",fg='red')
        else:
            self.warning_label.config(text="Calibrate the image",fg='black')
            self.boundingbox[0] = min(box[0],box[2]) #left
            self.boundingbox[2] = max(box[0],box[2]) #right
            self.boundingbox[1] = min(box[1],box[3]) #up
            self.boundingbox[3] = max(box[1],box[3]) #down
            self.img = self.source_img.crop((self.boundingbox[0],self.boundingbox[1],
                                            self.boundingbox[2],self.boundingbox[3]))
            self.refresh_img()

    def refresh_img(self):
        tkimg = ImageTk.PhotoImage(self.img.resize((200,200)))
        self.pic_label.config(image=tkimg)
        self.pic_label.image = tkimg
    
    def ok(self):
        # save the calibrated image:
        if (not self.boundingbox in self.parent.calibrated_boundingbox_after) or\
         not self.parent.img_pointer in self.parent.index_calibrated_img.append :
            self.parent.calibrated_boundingbox_before.append(self.parent.boundingbox_tank [self.parent.img_pointer-1]) 
            self.parent.calibrated_boundingbox_after.append(self.boundingbox)
            self.parent.calibrated_img_before.append(self.parent.img_tank[self.parent.img_pointer-1])    
            self.parent.calibrated_img_after.append(self.img)
            self.parent.index_calibrated_img.append(self.parent.img_pointer)
        self.destroy()
    
    def cancel(self):
        self.destroy()









        



        