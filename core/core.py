import os
import sys
import cv2
import numpy as np
import threading
import time

from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer
from tkinter import Tk, Label, Button, PhotoImage, CENTER, VERTICAL, HORIZONTAL, Canvas, Scrollbar, CHORD,filedialog
from random import randint

class Gui:
    def __init__(self, MyClient):
        self.MyClient = MyClient
        self.path = MyClient.path
        self.data = MyClient.client_data
        self.root = Tk()

        self.current_rgb = [0, 255, 0]
        self.root["bg"] = self.hex_from_rgb((255,253,225))
        self.root.bind_all('<Enter>',self.on_enter)
        self.root.bind_all('<Leave>',self.on_leave)

        self.modes = {
            "preview":"enabled",
            "count":"1",
            "audio":"on"
        }
        self.chg=0
        self.n=None
        self.first=[True for i in range(len(self.data))]
        self.framelog = []
        self.c=""
        self.thread_start = False
        
        self.root.attributes('-fullscreen', True)
        self.root.bind("1", lambda event: self.togglewindowstate())
        self.root.bind("<Button-1>", self.callback)

        self.scr_height = self.root.winfo_screenheight()
        self.scr_width = self.root.winfo_screenwidth()
        self.thumbx = (self.scr_width-105)//2
        self.thumby = (self.thumbx*9)//16

        self.mainlogo = ImageTk.PhotoImage(Image.open('assets/logo.png'))
        self.logo_pic = ImageTk.PhotoImage(Image.open('assets/logo.png').resize((55,55)))
        self.folder_pic = ImageTk.PhotoImage(Image.open(f"assets/folder.png").resize((35,35)))
        self.fullscreen_pic = ImageTk.PhotoImage(Image.open(f"assets/fullscreen.png").resize((35,35)))
        self.close_pic = ImageTk.PhotoImage(Image.open(f"assets/close.png").resize((35,35)))
        self.up_arrow_pic = ImageTk.PhotoImage(Image.open(f"assets/up_arrow.png").resize((50,50)))
        self.frontpage_pic = ImageTk.PhotoImage(Image.open(f"assets/frontpage.png").resize((self.scr_width-20,self.scr_height)))
 
        self.loading_screen()
        
        widthread = threading.Thread(target=lambda:self.widgets())
        widthread.start()

        linethread = threading.Thread(target=lambda:self.drawline())
        self.canvas.after(1000, lambda:linethread.start())

        self.root.mainloop()

    def loading_screen(self):
        self.canvas = Canvas(
            self.root, width = self.scr_width,
            height = self.scr_height,
            relief='flat',highlightthickness=0
        )

        self.canvas.create_image(self.scr_width/2,self.scr_height/2,image=self.mainlogo,anchor="center")  
        self.canvas.grid(row=0,column=0,sticky="EW")

    def transition(self):
        self.canvas.grid_forget()
        self.canvas2.grid(row=0,column=0,sticky="EW")
        self.canvas.delete("line")
        self.canvas.delete("line2")
        self.canvas.configure(bg=self.hex_from_rgb((255,253,235)))

    def drawline(self):
        for i in range(-95,96,2):
            self.canvas.create_line(self.scr_width//2-95,self.scr_height//2+125,self.scr_width//2+i,self.scr_height//2+125,width=2,fill=self.hex_from_rgb((90,90,90)),tags=("line"))
            self.canvas.delete("line2")
            self.canvas.create_line(self.scr_width//2-95,self.scr_height//2+125,self.scr_width//2+i+1,self.scr_height//2+125,width=2,fill=self.hex_from_rgb((90,90,90)),tags=("line2"))
            self.canvas.delete("line")
            time.sleep(0.015)
        self.transition()

    def hex_from_rgb(self, rgb):
        return "#%02x%02x%02x" % rgb

    def togglewindowstate(self):
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
        else:
            self.root.attributes('-fullscreen', True)

    def switchprevmode(self, m):
        self.canvas2.delete('mode')
        t=self.modes.get(m)
        self.m = m
        self.canvas2.create_text(self.scr_width-200,60,anchor="nw",font=("Liberation Serif",8),text=f"hover mode: {t}",tags=("mode"))

    def preview(self, filepath,c):
        cap = cv2.VideoCapture(filepath)
        if self.first[c] == True:
            number = self.framelog[c]
            self.first[c] = False
        else:
            framesno = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start,end = framesno//10, framesno-framesno//8
            number = randint(start,end)

        fps = cap.get(cv2.CAP_PROP_FPS)
        if cap.isOpened() == False:
            print("error opening video file")
            return

        cap.set(cv2.CAP_PROP_POS_FRAMES, number)
        if self.modes["audio"]=="on":
            player = MediaPlayer(filename=filepath,ff_opts={'ss': float(number/fps)+1})
            audio_frame, val = player.get_frame()

        res=True
        while res==True:
            s1=time.time()
            res, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = ImageTk.PhotoImage(Image.fromarray(frame).resize((self.thumbx,self.thumby)))
            cv2.destroyAllWindows()

            self.thumbnail_images[c]["image"] = im
            self.thumbnail_images[c].photo = im
            self.thumbnail_images[c]["text"] = ""
            if self.thread_start == False:
                break
            s2=time.time()
            wait=(1/fps)-(s2-s1)
            try:
                time.sleep(wait)
            except:
                pass

    def on_enter(self,*h):
        if ".!label" in str(h[0].widget):
            n = h[0].widget
            n.config(bg="gold")
            self.n = n
            try:
                c = int(str(n)[7:])-1-self.chg
            except:
                c = self.chg
            self.c=c
            if self.modes["preview"]=="disabled":
                return
            l=[c]
            if self.modes["count"]!="1":
                if c%2==1:
                    c-=1
                if self.modes["count"]=="2":
                    l=[c,c+1]
                else:
                    l=[c,c+1,c+2,c+3]
                    if self.modes["count"]=="4" and c+3>len(self.data)-1:
                        l=[c-2,c-1,c,c+1]
            self.thread_start = True
            for i in l:
                if i in range(len(self.data)):
                    filepath=self.data[i]
                    function1 = threading.Thread(target=lambda:self.preview(filepath,i))
                    function1.start()

    def on_leave(self,*h):
        self.thread_start = False
        if self.n:
            self.n.config(bg="salmon")
        self.c=""

    def run_vlc(self, paths):
        print("Playing video(s)")
        path=self.path+"\\"+paths
        print(path)
        os.system(f"start vlc \"{path}\"")

    def textlabelmaker(self,x1,y1,x2,y2,color,tag):
        self.canvas2.create_arc(x1-12,y1,x1+11,y2-1,start=90,extent=180,fill=color,width=0,style=CHORD,outline="",tags=(tag))
        self.canvas2.create_arc(x2-12,y1,x2+11,y2-1,start=270,extent=180,fill=color,width=0,style=CHORD,outline="",tags=(tag))
        self.canvas2.create_rectangle(x1,y1,x2,y2,fill=color,width=0,outline=color,tags=(tag))

    def callback(self,event):
        x = self.canvas2.canvasx(event.x)
        y = self.canvas2.canvasy(event.y)
        
        if x>=self.scr_width-175 and x<=self.scr_width-30 and y>=7 and y<=27:
            if self.modes["preview"]=="enabled":
                self.modes["preview"]="disabled"
            else:
                self.modes["preview"]="enabled"
            self.canvas2.delete("preview")
            self.canvas2.create_text(self.scr_width-170,8,text=f"Preview Mode: {self.modes['preview']}",anchor="nw",font=("Liberation Serif",10),tags=("preview"))
        
            self.canvas2.delete("_count")
            self.canvas2.delete("_audio")

            clrs=["lime","green yellow"]
            if self.modes["preview"] == 'disabled':
                clrs=["grey","grey"]

            self.textlabelmaker(self.scr_width-95,29,self.scr_width-40,49,color=clrs[0],tag="_count")
            self.canvas2.create_text(self.scr_width-95,30,anchor="nw",font=("Liberation Serif",10),text=f"count:  {self.modes['count']}",tags=("count"))

            self.textlabelmaker(self.scr_width-95,51,self.scr_width-40,71,color=clrs[1],tag="_audio")
            self.canvas2.create_text(self.scr_width-95,52,anchor="nw",font=("Liberation Serif",10),text=f"audio: {self.modes['audio']}",tags=("audio"))

        elif x>=self.scr_width-105 and x<=self.scr_width-30 and y>=29 and y<=49:
            if self.modes["preview"]=="disabled":
                return
            if self.modes["count"]=="1":
                self.modes["count"]="2"
            elif self.modes["count"]=="2":
                self.modes["count"]="4"
            elif self.modes["count"]=="4":
                self.modes["count"]="1"
            self.canvas2.delete("count")
            self.canvas2.create_text(self.scr_width-95,30,anchor="nw",font=("Liberation Serif",10),text=f"count:  {self.modes['count']}",tags=("count"))

        elif x>=self.scr_width-105 and x<=self.scr_width-30 and y>=51 and y<=71:
            if self.modes["preview"]=="disabled":
                return
            if self.modes['audio']=='on':
                self.modes['audio']='off'
            else:
                self.modes['audio']='on'
            self.canvas2.delete('audio')
            self.canvas2.create_text(self.scr_width-95,52,anchor="nw",font=("Liberation Serif",10),text=f"audio: {self.modes['audio']}",tags=("audio"))

        elif x>self.scr_width-160 and x<self.scr_width-125 and y>33 and y<68:
            path = filedialog.askdirectory()
            if not path:
                return
            self.canvas2.grid_forget()
            self.canvas.grid(row=0,column=0,sticky="EW")
            self.canvas2.delete("thumbs")
            self.canvas2.destroy()

            self.chg+=len(self.data)
            self.framelog = []
            self.data,self.path = self.MyClient.load_files(path)
            self.first = [True for i in range(len(self.data))]

            widthread = threading.Thread(target=lambda:self.widgets())
            widthread.start()

            thread = threading.Thread(target=self.transition)
            self.root.after(2000, lambda:thread.start())
        elif x>20 and x<75 and y>10 and y<65:
            self.canvas2.grid_forget()
            self.canvas.grid(row=0,column=0,sticky="EW")
            self.canvas2.delete("thumbs")
            self.canvas2.destroy()
            self.chg+=len(self.data)
            self.framelog = []
            self.data,self.path=[],""
            self.widgets()
            self.transition()

        elif x>self.scr_width-200 and x<self.scr_width-165 and y>33 and y<68:
            self.togglewindowstate()
        elif x>self.scr_width-240 and x<self.scr_width-205 and y>33 and y<68:
            self.MyClient.save_path(self.path)
            self.canvas2.destroy()
            self.root.destroy()
            sys.exit()
        elif self.h>self.scr_height*1.5 and x>self.scr_width-95 and x<self.scr_width-45 and y>self.h-210 and y<self.h-160:
            thread = threading.Thread(target=lambda:self.smoothscrolltotop())
            thread.start()
        elif self.c!="": 
            self.thread_start = False
            self.run_vlc(self.data[self.c])

    def smoothscrolltotop(self):   
        for i in range(100,-1,-1):
            self.canvas2.yview_moveto(i/100)

    def widgets(self):
        small_font = ("Verdana", 10)
        self.thumbnail_images = []
        self.titlenames = []
        cutoff=6
        current_row, current_column = 0,0
        pixel = PhotoImage(width=1, height=1)

        h=(((len(self.data)+1)//2)*(self.thumby+100))+300
        if  h-300<self.scr_height:
            h=self.scr_height+150
        self.h=h

        self.canvas2 = Canvas(
            self.root, width = self.root.winfo_screenwidth()-20,height = self.scr_height,
            relief='flat',highlightthickness=0,scrollregion=(0,0,700,h)
        )
        self.canvas2.configure(bg=self.hex_from_rgb((255,253,235)))

        self.vbar=Scrollbar(self.root,orient=VERTICAL)
        self.vbar.grid(row=0, column=1,sticky="NSEW")
        self.vbar.config(command=self.canvas2.yview)

        self.hbar=Scrollbar(self.root,orient=HORIZONTAL)
        self.hbar.grid(row=1,column=0)
        self.hbar.config(command=self.canvas2.xview)

        self.canvas2.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set,yscrollincrement=10)

        if h>self.scr_height*1.5:
            self.canvas2.create_image(self.scr_width-95,h-210,image=self.up_arrow_pic,anchor="nw")
        if len(self.data)==0:
            #self.textlabelmaker(30,100,375,130,color="bisque",tag='_preview')
            #self.canvas2.create_text(30,102,text=f"Click on the folder icon to pick a folder.",anchor="nw",font=("Liberation Serif",15))
            self.canvas2.create_image(0,0,image=self.frontpage_pic,anchor="nw")
        else:
            self.canvas2.create_rectangle(0,0,self.scr_width-20,75,fill="antique white",width=0)
            self.canvas2.create_line(0,75,self.scr_width-20,75,width=1,fill="grey")

        self.canvas2.create_image(20,10,image=self.logo_pic,anchor="nw")
        self.canvas2.create_image(self.scr_width-160,33,image=self.folder_pic,anchor="nw")
        self.canvas2.create_image(self.scr_width-200,33,image=self.fullscreen_pic,anchor="nw")
        self.canvas2.create_image(self.scr_width-240,33,image=self.close_pic,anchor="nw")


        self.textlabelmaker(self.scr_width-165,7,self.scr_width-40,27,color="cyan",tag='_preview')
        self.canvas2.create_text(self.scr_width-170,8,text=f"Preview Mode: {self.modes['preview']}",anchor="nw",font=("Liberation Serif",10),tags=("preview"))

        color=['lime','green yellow']
        if self.modes['preview']=="disabled":
            color=['grey','grey']

        self.textlabelmaker(self.scr_width-95,29,self.scr_width-40,49,color=color[0],tag="_count")
        self.canvas2.create_text(self.scr_width-95,30,anchor="nw",font=("Liberation Serif",10),text=f"count:  {self.modes['count']}",tags=("count"))

        self.textlabelmaker(self.scr_width-95,51,self.scr_width-40,71,color=color[1],tag="_audio")
        self.canvas2.create_text(self.scr_width-95,52,anchor="nw",font=("Liberation Serif",10),text=f"audio: {self.modes['audio']}",tags=("audio"))
        c=0
        y=100
        for key in self.data:
            mylabel = Label(self.root, image=pixel, text="loading...", compound="center", height=self.thumby, width=self.thumbx, borderwidth=3,bg="salmon")
            self.thumbnail_images.append(mylabel)

            if c%2==0:
                x=30
                y=(c//2)*(self.thumby+100)+100
            else:
                x=55+self.thumbx
                y=((c-1)//2)*(self.thumby+100)+100 

            self.canvas2.create_window(x,y,window=self.thumbnail_images[-1],anchor="nw",tags=("thumbs"))
            self.canvas2.create_arc(x+5,y+self.thumby+15,x+40,y+self.thumby+48,start=90,extent=180,fill="bisque",width=0,style=CHORD,outline="")
            self.canvas2.create_arc(x+self.thumbx-45,y+self.thumby+15,x+self.thumbx-10,y+self.thumby+48,start=270,extent=180,fill="bisque",width=0,style=CHORD,outline="")
            self.canvas2.create_rectangle(x+23,y+self.thumby+15,x+self.thumbx-28,y+self.thumby+49,fill="bisque",width=0)

            txt = self.canvas2.create_text(x+20,y+self.thumby+20,anchor="nw",font=("Liberation Serif",15),text="loading...")
            self.titlenames.append(txt)
            c+=1

        self.canvas2.create_rectangle(0,h-150,self.scr_width-20,h,fill="black",width=0)
        self.canvas2.create_text(20,h-140, anchor="nw",font=("Consolas",12), text="Built by Ankith Abhayan.",fill="grey")
        self.edit_thumbnail()
        

    def edit_thumbnail(self):
        #updating the labels to display images
        i = 0
        for value in self.data:
            filepath = value
            cap = cv2.VideoCapture(filepath)
            framesno = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            start,end = framesno//10, framesno-framesno//10
            number = randint(start,end)
            self.framelog.append(number)
            if cap.isOpened() == False:
                print("error opening video file")

            while cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, number)
                res, frame = cap.read()
                if res == True:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    im = ImageTk.PhotoImage(Image.fromarray(frame).resize((self.thumbx,self.thumby)))
                    cv2.destroyAllWindows()
                self.thumbnail_images[i]["image"] = im
                self.thumbnail_images[i].photo = im
                self.thumbnail_images[i]["text"] = ""
                val=value[:(self.thumbx-48)//10]
                if val != value:
                    val+="..."
                self.canvas2.itemconfig(self.titlenames[i],text=val)
                break
            i += 1