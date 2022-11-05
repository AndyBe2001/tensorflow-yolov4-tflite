#Import visitor parameter
from scripts.visitor import Visitor
#Import ui library
import tkinter as tk
from tkcalendar import Calendar
import cv2
from PIL import Image, ImageTk
import time
from threading import Thread, enumerate
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
import core.utils as utils
from core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

#Temp data
visitorData = {
    "inside":["19271",43],
    "hour":["00-01","01-02","02-03","03-04","04-05","05-06","06-07","07-08","08-09","09-10","10-11","11-12",
           "12-13","13-14","14-15","15-16","16-17","17-18","18-19","19-20","20-21","21-22","22-23","23-24"],
    "19271":[0,0,0,0,0,0,0,0,0,0,0,0,40,53,60,70,54,0,0,0,0,0,0,0],
    "19270":[0,0,0,0,0,0,0,0,0,0,13,90,40,76,34,70,54,0,0,0,0,0,0,0],
}

class UserInterface:
    def __init__(self, window, window_title, vid_width=800, vid_height=450):
        self.window = window
        self.window.title(window_title)

        self.frame = tk.Frame(self.window).pack()

        # Create a canvas that can fit the video
        self.videoPanel = tk.Frame(self.frame).pack(side=tk.BOTTOM)
        self.video = tk.Label(self.videoPanel)
        self.video.pack(side=tk.LEFT)
 
        # Create a frame that can fit the screenshot
        self.screen = tk.Frame(self.frame,height=200).pack(side=tk.TOP)

        #CheckBox value
        self.maskValue = tk.IntVar()
        self.forbiddenValue = tk.IntVar()
        self.visitorValue = tk.IntVar()
        self.volumeValue = tk.DoubleVar()

        #Side button
        self.optionBox = tk.Frame(self.videoPanel, bg='black', borderwidth=2, relief='groove').pack(side=tk.RIGHT)
        self.optionMenu = tk.Label(self.optionBox, text="功能選擇",font=('Arial',20)).pack(side=tk.TOP)
        self.maskOption = tk.Checkbutton(self.optionBox, text="口罩辨識", variable=self.maskValue, font=('Arial',15)).pack(side=tk.TOP)
        self.forbiddenOption = tk.Checkbutton(self.optionBox, text="違禁品辨識", variable=self.forbiddenValue, font=('Arial',15)).pack(side=tk.TOP)
        self.visitorOption = tk.Checkbutton(self.optionBox, text="入館人數統計", variable=self.visitorValue, font=('Arial',15)).pack(side=tk.TOP)
        self.separator2 = tk.Label(self.optionBox, text=" ",font=('Arial',20)).pack(side=tk.TOP)
        self.volumeMenu = tk.Label(self.optionBox, text="警報音量",font=('Arial',20)).pack(side=tk.TOP)
        self.volumeOption = tk.Scale(self.optionBox, variable=self.volumeValue, from_=0, to=100, orient=tk.HORIZONTAL,sliderlength=10).pack(side=tk.TOP)
        self.separator = tk.Label(self.optionBox, text=" ",font=('Arial',20)).pack(side=tk.TOP)
        self.visitorInside = tk.Label(self.optionBox, text="目前館內人數：43",font=('Arial',15)).pack(side=tk.TOP)
        self.visitorToday = tk.Label(self.optionBox, text="今日入館人數：132",font=('Arial',15)).pack(side=tk.TOP)
        self.chartWindow = tk.Button(self.optionBox, text="顯示統計數據(小時)", command=Thread(target = self.showChart,args=()).start(), font=('Arial',15)).pack(side=tk.TOP)
        self.separator1 = tk.Label(self.optionBox, text=" ",font=('Arial',20)).pack(side=tk.TOP)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.dayIndex = int(time.time()/(60*60*24))

        Thread(target=self.main, args=()).start()

        self.window.mainloop()
 
    def showChart(self):
        global visitorData
        self.subwindow = tk.Toplevel(self.window)
        self.subwindow.title("統計數據")

        self.subwindowCalendar = Calendar(self.subwindow, selectmode = 'day', year = 2022, month = 10, day = 3).grid(column=0,row=0,sticky=tk.EW)

        df1 = DataFrame(visitorData, columns=['hour',str(self.dayIndex)])
        figure1 = plt.Figure(figsize=(3,5))
        ax1 = figure1.add_subplot(111)
        df1 = df1[['hour',str(self.dayIndex)]].groupby('hour').sum()
        bar1 = FigureCanvasTkAgg(figure1, self.subwindow)
        bar1.get_tk_widget().grid(column=0,row=1)
        df1.plot(kind='bar', legend=True, ax=ax1, fontsize=5, title="2022/10/03")

    def update(self, img = None):
        self.photo = ImageTk.PhotoImage(image = Image.fromarray(img).resize((800,450)))
        self.video.configure(image = self.photo)
        self.video.image = self.photo

    def main(self):
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        session = InteractiveSession(config=config)
        STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_configv2()
        input_size = 416
        video_path = 0

        print("Video from: ", video_path )
        try:
            vid = cv2.VideoCapture(int(video_path))
        except:
            vid = cv2.VideoCapture(video_path)

        saved_model_loaded = tf.saved_model.load("./checkpoints/yolov4-416", tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        
        if False:
            # by default VideoCapture returns float instead of int
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(vid.get(cv2.CAP_PROP_FPS))
            codec = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(None, codec, fps, (width, height))

        frame_id = 0

        #Change begin
        visitor = Visitor('visitorLog.json')
        forbiden_class = []
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
            
            frame_size = frame.shape[:2]
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
            
            #Change end

            curr_time = time.time()
            exec_time = curr_time - prev_time
            #result = np.asarray(image)
            info = "time: %.2f ms" %(1000*exec_time)
            print(info)
            #result = ImageTk.PhotoImage(image=image)
            #result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if not False:
                '''
                cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
                cv2.imshow("result", result)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                '''
                self.update(img = image)

            #if None:
            #    out.write(result)

            #frame_id += 1

if __name__ == '__main__':
    try:
        GUI = UserInterface(tk.Tk(),"")
    
    except SystemExit:
        pass
