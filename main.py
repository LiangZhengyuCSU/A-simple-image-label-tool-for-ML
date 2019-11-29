# -*- coding:utf-8 -*-  
#----------------------------------------------------------------------------------#  
# Name:       A simple image labeling tool-launch_pad                              #
# Coder:      Zhengyu Liang at Central South Univ.                                 #
# Date:       May, 11, 2018                                                        #
# Git:        https://github.com/LiangZhengyuCSU/A-simple-image-label-tool-for-ML  #    
#----------------------------------------------------------------------------------# 
# import imagelabeler
import imagelabeler_semiauto
import tkinter as tk

# import pkgs
# launch the window


class ToolSelector():  
    def __init__(self):
        '''
        Constructed function, initiate  arguments.
        '''      
        # UI setup
        self.window = tk.Tk()
        self.labeler = []   
        self.window.title("Select a labeling tool")
        self.window.resizable(False,False)
        # # the Manual method frame
        # self.Manualframe = tk.LabelFrame(self.window, text="Adding labels to boundingbox Manually")
        # self.Manualframe.grid(row=0,column=0,padx=1,pady=1)
        # # the launch_Manual button
        # self.launch_Manual_button = tk.Button(self.Manualframe,command=self.launch_Manual,
        # text='Manual method',width=5,height=1,font=('Times New Roman',12),bg='white',
        # compound = 'center',state='normal',relief='raised')
        # self.launch_Manual_button.pack(fill='x')
        # the seimiauto method frame
        self.Seimiautoframe = tk.LabelFrame(self.window, text="Adding labels to boundingbox semi-automaticlly")
        self.Seimiautoframe.grid(row=1,column=0,padx=1,pady=1)
        # the launch_Seimiauto button
        self.launch_Seimiauto_button = tk.Button(self.Seimiautoframe,command=self.launch_Seimiauto,
        text='Semi-automatic method',width=5,height=1,font=('Times New Roman',12),bg='white',
        compound = 'center',state='normal',relief='raised')
        self.launch_Seimiauto_button.pack(fill='x')
        self.window.mainloop()   
    
    # def launch_Manual(self):
    #     self.window.destroy()
    #     self.labeler= imagelabeler.imagelabeler()
    
    def launch_Seimiauto(self):
        self.window.destroy()
        self.labeler= imagelabeler_semiauto.imagelabeler_semiauto()


if __name__ == '__main__':    
    ToolSelector() 