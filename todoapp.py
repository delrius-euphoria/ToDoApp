# Main imports
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
from lstbox import Tasks, PrevTasks, text, create_table
from widgets import PlaceholderEntry, ToolTip
from PIL import Image, ImageTk, ImageFilter
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import babel.numbers
import sqlite3
import win10toast
import webbrowser
import pyglet

# Initialize the window and basic settings
root = tk.Tk()
root.iconbitmap('images/logo.ico')
root.title('ToDoApp')
root['bg'] = 'white'
root.resizable(0,0)
pyglet.font.add_file('fonts/coolvetica compressed rg.ttf')
pyglet.font.add_file('fonts/kenyan coffee rg.ttf')
pyglet.font.add_file('fonts/Roboto-Black.ttf')
task_header = ('coolvetica compressed rg',35)
font_time = ('Roboto Black',30)
font_date = ('Roboto Black',15)
font_header = ('kenyan coffee rg',30)
con = sqlite3.connect('data/tasks.db')
toast = win10toast.ToastNotifier()
sc_h,sc_w = root.winfo_screenheight(),root.winfo_screenwidth()
tasks = []
prev_tasks = []
version = 'Beta 2.00'

# Function for adding tasks
def default(event=None):
    if text_entry.length() <= 25 and text_entry.acquire() != 'None':
        # bg_canvas.config(bg='#f0f0f0')
        scroll_frame.config(bg='#f0f0f0')
        tasks.append(Tasks(scroll_frame,text=text_entry.acquire(),d_date=date_picker.get()))
        tasks[-1].pack(pady=10)
        text_entry.remove(0,'end')
    else:
        messagebox.showerror('Enter proper details',f'Make sure to enter the task title below 25 characters\nTotal characters now: {text_entry.length()}')

# Function to show day and date
def timer():
    root.after(499,timer) #repeating the function 
    time = datetime.now().strftime('%I:%M:%S %p') #setting the format
    date = datetime.now().strftime('%A, %d %B, %Y') #setting the format
    twent3 = datetime.strptime(f"{datetime.now().strftime('%Y/%m/%d')} 23:00:00",'%Y/%m/%d %H:%M:%S')
    now = datetime.strptime(datetime.now().strftime('%Y/%m/%d %H:%M:%S'),'%Y/%m/%d %H:%M:%S') #setting the format
    date_time_canvas.itemconfig('time',text=time) #changing the text of the widget 
    date_time_canvas.itemconfig('date',text=date) #changing the text of the widget 
    if now == twent3:
        toast.show_toast('The To Do App','Have you checked your progress today?',threaded=True,duration=None,callback_on_click=progress)

# Function to change the bg of image
def change_image(event=None):
    try:
        path = filedialog.askopenfilename(title='Choose an image',filetypes=[('JPEG image','*.jpg'),('PNG image','*.png')])
        img = ImageTk.PhotoImage(Image.open(path).resize((bg_img_res_w,bg_img_res_h),Image.ANTIALIAS).filter(ImageFilter.GaussianBlur(2)))
        date_time_canvas.itemconfig('bg',image=img)
        date_time_canvas.image = img
    except AttributeError:
        pass

# Function to save the tasks
def save():
    if messagebox.askyesno('Are you sure?','Are you sure you want to exit?'):
            
        destroyed = False
        c = con.cursor()
        objs = list(scroll_frame.children.values())
        objs_set = set(scroll_frame.children.values())
        missing = obj_set.difference(objs_set)

        if len(objs) == 0:
            root.destroy()
            destroyed = True
        
        else:    
            for obj in objs:
                c.execute('SELECT * FROM tasks where `Tasks`=? and `Date`=?',(obj.get_text(),obj.get_date()))
                if c.fetchall() == []:  
                    c.execute('INSERT INTO tasks VALUES(?,?,?)',(obj.get_text(),obj.get_date(),int(obj.task_status())))
                    con.commit()
                else:
                    c.execute('UPDATE tasks SET `completed`=? WHERE `Tasks`=? and `Date`=?',(int(obj.task_status()),obj.get_text(),obj.get_date()))
                    con.commit()
            
        if missing:
            for ms_obj in missing:
                c.execute('DELETE FROM tasks where `Tasks`=? and `Date`=? and `completed`=?',(ms_obj.get_text(),ms_obj.get_date(),int(ms_obj.task_status())))
                con.commit()

        if not destroyed:
            con.close()
            root.destroy()

