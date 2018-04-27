import tkinter as tk
import imagelabeler
import math

### import pkgs
class selectivesearch_setting(tk.Toplevel):


    def __init__(self, parent):
        '''
        Constructed function, initiate  arguments and UI.
        '''
        super().__init__()
        self.title('Settings')
        self.parent = parent # the parent window
        self.window_size = [100,100]
        self.stride = 25
        self.geometry('450x250')
        self.resizable(False,False)
        # the "Scale" row
        Scale_frame = tk.Frame(self)
        Scale_frame.pack(fill="x")
        tk.Label(Scale_frame, text='Scale (200 for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Scale = tk.IntVar(value = 200)
        tk.Entry(Scale_frame, textvariable=self.Scale, width=8).pack(side=tk.LEFT)
        # the "Sigma" row
        Sigma_frame = tk.Frame(self)
        Sigma_frame.pack(fill="x")
        tk.Label(Sigma_frame, text='Sigma (0.6 for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Sigma = tk.DoubleVar(value = 0.6)
        tk.Entry(Sigma_frame, textvariable=self.Sigma, width=8).pack(side=tk.LEFT)        
        # the "Min_size" row
        Min_size_frame = tk.Frame(self)
        Min_size_frame.pack(fill="x")
        tk.Label(Min_size_frame, text='Min_size (80 for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Min_size = tk.IntVar(value = 80)
        tk.Entry(Min_size_frame, textvariable=self.Min_size, width=8).pack(side=tk.LEFT)              
        # the "Min_elongation" row
        Min_elongation_frame = tk.Frame(self)
        Min_elongation_frame.pack(fill="x")
        tk.Label(Min_elongation_frame, text='Min_elongation (0.5 for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Min_elongation = tk.DoubleVar(value = 0.5)
        tk.Entry(Min_elongation_frame, textvariable=self.Min_elongation, width=8).pack(side=tk.LEFT)  
        # the "Maximum_box" row
        Maximum_box_frame = tk.Frame(self)
        Maximum_box_frame.pack(fill="x")
        tk.Label(Maximum_box_frame, text='Maxsize of bounding box (10000 pixels for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Maximum_box = tk.IntVar(value = 10000)
        tk.Entry(Maximum_box_frame, textvariable=self.Maximum_box, width=8).pack(side=tk.LEFT)   
        # the "Minimum_box" row
        Minimum_box_frame = tk.Frame(self)
        Minimum_box_frame.pack(fill="x")
        tk.Label(Minimum_box_frame, text='Minsize of bounding box (100 pixels for default) ：', width=40,
        font=('Times New Roman',12)).pack(side=tk.LEFT)
        self.Minimum_box = tk.IntVar(value =100 )
        tk.Entry(Minimum_box_frame, textvariable=self.Minimum_box, width=8).pack(side=tk.LEFT)        
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
        Scale = self.Scale.get()
        Sigma = self.Sigma.get()
        Min_size = self.Min_size.get()
        Min_elongation = self.Min_elongation.get()
        Maximum_box = self.Maximum_box.get()
        Minimum_box = self.Maximum_box.get()

        for i in [Scale,Sigma,Min_size,Min_elongation,Maximum_box,Minimum_box]:
            if i <=0:
                self.warning_label.config(text='None positive value detected',
                fg='red')
                return

        if  not isinstance(Scale,(int)) or not isinstance(Min_size,(int)) \
        or not isinstance(Maximum_box,(int)) or not isinstance(Minimum_box,(int)):
            self.warning_label.config(text='Scale, Min_size, Maximum_box, Minimum_box can only be set as positive integer',
            fg='red')
        elif Sigma > 1 or Min_elongation > 1:
            self.warning_label.config(text='Sigma and Min_elongation must smaller than 1',
            fg='red')    
        else:
            # update the argument
            self.parent.scale = Scale
            self.parent.sigma = Sigma 
            self.parent.min_size = Min_size
            self.parent.minmum_elongation = Min_elongation # the minimum elongation 0.5 for default
            self.parent.maximum_box_size = Maximum_box # the maximum boxsize (100x100 for default)
            self.parent.minimum_box_size = Minimum_box # the minimum boxsize (10x10 for default)
        self.destroy()
        
    def cancel(self):
        self.destroy() # destroy the window
        self.parent.wait = False