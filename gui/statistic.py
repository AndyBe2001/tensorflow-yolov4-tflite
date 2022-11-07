from pathlib import Path
from tkinter.constants import ANCHOR, N
from tkinter import Frame, Canvas, Entry, Button, PhotoImage, N, BOTH, LEFT
from tkcalendar import Calendar
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def statistic():
    Statistic()
    
class Statistic(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent
        
        self.name = "statistic"
        self.configure(bg="#F4F6F8")
        
        self.chart_mode = 0
        
        canvas = Canvas(
            self,
            bg="#F4F6F8",
            height=670,
            width=1180,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        canvas.place(x=0,y=0)
        
        #Place plot chart
        self.chart = Canvas(
            self,
            bg="#F4F6F8",
            height=652,
            width=862,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.chart.place(x=7,y=7)
        
        #Place plot option
        self.option = Canvas(
            self,
            bg="#F4F6F8",
            height=652,
            width=304,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.option.place(x=876,y=7)
        
        self.chart.chart_bg_image = PhotoImage(file=relative_to_assets('image_5.png'))
        self.option.option_bg_image = PhotoImage(file=relative_to_assets('image_6.png'))
        self.option.option_refresh_image = PhotoImage(file=relative_to_assets('image_10.png'))
        self.option.option_mode_image = PhotoImage(file=relative_to_assets('image_11.png'))
        self.option.option_export_image = PhotoImage(file=relative_to_assets('image_9.png'))
        
        #Adding chart background
        self.chart.create_image(0,0,image = self.chart.chart_bg_image, anchor='nw')
        
        self.generateOption()
        self.generateChart()
        
    def generateChart(self):
        #Destroy last chart
        try:
            self.bar1.destroy()
        except:
            pass
        #Adding chart element
        try:
            self.chart_data = {
                'Hour':self.parent.visitor.hourList,
                'Visitor':self.parent.visitor.getVisitorInfo(self.calendarToDayIndex())
            }
        except:
            self.chart_data = {
                'Hour':self.parent.visitor.hourList,
                'Visitor':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            }   
        self.chart_dataFrame = pd.DataFrame(self.chart_data)
        #Show chart in canvas
        if self.chart_mode == 0:
            figure = plt.Figure(figsize=(6, 5), dpi=120)
            ax0 = figure.add_subplot(111)
            self.bar1 = FigureCanvasTkAgg(figure, self.chart)
            self.bar1.get_tk_widget().place(x=55, y=18, anchor='nw')
            self.chart_dataFrame = self.chart_dataFrame[['Hour', 'Visitor']].groupby('Hour').sum()
            self.chart_dataFrame.plot(kind='bar', legend=True, ax=ax0)
            ax0.set_title(self.calendarToDayString())
        elif self.chart_mode == 1:
            figure = plt.Figure(figsize=(6, 5), dpi=120)
            ax0 = figure.add_subplot(111)
            line0 = FigureCanvasTkAgg(figure, self.chart)
            line0.get_tk_widget().place(x=55, y=18, anchor='nw')
            self.chart_dataFrame = self.chart_dataFrame[['Hour', 'Visitor']].groupby('Hour').sum()
            self.chart_dataFrame.plot(kind='line', legend=True, ax=ax0, color='r', marker='o', fontsize=10)
            ax0.set_title(self.calendarToDayString())
    
    def generateOption(self):
        #Adding option background
        self.option.create_image(0, 0, image = self.option.option_bg_image, anchor='nw')
        #Adding the calendar
        self.option_frame = Frame(self.option, width=274, height=210)
        self.option_frame.place(x=10,y=15, anchor='nw')
        currentDate = time.localtime()
        self.option_calendar = Calendar(self.option_frame, font="Arial 11", selectmode='day',
                                        year=currentDate.tm_year, month=currentDate.tm_mon,
                                        day=currentDate.tm_mday)
        self.option_calendar.pack()
        #Adding the refresh button
        self.option_refresh = Button(
            self.option,
            image = self.option.option_refresh_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda : self.generateChart(),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat',
        )
        self.option_refresh.place(x=10, y=423)
        #Adding the mode button
        self.option_mode = Button(
            self.option,
            image = self.option.option_mode_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda : self.change_chart(),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat',
        )
        self.option_mode.place(x=10, y=496)
        #Adding the export button
        self.option_export = Button(
            self.option,
            image = self.option.option_export_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda : self.export_chart(),
            cursor='hand2', activebackground='#FFFFFF',
            relief='flat',
        )
        self.option_export.place(x=10, y=569)
        
    def change_chart(self):
        self.chart_mode = (self.chart_mode + 1) % 2
        self.generateChart()
    def export_chart(self):
        filename = self.option_calendar.get_date().replace('/','_')+".csv"
        self.chart_dataFrame.to_csv('./export/'+filename, header=True)
        
    def calendarToDayString(self):
        return self.option_calendar.get_date()
    def calendarToDayIndex(self):
        return int(time.mktime(time.strptime(self.option_calendar.get_date(),'%m/%d/%y'))/(60*60*24)) + 1
        