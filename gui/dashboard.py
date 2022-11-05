from pathlib import Path
from tkinter.constants import ANCHOR, N
from tkinter import Frame, Canvas, Entry, Button, PhotoImage, Label, N
from threading import Thread, enumerate
from PIL import Image, ImageTk
import pickle
import os

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
        
        #Setup screenshot params
        self.screenshot = {}  
        for filename in os.listdir('./screenshot'):
            file = os.path.join('./screenshot', filename)
            # checking if it is a file
            if os.path.isfile(file):
                self.screenshot[filename] = self.load_screenshot(file)
                
        self.screenshot_obj = {}
        
        print("Step 2 - Done")
        
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
            height=151,
            width=697,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.screenshot_canvas.place(x=450,y=500)
        
        #Place main video place
        self.canvas.camera_bg_image = PhotoImage(file=relative_to_assets('image_1.png'))
        self.canvas.create_image(29.665,0,image = self.canvas.camera_bg_image,anchor='nw')
        
        self.parent.camera = Label(self.canvas, image = ImageTk.PhotoImage(Image.open(relative_to_assets('image_1.png')).resize((854,480))))
        self.parent.camera.place(x=585,y=240, anchor='center')
        
        #Place the visitor information
        self.canvas.visitor_bg_image = PhotoImage(file=relative_to_assets('image_2.png'))
        self.canvas.create_image(20.665, 499.67, image = self.canvas.visitor_bg_image, anchor='nw')
        
        self.canvas.create_text(
            51.67,
            524,
            anchor='nw',
            text='當前館內人數',
            fill='#000000',
            font=('Arial Bold', 27 * -1),
            justify="right",
        )
        self.canvas.create_text(
            243.67,
            524,
            anchor='nw',
            text='本日入館人數',
            fill='#000000',
            font=('Arial Bold', 27 * -1),
            justify="right",
        )
        try:
            self.canvas.create_text(
                120,
                570,
                anchor='nw',
                text=str(self.parent.visitor.inside),
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        except:
            self.canvas.create_text(
                120,
                570,
                anchor='nw',
                text='0',
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        try:
            self.canvas.create_text(
                320,
                570,
                anchor='nw',
                text=str(self.parent.visitor.today),
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        except:
            self.canvas.create_text(
                320,
                570,
                anchor='nw',
                text='0',
                fill='#000000',
                font=('Arial', 53 * -1),
                justify="center",
            )
        
        self.refresh_screenshot()
        
    def save_screenshot(self, obj, filename):
        source, file = filename.split('shot/') #./screnshot/filename
        with open(filename, 'wb') as outp:  # Overwrites any existing file
            pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)
        self.screenshot[file] = obj
        self.refresh_screenshot()
            
    def load_screenshot(self, filename):
        with open(filename, 'rb') as inp:
            screenshot = pickle.load(inp)
        return screenshot
    
    def delete_screenshot(self, filename):
        os.remove("./screenshot/" + filename)
        self.screenshot.pop(filename)
        self.refresh_screenshot()
        
    def refresh_screenshot(self):
        count = 1
        self.screenshot_canvas.delete('all')
        #Place the screenshot information
        self.screenshot_canvas.screenshot_bg_image = PhotoImage(file=relative_to_assets('image_3.png'))
        self.screenshot_canvas.create_image(451, 499.67, image = self.screenshot_canvas.screenshot_bg_image, anchor='nw')
        
        self.screenshot_canvas.create_text(
            10,
            10,
            anchor='nw',
            text='時間',
            fill='#000000',
            font=('Arial Bold', 20 * -1),
            justify="left",
        )
        self.screenshot_canvas.create_text(
            280,
            10,
            anchor='nw',
            text='違規行為',
            fill='#000000',
            font=('Arial Bold', 20 * -1),
            justify="left",
        )
        for key in self.screenshot:
            objTime, objContent = key.split('_')
            
            #Putting the background
            self.screenshot_canvas.screenshot_content_bg_image = PhotoImage(file=relative_to_assets('image_4.png'))
            self.screenshot_canvas.create_image(451, 505 + (count * 44), image = self.screenshot_canvas.screenshot_content_bg_image, anchor='nw')
            
            #Putting the time
            self.screenshot_canvas.create_text(
                10,
                10 + (count * 44),
                anchor="nw",
                text = objTime,
                fill='#000000',
                font=('Arial Bold', 20 * -1),
                justify="left"
            )
            #Putting the content
            self.screenshot_canvas.create_text(
                280,
                10 + (count * 44),
                anchor="nw",
                text = objContent,
                fill='#000000',
                font=('Arial Bold', 20 * -1),
                justify='left'
            )
            
            #Putting the open photo button
            open_bg_image = PhotoImage(file=relative_to_assets("button_1.png"))
            screenshot_open_btn = Button(
                self.screenshot_canvas,
                image = open_bg_image,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: print("nothing now"),
                cursor='hand2', activebackground='#FFFFFF',
                relief='flat',
            )
            screenshot_open_btn.place(x=500,y=10+(count*44), width=62.67, height=27.33)
            #Putting the close screenshot button
            close_bg_image = PhotoImage(file=relative_to_assets("button_2.png"))
            screenshot_close_btn = Button(
                self.screenshot_canvas,
                image = close_bg_image,
                borderwidth=0,
                highlightthickness=0,
                command= lambda filename = key: self.delete_screenshot(filename),
                cursor='hand2', activebackground='#FFFFFF',
                relief='flat',
            )
            screenshot_close_btn.place(x=600,y=10+(count*44), width=62.67, height=27.33)
            
            count = count + 1