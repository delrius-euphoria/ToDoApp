import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pyglet 
from widgets import ToolTip
import pygame
from datetime import datetime
import sqlite3

pyglet.font.add_file('fonts/coolvetica compressed rg.ttf') # Add the task font
pygame.mixer.init() # Init pygame mixer
lst = [pygame.mixer.Sound('sounds/bell.ogg'),pygame.mixer.Sound('sounds/woosh.ogg')] # List with all the necessary music
tool_tip = 'You wil be able type more about your task here soon. As of now\nThis tasks is supposed to be completed on:'
text = '''Enter the name of your task here and choose the deadline below(today, by default).
Either press the button or the return key on your keyboard to add to the list.
The plus circle icon depics the completion of the task and use the dustbin icon to delete tasks.
Once you are done with the tasks, just close the app and open it whenever you want to see your progress.
Also keep in mind, once tasks are deleted and app is closed, there is no getting the same task back.'''

class Tasks(tk.Frame):
    def __init__(self,root, text: str,tooltip_text=tool_tip,d_date=datetime.now().strftime('%Y-%m-%d'),ticked=False, **kwargs):

        tk.Frame.__init__(self, root, **kwargs)

        self.parent = root
        self.text = text
        self.ticked = ticked
        self.count = 0
        self.d_date = d_date
        self.sc_h,self.sc_w = self.parent.winfo_screenheight(),self.parent.winfo_screenwidth()
        cnv_h,cnv_w = self.sc_h/21.6,self.sc_w/3.84

        self.canvas = tk.Canvas(self, bg='white', height=cnv_h, width=cnv_w) #500x50
        self.canvas.pack(fill='both', expand=1)

        self.canvas.create_text(cnv_w/2, cnv_h/2, text=self.text,
                                font=('coolvetica compressed rg',30), tag='text') #250,25

        tick_img_res_h,tick_img_res_w = int(self.sc_w/76.8),int(self.sc_h/43.2) #25,25
        dust_img_res_h,dust_img_res_w = int(self.sc_w/54.85), int(self.sc_h/30.85) #35,35
        
        self.img = ImageTk.PhotoImage(Image.open(
            'images/unchecked3.png').resize((tick_img_res_w,tick_img_res_h), Image.ANTIALIAS)) #25,25
        self.img1 = ImageTk.PhotoImage(Image.open(
            'images/checked3.png').resize((tick_img_res_w,tick_img_res_h), Image.ANTIALIAS)) #25,25
        self.img2 = ImageTk.PhotoImage(Image.open(
            'images/hover.png').resize((tick_img_res_w,tick_img_res_h), Image.ANTIALIAS)) #25,25
        self.img3 = ImageTk.PhotoImage(Image.open(
            'images/dustbin.png').resize((dust_img_res_w,dust_img_res_h), Image.ANTIALIAS)) #35,35
        self.img4 = ImageTk.PhotoImage(Image.open(
            'images/dustbinhover.png').resize((dust_img_res_w,dust_img_res_h), Image.ANTIALIAS)) #35,35

        self.canvas.create_image(
            cnv_w/5, cnv_h/2, image=self.img, anchor='center', tag='check') #100,25

        self.canvas.tag_bind(
            'check', '<Button-1>', lambda event=None: self.change(self.count, self.ticked))
        self.canvas.tag_bind('check', '<Enter>',
                             lambda event=None: self.enter())
        self.canvas.tag_bind('check', '<Leave>',
                             lambda event=None: self.leave())

        self.canvas.create_image(
            cnv_w/1.11, cnv_h/2, image=self.img3, anchor='center', tag='dustbin') #450,25
        self.canvas.tag_bind('dustbin', '<Button-1>', self.ridoff)
        self.canvas.tag_bind('dustbin', '<Enter>',
                             lambda event=None: self.enter1())
        self.canvas.tag_bind('dustbin', '<Leave>',
                             lambda event=None: self.leave1())

        if self.ticked:
            self.canvas.itemconfig('check', image=self.img1)
        else:
            self.canvas.itemconfig('check', image=self.img)

        self.tool = ToolTip(self.canvas,text=f'{tooltip_text} {self.d_date}',bg='white')
        # self.parent.bind('<Button-1>', self.check)
        self.canvas.bind('<Double-Button-1>', self.check)

        if len(self.text) > 20:

            self.mod_text = self.text[:15] + '\n' + self.text[15:]
            self.canvas.itemconfig('text', text=self.mod_text)
            self.canvas.config(height=cnv_w/5) #100
            self.canvas.coords('text', cnv_w/2, cnv_h) #250,50
            self.canvas.coords('check', cnv_w/5, cnv_h) #100,50
            self.canvas.coords('dustbin', cnv_w/1.11, cnv_h) #450,50
            if len(self.text) > 40:
                self.mod_text = self.text[:30] + '...'
                self.canvas.itemconfig('text',text=self.mod_text)
    
    def change(self, count, ticked):
        # global ticked, count
        # self.canvas.itemconfig('check', image=self.img)
        if self.ticked:
            count = 1
        if count == 0:
            if not self.ticked:
                ticked = True
        else:
            if count % 2 == 0:
                ticked = True
            else:
                ticked = False

        if ticked == True:
            self.canvas.itemconfig('check', image=self.img1)
            lst[0].play()
        else:
            self.canvas.itemconfig('check', image=self.img)
        
        count += 1
        self.canvas.tag_unbind('check', '<Button-1>')
        self.canvas.tag_bind('check', '<Button-1>',
                             lambda event=None: self.change(count, ticked))
        self.ticked = ticked

    def task_status(self):
        return self.ticked

    def enter(self):
        if not self.ticked:
            self.canvas.itemconfig('check', image=self.img2)

    def enter1(self):
        self.canvas.itemconfig('dustbin', image=self.img4)

    def leave(self):
        if self.ticked:
            self.canvas.itemconfig('check', image=self.img1)
        else:
            self.canvas.itemconfig('check', image=self.img)

    def leave1(self):
        self.canvas.itemconfig('dustbin', image=self.img3)

    def check(self, event):
        return self.ticked

    def ridoff(self, event):
        lst[1].play()
        wid = self.parent.winfo_containing(
            event.x_root, event.y_root).winfo_parent()
        self.destroy()
        self.tool.remove()
        return wid

    def get_text(self):
        return self.text

    def get_date(self):
        return self.d_date

