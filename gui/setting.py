from pathlib import Path
from tkinter.constants import ANCHOR, N
from tkinter import Frame, Canvas, Entry, PhotoImage, Checkbutton, Scale, HORIZONTAL, N

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def setting():
    Setting()
    
class Setting(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent
        
        self.name = "setting"
        self.configure(bg="#F4F6F8")
        
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
        
        #Place setting bloc
        canvas.setting_bg_image = PhotoImage(file=relative_to_assets('image_7.png'))
        canvas.create_image(7,7,image = canvas.setting_bg_image, anchor='nw')
        
        #Place function filter
        canvas.create_text(
            35.67,
            29,
            anchor="nw",
            text="功能選項",
            fill="#000000",
            font=("Arial Bold", 30 * -1),
        )
            #Adding mask option checkbutton
        Checkbutton(canvas, text="口罩辨識", variable=self.parent.maskValue, onvalue=1, offvalue=0, bg="white", font=('Arial',15)).place(x=35.67, y=70, anchor='nw')
            #Adding forbidden option checkbutton
        Checkbutton(canvas, text="違禁品辨識", variable=self.parent.forbiddenValue, onvalue=1, offvalue=0, bg="white", font=('Arial',15)).place(x=35.67, y=110, anchor='nw')
            #Adding visitor option checkbutton
        Checkbutton(canvas, text="入館人數統計", variable=self.parent.visitorValue, onvalue=1, offvalue=0, bg="white", font=('Arial',15)).place(x=35.67, y=150, anchor='nw')
        
        #Place volume setting
        canvas.create_text(
            619,
            29,
            anchor="nw",
            text="警報音量",
            fill="#000000",
            font=("Arial Bold", 30 * -1),
        )
            #Adding volume option drag
        Scale(canvas, variable=self.parent.volumeValue, from_=0, to=100, orient=HORIZONTAL,sliderlength=15,length=250, bg="white").place(x=619, y=70, width=100,anchor='nw')