# Function to add the pending tasks 
def add_prev_tasks(title,d_date):
    c = con.cursor()
    c.execute('DELETE FROM tasks where `Tasks`=? and `Date`=? and `completed`=?',(title,d_date,0))
    con.commit()
    tasks.append(Tasks(scroll_frame,text=title,d_date=date_picker.get()))
    tasks[-1].pack(pady=10)

# Function to fetch data to add tasks
def populate():
    global obj_set

    c = con.cursor()
    cc = con.cursor()

    today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d')
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    
    cc.execute(f"SELECT * FROM tasks WHERE date(`Date`)>=date(?);",(today.strftime('%Y-%m-%d'),))
    
    data = cc.fetchall()
    for title,date,status in data:
        tasks.append(Tasks(scroll_frame,text=title,d_date=date,ticked=bool(status)))
        tasks[-1].pack(pady=10)
    obj_set = set(scroll_frame.children.values())

    c.execute('SELECT * FROM tasks where date(`Date`)<=? and `completed`=?',(yesterday,0))
    for title,date,_ in c.fetchall():
        prev_tasks.append(PrevTasks(scroll_frame_prev,text=title,func=lambda title=title,date=date:add_prev_tasks(title,date)))
        prev_tasks[-1].pack(pady=10)

# Function to display daily progress
def progress():
    prog = tk.Toplevel()
    prog['bg'] = 'white'
    prog.iconbitmap('images/logo.ico')
    c = con.cursor()
    date = datetime.today().strftime('%Y-%m-%d')
    c.execute('SELECT `Tasks` FROM tasks WHERE date(`Date`) >= date(?) and `completed`=1',(date,))
    tk.Label(prog,text='Todays completed tasks:',font=font_header,bg='white').pack(padx=10,pady=10)
    data = c.fetchall()
    if data:
        for idx,title in enumerate(data,start=1):
            tk.Label(prog,text=f'{idx}. {title[0]}',font=task_header,bg='white').pack(padx=10,pady=5)
    else:
        tk.Label(prog,text='You might not have done something great today, but that\ndoes not stop you from doing something great tomorrow!',font=font_date).pack()
        
    tk.Label(prog,text='Tomorrow will be another great day!',font=font_date,bg='white').pack(padx=10,pady=10)

# Function for popup menu
def popup(event):
    try:
        menu.tk_popup(event.x_root,event.y_root)
    finally:
        menu.grab_release()

# Function to display about section
def about():
    # Defining Urls
    url = "https://nihaalnz.herokuapp.com"
    url_2 = "https://github.com/nihaalnz/ToDoApp"

    def openweb():
        webbrowser.open(url, new=1)

    def openweb_2():
        webbrowser.open(url_2, new=1)

    # Define about section
    about = tk.Toplevel(root)
    about.resizable(False,False)
    about.title('About')
    about.focus_force()
    about.iconbitmap('images/about.ico')
    about.geometry('300x300')
    # Making frames
    frame = tk.LabelFrame(about, text='About this program:', padx=5, pady=5)
    # Making frame items
    l_name = tk.Label(frame, text='Created by Nihaal Nz')
    l_ver = tk.Label(frame, text=f'Ver: {version}')
    l_lic = tk.Label(frame, text='Licensed under MIT')
    btn_sup = ttk.Button(frame, text='Website', command=openweb)
    btn_cod = ttk.Button(frame, text='Source Code!', command=openweb_2)
    btn_cls = ttk.Button(frame, text='Close', command=about.destroy)
    #Placing in screen
    frame.grid(row=0, column=0, padx=70, pady=40)
    l_name.grid(row=0, column=0)
    l_ver.grid(row=1, column=0)
    l_lic.grid(row=2, column=0)
    btn_sup.grid(row=3, columnspan=2, sticky='ew', pady=(5, 0))
    btn_cod.grid(row=4, columnspan=2, sticky='ew', pady=5)
    btn_cls.grid(row=5, columnspan=2, sticky='ew')

