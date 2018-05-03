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
## child windows ##
import window_size_setting
import selective_search_window
import selectivesearch_setting
import imagecalibration_window
## ------------- ##

## import an open source selctive search package avaliable on https://github.com/AlpacaDB/selectivesearch ##
import selectivesearch 
## ------------ one can also use "pip install selectivesearch" to install this package ------------------ ##

### ---------------- Import pkgs ---------------- ###

class imagelabeler(object):

    def __init__(self):
        '''
        Constructed function, initiate  arguments.
        '''
        # source image arguments
        self.source_img = []
        self.source_img_show = []
        # config arguments
        self.src_imported = False
        self.unlabelimg_imported = False
        self.wait = False # busy flag
        self.work_dir = None
        self.saved = False
        # sliding window algorithm arguments #
        self.window_size = [100,100]
        self.stride = 25
        # selective search algorithm arguments #
        self.scale = 200 
        self.sigma = 0.6 
        self.min_size = 80
        self.minmum_elongation = 0.5 # the minimum elongation 0.5 for default
        self.maximum_box_size = 10000 # the maximum boxsize (100x100 for default)
        self.minimum_box_size = 100 # the minimum boxsize (10x10 for default)
        # bounding boxes arguments #
        self.boundingbox_tank = [] # used to catch the outputed bounding box (only in selective search)
        self.img_tank = []
        self.img_label = []
        self.img_pointer = 0
        # calibrated bounding boxes arguments #
        self.calibrated_img_before = []
        self.calibrated_img_after = [] 
        self.calibrated_boundingbox_before = []
        self.calibrated_boundingbox_after = []
        self.index_calibrated_img = []
  
        # launch the UI
        self.init_UI()
    
    def init_UI(self):
        '''
        Initiate the UI.
        '''
        # the window
        self.window = tk.Tk()
        self.window.title('Labeler')
        self.window.geometry('740x360')
        self.window.resizable(False,False)
        ### components used to show the image ###
        # the label frame
        self.labelframe = tk.LabelFrame(self.window, text="")
        self.labelframe.grid(row=0,column=1,padx=1,pady=1,columnspan=2)
        # the picture label
        self.pic_label = tk.Label(self.labelframe,bg='black'
            ,image=tk.BitmapImage(),width=200,height=200,compound = 'center')
        self.pic_label.pack()
        # the reminder label
        self.reminder_label = tk.Label(self.labelframe
        ,text='Please import the source Image',font=('Times New Roman',12)
        ,image=tk.BitmapImage(),width=190,height=20,compound = 'center',
        relief="solid", borderwidth=1)
        self.reminder_label.pack(fill='x')
        # the previous button
        self.transfer_button = tk.Button(self.labelframe,command=self.previous_button_func,
        text='Previous image',width=5,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.transfer_button.pack(fill='x')
        # the next button
        self.transfer_button = tk.Button(self.labelframe,command=self.next_button_func,
        text='Next image',width=5,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.transfer_button.pack(fill='x')
        # the image calibration button
        self.calibrate_button = tk.Button(self.labelframe,command=self.calibrate_button_func,
        text='Calibrate image',width=5,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.calibrate_button.pack(fill='x')

        ### the cutted image browser(a list box) ###
        # frame that contains both the list box and the scrollbar
        self.listbox_frame=tk.LabelFrame(self.window,text='Images',font=('Times New Roman',12))
        self.listbox_frame.grid(row=0,column=4,padx=10,pady=10)
        # the scrollbar in the image browser
        self.list_scrollbar = tk.Scrollbar(self.listbox_frame) 
        self.list_scrollbar.pack(side='right', fill='y')
        self.image_browser = tk.Listbox(self.listbox_frame,listvariable=None,
            width=13,height=15,yscrollcommand=self.list_scrollbar.set)
        self.image_browser.pack()
        self.list_scrollbar.config(command=self.image_browser.yview)
        # the button helps transfering to the selected image
        self.transfer_button = tk.Button(self.listbox_frame,command=self.transfer_button_func,
        text='Transfer to',width=10,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.transfer_button.pack(side='bottom')


        ### the calibrated image browser(a list box) ###
        # frame that contains both the list box and the scrollbar
        self.calibrated_listbox_frame=tk.LabelFrame(self.window,text='calibrated images',font=('Times New Roman',12))
        self.calibrated_listbox_frame.grid(row=0,column=5,padx=10,pady=10)
        # the scrollbar in the image browser
        self.calibrated_list_scrollbar = tk.Scrollbar(self.calibrated_listbox_frame) 
        self.calibrated_list_scrollbar.pack(side='right', fill='y')
        self.calibrated_image_browser = tk.Listbox(self.calibrated_listbox_frame,listvariable=None,
            width=16,height=15,yscrollcommand=self.calibrated_list_scrollbar.set)
        self.calibrated_image_browser.pack()
        self.list_scrollbar.config(command=self.calibrated_image_browser.yview)
        # the button helps delete the selected image
        self.calibrated_delete_button = tk.Button(self.calibrated_listbox_frame,command=self.delete_button_func,
        text='Delete',width=10,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.calibrated_delete_button.pack(side='bottom')

        ### buttons in the button frame ###
        # the button frame
        self.button_frame = tk.LabelFrame(self.window, text="")
        self.button_frame.grid(row=0,column=3,padx=10,pady=10)
        # the boundingbox algorithm selection frame
        self.algorithm_frame = tk.LabelFrame(self.button_frame,text='Select boundingbox algorithm',
        font=('Times New Roman',12),fg='red')
        self.algorithm_frame.pack(side='top')
        # the radio button to select bounding box algorithm
        self.boundingbox_algorithm = tk.IntVar(value=None) # 1 for sliding window 2 for selcetive search
        self.r_slidingwindow = tk.Radiobutton(self.algorithm_frame,text='Sliding window',
        variable=self.boundingbox_algorithm,value= 1, command = self.select_BBalgorithm)
        self.r_slidingwindow.pack(fill='x')
        self.r_selectivesearch = tk.Radiobutton(self.algorithm_frame,text='Selective search',
        variable=self.boundingbox_algorithm,value= 2, command = self.select_BBalgorithm)
        self.r_selectivesearch.pack(fill='x')  
        # the cutting button
        self.cut_button = tk.Button(self.button_frame,command=self.generate_BB,
        text='Generate bounding box\n (No algorithm selected)'
        ,width=18,height=2,font=('Times New Roman',10),bg='#1E90FF',compound = 'center',state='normal',
        relief='raised')
        self.cut_button.pack(fill='x',pady=8)
        # labeling button 0
        self.labeling_0 = tk.Button(self.button_frame,command=self.label_as_0,text='Set the Label as "0"'
        ,width=14,height=1,font=('Times New Roman',12),bg='white',compound = 'center',state='normal',
        relief='raised')
        self.labeling_0.pack(fill='x',pady=8)
        # labeling button 1
        self.labeling_1 = tk.Button(self.button_frame,command=self.label_as_1,text='Set the Label as "1"'
        ,width=14,height=1,font=('Times New Roman',12),bg='white',compound = 'center',state='normal',
        relief='raised')
        self.labeling_1.pack(fill='x',pady=8)
        # labeling button 2
        self.labeling_2 = tk.Button(self.button_frame,command=self.label_as_2,text='Set the Label as "2"'
        ,width=14,height=1,font=('Times New Roman',12),bg='white',compound = 'center',state='normal',
        relief='raised')
        self.labeling_2.pack(fill='x',pady=8)
        # labeling button 3
        self.labeling_3 = tk.Button(self.button_frame,command=self.label_as_3,text='Set the Label as "3"'
        ,width=14,height=1,font=('Times New Roman',12),bg='white',compound = 'center',state='normal',
        relief='raised')
        self.labeling_3.pack(fill='x',pady=8)
        ### the open_File menu ###
        self.menubar = tk.Menu(self.window)  
        self.filemenu = tk.Menu(self.menubar,tearoff=0)
        # the Open command 
        self.filemenu.add_command(label='Open the source picture', accelerator='Ctrl+o',  
            command=self.import_image, underline=0)
        self.filemenu.add_command(label='Import unlabeled images', accelerator='Ctrl+o+i',  
            command=self.import_unlabel_img, underline=0)
        # the save command 
        self.filemenu.add_command(label='Save labels and calibration', accelerator='Ctrl+s',  
        command=self.save_func, underline=0)
        self.filemenu.add_command(label='Save unlabeled images', accelerator='Ctrl+s+u',  
        command=self.save_unlabel_img, underline=0)

        ### the setting menu ###
        self.setwindow_menu = tk.Menu(self.menubar,tearoff=0)
        # the sliding window algorithm configuration command 
        self.setwindow_menu.add_command(label='Setting the parameters for sliding window algorithm', accelerator='Ctrl+i',  
                command=self.set_windowsize_func, underline=0)
        # the selective search algorithm configuration command 
        self.setwindow_menu.add_command(label='Setting the parameters for selective search algorithm', accelerator='Ctrl+i+s',  
                command=self.set_search_func, underline=0)
        # pack the menubar to the main window
        self.menubar.add_cascade(label='File',menu=self.filemenu)
        self.menubar.add_cascade(label='Configuration',menu=self.setwindow_menu)
        self.window.config(menu=self.menubar) 


        # launch the main window
        self.window.mainloop()

    ### functions for all contents ###
    def init_imgtank(self):
        '''initiate the imagetank and display the source image'''
        self.img_tank = []
        self.img_label = []
        self.img_pointer = 0
        self.boundingbox_tank = []
        self.calibrated_img_before = []
        self.calibrated_img_after = [] 
        self.calibrated_boundingbox_before = []
        self.calibrated_boundingbox_after = []
        self.index_calibrated_img = []        
        self.change_browser()
        self.change_calibrated_browser()

        if not self.source_img:
            self.pic_label.config(image=tk.BitmapImage())
            self.pic_label.image=tk.BitmapImage()
            self.change_reminder('Please import the source Image')
        else:
            # reset the picture label        
            source_img_show = self.source_img.resize((200,200))
            self.change_img(source_img_show)
            self.change_reminder('Now dispaly the source image')



    def init_img(self):
        '''initiate the imagetank and display the source image'''
        self.img_tank = []
        self.img_label = []
        self.img_pointer = 0
        self.calibrated_img_before = []
        self.calibrated_img_after = [] 
        self.calibrated_boundingbox_before = []
        self.calibrated_boundingbox_after = []
        self.index_calibrated_img = []        
        self.source_img = []
        self.source_img_show = []
        self.boundingbox_tank = []
        self.change_browser()
        self.change_calibrated_browser()
        # config arguments
        self.src_imported = False
        self.unlabelimg_imported = False
        self.wait = False # busy flag
        self.saved = False
        # reset the picture label
        self.pic_label.config(image=tk.BitmapImage())
        self.pic_label.image=tk.BitmapImage()
        self.change_reminder('Please import the source Image')
    
    def change_img(self,img):
        '''change the image of the imagelabel'''
        tkimg=ImageTk.PhotoImage(img)
        self.pic_label.config(image=tkimg)
        self.pic_label.image=tkimg
    
    def change_reminder(self,text):
        '''change the text of the reminderlabel'''
        self.reminder_label.config(text=text,image=tk.BitmapImage())
        self.reminder_label.text=text

    def change_browser(self):
        '''
        this function is used to refresh the img_tank listbox, the procedure generally designed as first
        destory the entire listbox and then rebuild it. This is actually unnecessary for many caces
        and can be optimized.
        '''
        if not self.img_tank:
            self.image_browser.delete(0,'end')
        else:
            self.image_browser.delete(0,'end')
            for i in range(0,len(self.img_tank)):
                if self.img_label[i][0] is None:
                    list_label='%d(No label)' %(i+1)
                    self.image_browser.insert(i,list_label)
                else:
                    list_label='%d(Label: "%d")' %(i+1,self.img_label[i][0])
                    self.image_browser.insert(i,list_label)

    def change_calibrated_browser(self):
        '''
        this function is used to refresh the calibrated img listbox, the procedure generally designed as first
        destory the entire listbox and then rebuild it. This is actually unnecessary for many caces
        and can be optimized.
        '''
        if not self.calibrated_boundingbox_after:
            self.calibrated_image_browser.delete(0,'end')
        else:
            self.calibrated_image_browser.delete(0,'end')
            for i in range(0,len(self.calibrated_boundingbox_after)):
                list_label='%d (No.%d image)' %(i+1,self.index_calibrated_img[i])
                self.calibrated_image_browser.insert(i,list_label)

    def transfer_to_img(self,target):
            self.img_pointer = target
            if  self.img_pointer > len(self.img_tank): 
                self.img_pointer = len(self.img_tank) 
            elif self.img_pointer < 1:
                self.img_pointer = 1
            target_img=self.img_tank[self.img_pointer-1]
            target_img=target_img.resize((200,200))
            self.change_img(target_img)
            self.change_reminder('Now dispaly No. %d image' % self.img_pointer)
        
    ### functions for menus ###
    def import_image(self):
        '''
        Import imgfile as the source img.
        '''
        if self.wait:
            return        
        answer = 'yes'
        if len(self.img_tank)>0:
            answer=messagebox.askquestion(title='Attention please',
            message='Importing a new source image will delete all unsaved images\n, are you still want to import another image?')
        
        if  answer == 'yes':
            filetypes =[("jpg", '*.jpg',),  
                    ("PNG", '*.png',),  
                    ("tif", '*.tif',)]  
            filename = tkfd.askopenfilename(filetypes=filetypes)
            if filename == '':
                return  
            self.source_img = Image.open(filename)
            self.init_imgtank()
            self.src_imported = True
        elif answer == 'no':
            return
    
    def import_unlabel_img(self):
        '''
        Import directly imagetank from unlabeled image files.
        '''
        if self.wait:
            return        
        answer = 'yes'
        if len(self.img_tank) >0:
            answer=messagebox.askquestion(title='Attention please',
            message='This will delete all unsaved images\n, are you still want to import another image?')
        if answer == 'no':
            return
        elif answer == 'yes':
            self.init_imgtank()
            self.init_img
            unlabel_image_path = askdirectory(title='Select the unlabeled images directory')
            if unlabel_image_path == '':
                return  
            imgname_list = glob.glob(os.path.join(unlabel_image_path, '*.jpg'))
            for i_name in imgname_list:
                self.img_tank.append(Image.open(i_name))
            
            self.unlabelimg_imported = True
            # show the first image
            self.transfer_to_img(1)
            for _ in range(len(self.img_tank)):
                self.img_label.append([None])
            self.change_browser()
            success_info = ' %d unlabel images has been imported.'%(len(self.img_tank))
            messagebox.showinfo(title='information',message=success_info)



    def set_windowsize_func(self):
        '''
        Setting the size of sliding window.
        '''
        if not self.wait:
            if not self.src_imported:
                messagebox.showwarning(title='warning',message='Please import the source image first')
                return            
            self.wait = True
            set_window = window_size_setting.window_size_setting(self)
            self.window.wait_window(set_window)
            self.wait = False
    
    def set_search_func(self):
        '''
        Setting the parameters for selective search algorithm.
        '''
        if not self.wait:
            if not self.src_imported:
                messagebox.showwarning(title='warning',message='Please import the source image first')
                return            
            self.wait = True
            set_window = selectivesearch_setting.selectivesearch_setting(self)
            self.window.wait_window(set_window)
            self.wait = False           
    
    def save_func(self):
        '''
        Save the labeled images into choosed file.
        '''
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.wait = True
            # return if the imgtanke is empty
            if not self.img_tank:
                messagebox.showwarning(title='warning',message='The image tank is empty')
                self.init_imgtank()
                self.wait = False
                return
            
            # choose an work_dir if the value of it is None
            if self.work_dir is None:
                workdir = askdirectory()
                if workdir == '':
                    return
                self.work_dir = workdir

            save_path = self.work_dir + '\\labeledImages'
            label = list(range(0,4))
            # create a flag list to mark which imges are saved
            Saved =[]
            for j in range(0,len(self.img_tank)):
                Saved.append(False)

            # save the labeled img in to the folder named by its label
            for i in label:
                tispath = save_path+'\\%d'%i
                self.mkdir(tispath)
                for j in range(0,len(self.img_tank)):
                    if self.img_label[j][0] == i:
                        filenum = len(os.listdir(tispath))
                        save_name = tispath + '\\ %d.jpg' %(filenum+1)
                        img = self.img_tank[j]
                        img.save(save_name)
                        Saved[j] = True
            # save calibrated images
            if not not self.index_calibrated_img:
                for i,j in zip(self.calibrated_img_before,self.calibrated_img_after):
                    path_before = self.work_dir + '\\calibratedImages_before'
                    path_after = self.work_dir + '\\calibratedImages_after'
                    self.mkdir(path_before)
                    self.mkdir(path_after)
                    filenum_before = len(os.listdir(path_before))
                    filenum_after = len(os.listdir(path_after))
                    save_name_before = path_before + '\\ %d.jpg' %(filenum_before+1)
                    save_name_after = path_after + '\\ %d.jpg' %(filenum_after+1)
                    i.save(save_name_before)
                    j.save(save_name_after)
            # delete saved calibration
  

                calibrate_BBpath = self.work_dir + '\\calibratedBoundingbox'
                self.mkdir(calibrate_BBpath)
                f = open(calibrate_BBpath+'\\before.txt', 'w')
                for i in self.calibrated_boundingbox_before:
                    for j in i:
                        f.write('%d '%j)
                    f.write('\n')
                f.close()
                f = open(calibrate_BBpath+'\\after.txt', 'w')
                for i in self.calibrated_boundingbox_after:
                    for j in i:
                        f.write('%d '%j)
                    f.write('\n')
                f.close()   
                
                self.calibrated_img_before = []
                self.calibrated_img_after = [] 
                self.calibrated_boundingbox_before = []
                self.calibrated_boundingbox_after = []
                self.index_calibrated_img = []                   
            # delete saved images
            new_img_tank = []
            new_label_tank =[]

            for i in range(0,len(self.img_tank)):
                if not Saved[i]:
                    new_img_tank.append(self.img_tank[i])
                    new_label_tank.append(self.img_label[i])
                        
            # assign unsaved imgs to the img tank
            self.img_tank = new_img_tank
            self.img_label = new_label_tank


            if not not new_img_tank:
                self.change_browser()
                self.change_calibrated_browser()
                self.transfer_to_img(1)
            else: 
                self.init_img()
                

            success_info = 'The images has been saved successfully to \n'+save_path
            messagebox.showinfo(title='information',message=success_info)
            self.saved = True
            self.wait = False

    def save_unlabel_img(self):
        '''
        Save the unlabeled images into the unlabeled file.
        '''
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.wait = True
            # return if the imgtanke is empty
            if not self.img_tank:
                messagebox.showwarning(title='warning',message='The image tank is empty')
                self.init_imgtank()
                self.wait = False
                return
            else:
                answer = messagebox.askquestion(title='Attention please',
                message='This will delete all unsaved labels \n, are you still want to continue?')
                if answer == 'no':
                    self.wait = False
                    return
                elif answer == 'yes':
                    # choose an work_dir if the value of it is None
                    if self.work_dir is None:
                        self.work_dir = askdirectory()
                    save_path = self.work_dir + '\\UnlabeledImages'
                    self.mkdir(save_path)
                    for j in range(0,len(self.img_tank)):
                        filenum = len(os.listdir(save_path))
                        save_name = save_path + '\\ %d.jpg' %(filenum+1)
                        img = self.img_tank[j]
                        img.save(save_name)                    
                    self.init_img()




    ### functions for buttons ###
    def select_BBalgorithm(self):
        if self.boundingbox_algorithm.get() == 1:
            self.cut_button.config(text='Generate bounding boxes\n (Sliding window algorithm)')
        elif self.boundingbox_algorithm.get() == 2:
            self.cut_button.config(text='Generate bounding boxes\n (Selective search algorithm)')
    
    def generate_BB(self):
        # check if the source image exist
        if not self.src_imported:
            messagebox.showwarning(title='warning',message='No source image available')
            return

        if self.boundingbox_algorithm.get() == 1:
            self.cut_img_slidingwindow()
        elif self.boundingbox_algorithm.get() == 2:
            self.cut_img_selectivesearch()
        else:                        
            messagebox.showwarning(title='warning',message='Please Select the bounding box generation algorithm')


    def cut_img_slidingwindow(self):
        '''
        cutting the source_img in the source into numbers of subimages
        and put them into the img_tank (employ sliding window algorithm)
        '''
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        else:
            self.init_imgtank()
            img_width = self.source_img.width
            img_height = self.source_img.height
        
            # sliding window algorithm
            for wp in range(0,img_width-self.window_size[0],self.stride):
                for hp in range(0,img_height-self.window_size[1],self.stride):
                    self.boundingbox_tank.append([wp,hp,wp+self.window_size[0],hp+self.window_size[1]])
                    cropImg = self.source_img.crop((wp,hp,wp+self.window_size[0],hp+self.window_size[1]))
                    self.img_tank.append(cropImg)
            
            # show the first image
            self.transfer_to_img(1)
            for _ in range(len(self.img_tank)):
                self.img_label.append([None])
            self.change_browser()
            success_info = 'The source image has been cut successfully into %d images.'%(len(self.img_tank))
            messagebox.showinfo(title='information',message=success_info)

    
    def cut_img_selectivesearch(self):
        '''
        cutting the source_img in the source into numbers of subimages
        and put them into the img_tank (employ selctivesearch algorithm).
        ''' 
        if self.wait:
            return

        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')    
        else:
            self.init_imgtank()
            self.wait = True
            # transfer the bundingbox_tank to an temporary tank to prevent the result from last cutting to intervene the judgement
            temp_boundingbox_tank = self.boundingbox_tank
            self.boundingbox_tank = []
            # ### run the selective search ###
            Search_window = selective_search_window.selective_search_window(self)
            self.window.wait_window(Search_window)
            
            if not self.boundingbox_tank: #if no value is catched (user exit directly the window)
                self.boundingbox_tank = temp_boundingbox_tank # reset the boundingbox tank
                temp_boundingbox_tank = []
                self.wait = False
                success_info = ' Found %d images from the source image.'%(len(self.img_tank))
                messagebox.showinfo(title='information',message=success_info)  
                return
            else:
                temp_boundingbox_tank = []
                for i in self.boundingbox_tank:
                    cropImg = self.source_img.crop((i[0],i[1],i[2],i[3]))                    
                    self.img_tank.append(cropImg)
                # show the first image
                self.transfer_to_img(1)
                for _ in range(len(self.img_tank)):
                    self.img_label.append([None])
                self.change_browser()
                success_info = ' Found %d images from the source image.'%(len(self.img_tank))
                messagebox.showinfo(title='information',message=success_info)   
                self.window.update()  
                self.wait = False

    def transfer_button_func (self):
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        else:
            try:
                target = self.image_browser.get(self.image_browser.curselection())
            except:
                messagebox.showwarning(title='warning',message='Please select an image')
            # find the first N number
            mode = re.compile(r'\d+')
            target = mode.findall(target)[0]
            target = int(target)
            self.transfer_to_img(target)

    def delete_button_func (self):
        
        def delete(li, index):# defining an delete function
            li = li[:index] + li[index+1:]
            return li

        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        else:
            try:
                target = self.calibrated_image_browser.get(self.calibrated_image_browser.curselection())
            except:
                messagebox.showwarning(title='warning',message='Please select an image')
            # find the first N number
            mode = re.compile(r'\d+')
            target = mode.findall(target)[0]
            target = int(target)

            self.calibrated_img_before = delete(self.calibrated_img_before,target-1)
            self.calibrated_img_after = delete(self.calibrated_img_after,target-1)
            self.calibrated_boundingbox_before = delete(self.calibrated_boundingbox_before,target-1)
            self.calibrated_boundingbox_after = delete(self.calibrated_boundingbox_after,target-1)
            self.index_calibrated_img = delete(self.index_calibrated_img,target-1)
            self.change_calibrated_browser()


            
        
    def previous_button_func(self):
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            target = self.img_pointer-1
            self.transfer_to_img(target)
    
    def next_button_func(self):
        if self.wait:
            return

        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            target = self.img_pointer+1
            self.transfer_to_img(target)
    
    def calibrate_button_func(self):
        if self.wait:
            return
        
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.src_imported and self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Can only revise image when the source image exist')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        elif self.img_pointer in self.index_calibrated_img:
            messagebox.showwarning(title='warning',message='This image has already been calibrated')
        else:
            self.wait = True
            calibrate_window = imagecalibration_window.imagecalibration_window(self)
            self.window.wait_window(calibrate_window)
            self.wait = False
            self.transfer_to_img(self.img_pointer)
            self.change_calibrated_browser()


    

    
    def label_as_0(self):
        if self.wait:
            return

        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.img_label[self.img_pointer-1][0]=0
            self.change_browser()
            self.next_button_func()

    def label_as_1(self):
        if self.wait:
            return

        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.img_label[self.img_pointer-1][0]=1
            self.change_browser()
            self.next_button_func()
    def label_as_2(self):
        if self.wait:
            return
            
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.img_label[self.img_pointer-1][0]=2
            self.change_browser()
            # self.next_button_func()

    def label_as_3(self):
        if self.wait:
            return
            
        if not self.src_imported and not self.unlabelimg_imported:
            messagebox.showwarning(title='warning',message='Please import some image first')
        elif not self.img_tank:
            messagebox.showwarning(title='warning',message='Please cut the image')
        else:
            self.img_label[self.img_pointer-1][0]=3
            self.change_browser()
            # self.next_button_func()

    ### other functons ###
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