class PrevTasks(tk.Frame):
    def __init__(self,root, text: str,func=None,d_date=datetime.now().strftime('%Y-%m-%d'), **kwargs):

        tk.Frame.__init__(self, root, **kwargs)

        self.parent = root
        self.text = text
        self.func = func
        self.sc_h,self.sc_w = self.parent.winfo_screenheight(),self.parent.winfo_screenwidth()
        cnv_h,cnv_w = self.sc_h/21.6,self.sc_w/3.84

        self.canvas = tk.Canvas(self, bg='white', height=cnv_h, width=cnv_w)
        self.canvas.pack(fill='both', expand=1)

        self.canvas.create_text(cnv_w/2, cnv_h/2, text=self.text,
                                font=('coolvetica compressed rg',30), tag='text')

        tick_img_res_h,tick_img_res_w = int(self.sc_w/76.8),int(self.sc_h/43.2)


        self.img = ImageTk.PhotoImage(Image.open(
            'images/plus_unchecked.png').resize((tick_img_res_w, tick_img_res_h), Image.ANTIALIAS))
        self.img1 = ImageTk.PhotoImage(Image.open(
            'images/plus_checked.png').resize((tick_img_res_w, tick_img_res_h), Image.ANTIALIAS))

        self.canvas.create_image(
            cnv_w/1.11,cnv_h/2, image=self.img, anchor='center', tag='check')

        self.canvas.tag_bind(
            'check', '<Button-1>', lambda event=None: self.click())
        self.canvas.tag_bind('check', '<Enter>',
                             lambda event=None: self.canvas.itemconfig('check',image=self.img1))
        self.canvas.tag_bind('check', '<Leave>',
                             lambda event=None: self.canvas.itemconfig('check',image=self.img))

        if len(self.text) > 20:
            self.mod_text = self.text[:15] + '\n' + self.text[15:]
            self.canvas.itemconfig('text', text=self.mod_text)
            self.canvas.config(height=cnv_w/5)
            self.canvas.coords('text', cnv_w/2, cnv_h)
            self.canvas.coords('check', cnv_w/1.11, cnv_h)
            if len(self.text) > 40:
                self.mod_text = self.text[:30] + '...'
                self.canvas.itemconfig('text',text=self.mod_text)
    
    def click(self,*args):
        lst[1].play()
        text = self.text
        try:
            self.func()
        except:
            pass
        self.destroy()
        return text

    def get_text(self):
        return self.text

def create_table(con):
    c = con.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks(
        `Tasks` text,
        `Date` text,
        `completed` integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS first_time(
        `date` text,
        `opened` integer default 1)''')
    