# Function to run for first time users
def first_time():
    now = datetime.strptime(datetime.now().strftime('%Y/%m/%d %H:%M:%S'),'%Y/%m/%d %H:%M:%S') #setting the format
    c = con.cursor()
    c.execute('SELECT * FROM first_time;')
    data = c.fetchall()
    if data == []:
        c.execute('INSERT INTO first_time(`date`) VALUES(?)',(now,))
        con.commit()
        changelog = tk.Toplevel()
        changelog.iconbitmap('images/changes.ico')
        changelog.resizable(0,0)
        changelog.title('Changelog')
        changes = scrolledtext.ScrolledText(master=changelog,wrap='word')
        changes.pack()
        ttk.Button(changelog,text='Exit',command=changelog.destroy).pack(fill='x')
        changelog.attributes('-topmost',1)
        with open('changelog.txt','r') as f:
            changes.insert('1.0',f.read())
            changes.config(state='disabled')
        

# Tasks frame
main_section = tk.Frame(root,bg='white')
main_section.grid(row=0,column=1)

pseudo_frame = tk.Frame(main_section)
pseudo_frame.grid(row=3,column=0,columnspan=2)

bg_canvas = tk.Canvas(pseudo_frame,bg='white',highlightthickness=0,height=sc_h/2.16)
bg_canvas.pack(side='left', fill='both', expand=1)

scrollbar = ttk.Scrollbar(pseudo_frame,orient='vertical',command=bg_canvas.yview)
bg_canvas.config(yscrollcommand=scrollbar.set)

scroll_frame = tk.Frame(bg_canvas,bg='white')
scroll_frame.bind('<Configure>', lambda e: [bg_canvas.configure(scrollregion=bg_canvas.bbox("all")),scrollbar.pack(side='right',fill='y')])
bg_canvas.create_window(0,0,window=scroll_frame,anchor='n')

header_label = tk.Label(main_section,text='Add to the list',font=font_header,bg='white')
header_label.grid(row=0,column=0,columnspan=2)

text_entry = PlaceholderEntry(main_section,placeholder='Cover entire syllabus!..',font=(0,13)) 
text_entry.grid(row=1,column=0,pady=15,ipady=5,ipadx=5)

submit_button = ttk.Button(main_section,text='Add to your list',command=default) 
submit_button.grid(row=1,column=1,padx=10,ipady=5)

date_picker = DateEntry(main_section,year=int(datetime.now().strftime("%Y")),month=int(datetime.now().strftime("%m"))
                            ,day=int(datetime.now().strftime("%d")),date_pattern='Y-mm-dd',font=(0,12),justify='center'
                            ,mindate=datetime.now(),state='readonly',selectfg='red')
date_picker.grid(row=2,column=0,columnspan=2,pady=5,sticky='ew')

text_entry.bind('<Return>',default)


# Date and time Frame
date_time_frame = tk.Frame(root)
date_time_frame.grid(row=0,column=2,padx=sc_w/48,sticky='n')
date_cnv_h,date_cnv_w = sc_h/1.54,sc_w/4.8
date_time_canvas = tk.Canvas(date_time_frame,width=sc_w/4.8,height=sc_h/1.54,highlightthickness=0) #400x700
date_time_canvas.pack()

bg_img_res_h,bg_img_res_w = int(sc_w/2.56), int(sc_h/1.44) #750,750
cam1_img_res_h,cam1_img_res_w = int(sc_w/76.8),int(sc_h/43.2) #25,25
cam2_img_res_h,cam2_img_res_w = int(sc_w/54.85), int(sc_h/30.85) #35,35

bg = ImageTk.PhotoImage(Image.open('images/bg.jpg').rotate(180).resize((bg_img_res_w,bg_img_res_h),Image.ANTIALIAS).filter(ImageFilter.GaussianBlur(2)))
cam1 = ImageTk.PhotoImage(Image.open('images/defaultcam.png').resize((cam1_img_res_w,cam1_img_res_h),Image.ANTIALIAS))
cam2 = ImageTk.PhotoImage(Image.open('images/cam.png').resize((cam2_img_res_w,cam2_img_res_h),Image.ANTIALIAS))
date_time_canvas.create_image(date_cnv_w/2,date_cnv_h/2,image=bg,anchor='center',tag='bg') #200,350
date_time_canvas.create_text(date_cnv_w/2,date_cnv_h/2,tag='time',font=font_time,anchor='center') #200,350
date_time_canvas.create_text(date_cnv_w/2,date_cnv_h/1.75,tag='date',font=font_date,anchor='center') #200,400

