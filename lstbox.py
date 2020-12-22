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
    
        # print(len(text))
        self.canvas = tk.Canvas(self, bg='white', height=50, width=500)
        self.canvas.pack(fill='both', expand=1)

        self.canvas.create_text(250, 25, text=self.text,
                                font=('coolvetica compressed rg',30), tag='text')

        self.img = ImageTk.PhotoImage(Image.open(
            'images/unchecked3.png').resize((25, 25), Image.ANTIALIAS))
        self.img1 = ImageTk.PhotoImage(Image.open(
            'images/checked3.png').resize((25, 25), Image.ANTIALIAS))
        self.img2 = ImageTk.PhotoImage(Image.open(
            'images/hover.png').resize((25, 25), Image.ANTIALIAS))
        self.img3 = ImageTk.PhotoImage(Image.open(
            'images/dustbin.png').resize((35, 35), Image.ANTIALIAS))
        self.img4 = ImageTk.PhotoImage(Image.open(
            'images/dustbinhover.png').resize((35, 35), Image.ANTIALIAS))

        self.canvas.create_image(
            100, 25, image=self.img, anchor='center', tag='check')

        self.canvas.tag_bind(
            'check', '<Button-1>', lambda event=None: self.change(self.count, self.ticked))
        self.canvas.tag_bind('check', '<Enter>',
                             lambda event=None: self.enter())
        self.canvas.tag_bind('check', '<Leave>',
                             lambda event=None: self.leave())

        self.canvas.create_image(
            450, 25, image=self.img3, anchor='center', tag='dustbin')
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
            # print(len(self.text))
            self.mod_text = self.text[:15] + '\n' + self.text[15:]
            self.canvas.itemconfig('text', text=self.mod_text)
            self.canvas.config(height=100)
            self.canvas.coords('text', 250, 50)
            self.canvas.coords('check', 100, 50)
            self.canvas.coords('dustbin', 450, 50)
            if len(self.text) > 40:
                print(len(self.text))
                self.mod_text = self.text[:30] + '...'
                self.canvas.itemconfig('text',text=self.mod_text)
    
    def change(self, count, ticked):
        # global ticked, count
        if count == 0:
            ticked = True
        self.canvas.itemconfig('check', image=self.img)
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
        # print('Done' if self.ticked else 'Pending')

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

        # print(len(text))
        self.canvas = tk.Canvas(self, bg='white', height=50, width=500)
        self.canvas.pack(fill='both', expand=1)

        self.canvas.create_text(250, 25, text=self.text,
                                font=('coolvetica compressed rg',30), tag='text')

        self.img = ImageTk.PhotoImage(Image.open(
            'images/plus_unchecked.png').resize((25, 25), Image.ANTIALIAS))
        self.img1 = ImageTk.PhotoImage(Image.open(
            'images/plus_checked.png').resize((25, 25), Image.ANTIALIAS))

        self.canvas.create_image(
            450,25, image=self.img, anchor='center', tag='check')

        self.canvas.tag_bind(
            'check', '<Button-1>', lambda event=None: self.click())
        self.canvas.tag_bind('check', '<Enter>',
                             lambda event=None: self.canvas.itemconfig('check',image=self.img1))
        self.canvas.tag_bind('check', '<Leave>',
                             lambda event=None: self.canvas.itemconfig('check',image=self.img))

        if len(self.text) > 20:
            # print(len(self.text))
            self.mod_text = self.text[:15] + '\n' + self.text[15:]
            self.canvas.itemconfig('text', text=self.mod_text)
            self.canvas.config(height=100)
            self.canvas.coords('text', 250, 50)
            self.canvas.coords('check', 450, 50)
            if len(self.text) > 40:
                print(len(self.text))
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
