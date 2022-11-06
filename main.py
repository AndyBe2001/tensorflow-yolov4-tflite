#Import visitor parameter
from scripts.visitor import Visitor
#Import ui window
from gui.dashboard import Dashboard
from gui.statistic import Statistic
from gui.setting import Setting
#Import ui library
from pathlib import Path
from tkinter import (
    Tk,
    Toplevel,
    Frame,
    Canvas,
    Button,
    PhotoImage,
    messagebox,
    StringVar,
    IntVar,
    DoubleVar
)
#import cv2
from PIL import Image, ImageTk
import time
from threading import Thread, enumerate
import vlc

#Import yolo library
import time
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
import core.utils as utils
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto

#GUI
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./gui/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

root = Tk()
root.withdraw()

def mainWindow():
    MainWindow()
    
class MainWindow(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        
        Thread(target=self.main, args=()).start()
        
        self.title("運用深度學習技術於圖書館人物偵測")
        
        self.geometry("1280x720")
        self.configure(bg = "#F4F6F8")
        
        self.current_window = None
        self.current_window_label = StringVar()
        
        self.alarmOn = False    
        
        self.camera = None
        
        #Main window canvas
        self.canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=720,
            width=1280,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
            #Main content
        self.canvas.place(x=0,y=0) 
        self.canvas.create_rectangle(
            92,0,1280,720, fill="#F4F6F8", outline=""
        )
        
        #Adding the navigation panel
        self.canvas.navigationPanel_bg_image = PhotoImage(file=relative_to_assets('image_8.png'))
        self.canvas.create_image(0, 0, image = self.canvas.navigationPanel_bg_image, anchor='nw')
        
            #Adding the navigator bar
        self.sidebar_indicator = Frame(self, background="#000000")
        self.sidebar_indicator.place(x=80.67, y=427.33, height=67.33, width=7.33)
        
            #Adding the dashboard
        button_image_1 = PhotoImage(file=relative_to_assets("button_5.png"))
        self.dashboard_btn = Button(
            self.canvas,
            image = button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.handle_btn_press(self.dashboard_btn, "dashboard"),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat',
        )
        self.dashboard_btn.place(x=16,y=420, width=60, height=77.33)
            #Adding the statics button
        button_image_2 = PhotoImage(file=relative_to_assets('button_4.png'))
        self.statistic_btn = Button(
            self.canvas,
            image = button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.handle_btn_press(self.statistic_btn, "statistic"),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat',
        )
        self.statistic_btn.place(x=20.67, y=520, width=53.33, height=77.33)
            #Adding the setting button
        button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
        self.setting_btn = Button(
            self.canvas,
            image = button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command= lambda: self.handle_btn_press(self.setting_btn, "setting"),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat'
        )
        self.setting_btn.place(x=21.33,y=620, width=52, height=77.33)
        
        #Add title
        self.heading = self.canvas.create_text(
            364,
            11.33,
            anchor='nw',
            text="運用深度學習技術於圖書館人物偵測",
            fill="#000000",
            font=('Arial Bold',40 * -1),
        )
        
        self.maskValue = IntVar()
        self.forbiddenValue = IntVar()
        self.visitorValue = IntVar()
        self.volumeValue = DoubleVar()
        
        #Loop through windows and place them
        self.windows = {
            'dashboard': Dashboard(self),
            'statistic': Statistic(self),
            'setting': Setting(self),
        }
        
        self.handle_btn_press(self.dashboard_btn, 'dashboard')
        self.sidebar_indicator.place(x=80.67, y=427.33)
        
        self.current_window.place(x=100, y=60, width=1280, height=720)

        self.current_window.tkraise()
        self.resizable(False, False)
        
        self.mainloop()
    
    def handle_btn_press(self, caller, name):
        #Place the sidebar on respective button
        self.sidebar_indicator.place(x=80.67, y=caller.winfo_y()+6)
        
        #Hide all screen
        for window in self.windows.values():
            window.place_forget()
        
        #Set current window
        self.current_window = self.windows.get(name)
        
        #Show the screen of the button pressed
        self.windows[name].place(x=100, y=60, width=1280, height=720)
        
    def handle_dashboard_refresh(self):
        self.windows['dashboard'] = Dashboard(self)

    def update(self, img = None):
        self.photo = ImageTk.PhotoImage(image = Image.fromarray(img).resize((854,480)))
        self.camera.configure(image = self.photo)
        self.camera.image = self.photo
    
    def alarmSound(self):
        if(not self.alarmOn):
            self.alarmOn = True
            media_player = vlc.MediaPlayer()
            media = vlc.Media('./data/alarm.wav')
            media_player.set_media(media)
            media_player.play()
            time.sleep(3)
            self.alarmOn = False
    
    def main(self):
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        input_size = 416
        video_path = 0

        print("Video from: ", video_path )
        try:
            vid = cv2.VideoCapture(int(video_path))
        except:
            vid = cv2.VideoCapture(video_path)

        saved_model_loaded = tf.saved_model.load("./checkpoints/yolov4-monitor_best", tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']

        frame_id = 0

        #Change begin
        self.visitor = Visitor('visitorLog.json', vertical = True, x = 300)
        forbiden_class = [0,1,4,5]
        forbiden_content = ['帶水瓶','帶鋁罐','無口罩','口罩未戴好']
        #Change end

        while True:
            return_value, frame = vid.read()
            if return_value:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
            else:
                if frame_id == vid.get(cv2.CAP_PROP_FRAME_COUNT):
                    print("Video processing complete")
                    break
                raise ValueError("No image! Try with another video format")
            
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            prev_time = time.time()

            batch_data = tf.constant(image_data)
            pred_bbox = infer(batch_data)
            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=0.45,
                score_threshold=0.25
            )
            pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
            image = utils.draw_bbox(frame, pred_bbox)

            #Change begin
                #Detect forbidden object
            for i in range(50):
                if (pred_bbox[1][0][i] >= 0.45 and pred_bbox[2][0][i] in forbiden_class):
                    #If forbidden object detected, make alarm ring
                    Thread(target = self.alarmSound, args = ()).start()
                    #Save the screenshot of the scene
                    filename = time.strftime('%Y-s-%m-s-%d %H-c-%M-c-%S', time.localtime(time.time())) + "_" + forbiden_content[forbiden_class.index(pred_bbox[2][0][i])]
                    filepath = "./screenshot/" + filename
                    self.windows["dashboard"].save_screenshot(image, filepath)
            #Change end

            curr_time = time.time()
            exec_time = curr_time - prev_time
            info = "time: %.2f ms" %(1000*exec_time)
            
            self.update(img = image)

if __name__ == '__main__':
    try:
       mainWindow()
       root.mainloop()
    
    except SystemExit:
        pass
