from pathlib import Path
from tkinter.constants import ANCHOR, N
from tkinter import Frame, Canvas, Entry, Button, PhotoImage, Label, Toplevel, N
from threading import Thread, enumerate
from PIL import Image, ImageTk
import pickle
import os
import time

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def dashboard():
    Dashboard()
    
class Dashboard(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent
        
        self.name = "dashboard"
        self.configure(bg="#F4F6F8")
        
        self.captured = False
        
        #Setup screenshot params
        self.screenshot = {}  
        for filename in os.listdir('./screenshot'):
            file = os.path.join('./screenshot', filename)
            # checking if it is a file
            if os.path.isfile(file):
                self.screenshot[filename] = self.load_screenshot(file)
                
        self.screenshot_obj = {}
        
        self.canvas = Canvas(
            self,
            bg="#F4F6F8",
            height=660,
            width=1180,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.canvas.place(x=0,y=0)
        
        self.screenshot_canvas = Canvas(
            self,
            bg="#F4F6F8",
            height=155,
            width=710,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.screenshot_canvas.place(x=455,y=510)
        
        self.screenshot_canvas.screenshot_bg_image = PhotoImage(file=relative_to_assets('image_3.png'))
        self.screenshot_canvas.screenshot_content_bg_image = PhotoImage(file=relative_to_assets('image_4.png'))
        self.screenshot_open_bg_image = PhotoImage(file=relative_to_assets("button_1.png"))
        self.screenshot_close_bg_image = PhotoImage(file=relative_to_assets("button_2.png"))
        
        self.button_list = []
        
        #Place main video place
        self.canvas.camera_bg_image = PhotoImage(file=relative_to_assets('image_1.png'))
        self.canvas.create_image(29.665,0,image = self.canvas.camera_bg_image,anchor='nw')
        
        self.camera_loading_image = ImageTk.PhotoImage(Image.open(relative_to_assets('image_12.png')))
        self.parent.camera = Label(self.canvas, image = self.camera_loading_image)
        self.parent.camera.place(x=594.165,y=240, anchor='center')
        
        #Place the visitor information
        self.canvas.visitor_bg_image = PhotoImage(file=relative_to_assets('image_2.png'))
        self.canvas.create_image(20.665, 509.67, image = self.canvas.visitor_bg_image, anchor='nw')
        
        self.canvas.create_text(
            51.67,
            534,
            anchor='nw',
            text='當前館內人數',
            fill='#000000',
            font=('Arial Bold', 27 * -1),
            justify="right",
        )
        self.canvas.create_text(
            243.67,
            534,
            anchor='nw',
            text='本日入館人數',
            fill='#000000',
            font=('Arial Bold', 27 * -1),
            justify="right",
        )
        try:
            self.insideInfo  = self.canvas.create_text(
                130,
                610,
                anchor='center',
                text=str(self.parent.visitor.inside),
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        except:
            self.insideInfo  = self.canvas.create_text(
                130,
                610,
                anchor='center',
                text='0',
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        try:
            self.todayInfo  = self.canvas.create_text(
                320,
                610,
                anchor='center',
                text=str(self.parent.visitor.today),
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        except:
            self.todayInfo  = self.canvas.create_text(
                320,
                610,
                anchor='center',
                text='0',
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        
        self.refresh_screenshot()
       
    def refresh_visitor(self):
        self.canvas.itemconfig(self.insideInfo, text=str(self.parent.visitor.inside))
        self.canvas.itemconfig(self.todayInfo, text=str(self.parent.visitor.today))
     
    def wait_next_capture(self):
        time.sleep(3)
        self.captured = False
    
    def save_screenshot(self, obj, filename):
        if self.captured:
            return
        self.captured = True
        source, file = filename.split('shot/') #./screnshot/filename
        with open(filename, 'wb') as outp:  # Overwrites any existing file
            pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)
        self.screenshot[file] = obj
        Thread(target=self.wait_next_capture,args=()).start()
        self.refresh_screenshot()
            
    def load_screenshot(self, filename):
        with open(filename, 'rb') as inp:
            screenshot = pickle.load(inp)
        return screenshot
    
    def delete_screenshot(self, filename):
        os.remove("./screenshot/" + filename)
        self.screenshot.pop(filename)
        self.refresh_screenshot()
    
    def open_screenshot(self, filename):
        screenshot_window = Toplevel(self.parent)
        screenshot_window.geometry("1440x810")
        screenshot_window.title(filename)
        screenshot_to_show_content = self.screenshot[filename]
        screenshot_to_show_content = ImageTk.PhotoImage(image = Image.fromarray(screenshot_to_show_content).resize((1440,810)))
        screenshot_to_show = Label(screenshot_window, image = screenshot_to_show_content)
        screenshot_to_show.pack()
        screenshot_window.mainloop()
        
    def refresh_screenshot(self):
        for button in self.button_list:
            button[0].destroy()
            button[1].destroy()
        count = 1
        self.screenshot_canvas.delete('all')
        #Place the screenshot information
        self.screenshot_canvas.create_image(0, 0, image = self.screenshot_canvas.screenshot_bg_image, anchor='nw')
        
        self.screenshot_canvas.create_text(
            20,
            20,
            anchor='nw',
            text='時間',
            fill='#000000',
            font=('Arial Bold', 24 * -1),
            justify="left",
        )
        self.screenshot_canvas.create_text(
            250,
            20,
            anchor='nw',
            text='違規行為',
            fill='#000000',
            font=('Arial Bold', 24 * -1),
            justify="left",
        )
        for key in self.screenshot:
            objTime, objContent = key.split('_')
            
            #Putting the background
            if count%2 == 1:
                self.screenshot_canvas.create_image(7, 15 + (count * 40), image = self.screenshot_canvas.screenshot_content_bg_image, anchor='nw')
            
            #Putting the time
            self.screenshot_canvas.create_text(
                20,
                25 + (count * 40),
                anchor="nw",
                text = objTime.replace('-s-','/').replace('-c-',':'),
                fill='#000000',
                font=('Arial Bold', 20 * -1),
                justify="left"
            )
            #Putting the content
            self.screenshot_canvas.create_text(
                250,
                25 + (count * 40),
                anchor="nw",
                text = objContent,
                fill='#000000',
                font=('Arial Bold', 20 * -1),
                justify='left'
            )
            
            #Putting the open photo button
            screenshot_open_btn = Button(
                self.screenshot_canvas,
                image = self.screenshot_open_bg_image,
                borderwidth=0,
                highlightthickness=0,
                command=lambda filename = key: self.open_screenshot(filename),
                cursor='hand2', activebackground='#FFFFFF',
                relief='flat',
            )
            screenshot_open_btn.place(x=580,y=23+(count*40), width=62.67, height=27.33)
            #Putting the close screenshot button
            screenshot_close_btn = Button(
                self.screenshot_canvas,
                image = self.screenshot_close_bg_image,
                borderwidth=0,
                highlightthickness=0,
                command= lambda filename = key: self.delete_screenshot(filename),
                cursor='hand2', activebackground='#FFFFFF',
                relief='flat',
            )
            screenshot_close_btn.place(x=650,y=23+(count*40), width=27, height=27)
            
            self.button_list.append([screenshot_open_btn, screenshot_close_btn])            
            count = count + 1