date_time_canvas.create_image(date_cnv_w/1.11,date_cnv_h/1.06,image=cam1,anchor='center',tag='cam') #360,660
date_time_canvas.tag_raise('cam')
date_time_canvas.tag_bind('cam','<Enter>',lambda e:date_time_canvas.itemconfig('cam',image=cam2))
date_time_canvas.tag_bind('cam','<Leave>',lambda e:date_time_canvas.itemconfig('cam',image=cam1))
date_time_canvas.tag_bind('cam','<Button-1>',change_image)

# Previous tasks frame
previous_tasks = tk.Frame(root,bg='white')
previous_tasks.grid(row=0,column=0,sticky='n',padx=(0,sc_w/48))

pseudo_frame_prev = tk.Frame(previous_tasks)
pseudo_frame_prev.grid(row=1,column=0)

bg_canvas_prev = tk.Canvas(pseudo_frame_prev,bg='white',highlightthickness=0,height=sc_h/2.16)
bg_canvas_prev.pack(side='left', fill='both', expand=1)

scrollbar_prev = ttk.Scrollbar(pseudo_frame_prev,orient='vertical',command=bg_canvas_prev.yview)
bg_canvas_prev.config(yscrollcommand=scrollbar_prev.set)

scroll_frame_prev = tk.Frame(bg_canvas_prev,bg='white')
scroll_frame_prev.bind('<Configure>', lambda e: [bg_canvas_prev.configure(scrollregion=bg_canvas_prev.bbox("all")),scrollbar_prev.pack(side='right', fill='y')])
bg_canvas_prev.create_window(0,0,window=scroll_frame_prev,anchor='n')

previous_sec_header = tk.Label(previous_tasks,text='Pending tasks',font=font_header,bg='white')
previous_sec_header.grid(row=0,column=0,pady=10)


# Defining and adding menu and popup menu
my_menu =tk.Menu(root)
root.config(menu=my_menu)
file_menu = tk.Menu(my_menu,tearoff=0)
my_menu.add_cascade(label='Menu', menu=file_menu)
file_menu.add_command(label='Change image',command=change_image)
file_menu.add_command(label='Revert to default image',command=lambda: date_time_canvas.itemconfig('bg',image=bg))
file_menu.add_command(label='Change date-time text color to white',command=lambda: [date_time_canvas.itemconfig('date',fill='white'),
                                                            date_time_canvas.itemconfig('time',fill='white')])
file_menu.add_command(label='Revert to black date-time text color',command=lambda: [date_time_canvas.itemconfig('date',fill='black'),
                                                            date_time_canvas.itemconfig('time',fill='black')])
file_menu.add_separator()
file_menu.add_command(label='About', command=about)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=save)

menu = tk.Menu(root,tearoff=0)
menu.add_command(label='Change image',command=change_image)
menu.add_command(label='Revert to default image',command=lambda: date_time_canvas.itemconfig('bg',image=bg))
menu.add_command(label='Change date-time text color to white',command=lambda: [date_time_canvas.itemconfig('date',fill='white'),
                                                            date_time_canvas.itemconfig('time',fill='white')])
menu.add_command(label='Revert to black date-time text color',command=lambda: [date_time_canvas.itemconfig('date',fill='black'),
                                                            date_time_canvas.itemconfig('time',fill='black')])
menu.add_separator()
menu.add_command(label='Exit',command=save)
root.bind('<Button-3>',popup)

# Protocol to follow while closing window
root.wm_protocol('WM_DELETE_WINDOW',save)

# Defining progress and exit buttons
ttk.Button(root,text='Show progress',command=progress).grid(row=1,column=0,columnspan=3,sticky='ew',pady=(10,3))
ttk.Button(root,text='Exit',command=save).grid(row=2,column=0,columnspan=3,sticky='ew')

# Tooltip for the entry box
ToolTip(text_entry,text=text,bg='white')

# Functipn to fill the GUI
timer()
try:
    populate()
    
except sqlite3.OperationalError:
    create_table(con)
    populate()
try:
    first_time()
except sqlite3.OperationalError:
    create_table(con)
    first_time()

# GUI loop.
root.mainloop()