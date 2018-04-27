import tkinter as tk
import imagelabeler
import math
### import pkgs
class window_size_setting(tk.Toplevel):


    def __init__(self, parent):
        '''
        Constructed function, initiate  arguments and UI.
        '''
        super().__init__()
        self.title('Settings')
        self.parent = parent # the parent window
        self.window_size = [100,100]
        self.stride = 25
        self.geometry('380x140')
        self.resizable(False,False)
        # the windowsize x row
        window_sizex_frame = tk.Frame(self)
        window_sizex_frame.pack(fill="x")
        tk.Label(window_sizex_frame, text='Windowsize x (100 pixels for default) ：', width=30,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.window_size_x = tk.IntVar(value=100)
        tk.Entry(window_sizex_frame, textvariable=self.window_size_x, width=12).pack(side=tk.LEFT)
        
        # the windowsize y row
        window_sizey_frame = tk.Frame(self)
        window_sizey_frame.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(window_sizey_frame, text='Windowsize y (100 pixels for default) ：', width=30,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.window_size_y = tk.IntVar(value=100)
        tk.Entry(window_sizey_frame, textvariable=self.window_size_y, width=12).pack(side=tk.LEFT)
        
        # the button row
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x",pady=10)
        tk.Button(self.button_frame, text="Cancel", command=self.cancel,
        relief='raised',font=('Times New Roman',12)).pack(side=tk.RIGHT,padx=20)
        tk.Button(self.button_frame, text="Confirm", command=self.ok,
        relief='raised',font=('Times New Roman',12)).pack(side=tk.LEFT,padx=20)
        # the warning label
        self.warning_label = tk.Label(self,text='Please input the desired windowsize',
        width=45,height=20,font=('Times New Roman',10))
        self.warning_label.pack(pady=5,fill='x')
        

    def ok(self):
        img_width = self.parent.source_img.width
        img_height = self.parent.source_img.height
        x = self.window_size_x.get()
        y = self.window_size_y.get()
        if not isinstance(x,(int)) or not isinstance(y,(int)) or x <=0 or y<=0:
            self.warning_label.config(text='The windowsize can only be set as positive integer',
            fg='red')
            self.warning_label.text = 'The windowsize can only be set as positive integer'
            self.warning_label.fg = 'red'

        elif x > img_width or y > img_height:
            self.warning_label.config(text='The windowsize can not be larger than the imagesize (%dx%d)'%(img_width,img_height),
            fg='red')    
        else:
            # update the argument
            self.parent.window_size[0] = x
            self.parent.window_size[1] = y
            self.parent.stride = int(math.floor(min(x,y)/4))     
            self.destroy() # destroy the window
        
    def cancel(self):
        self.destroy() # destroy the window
        self.parent.wait = False
