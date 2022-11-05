from pathlib import Path
from tkinter.constants import ANCHOR, N
from tkinter import Frame, Canvas, Entry, PhotoImage, N

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
        canvas.plot_bg_image = PhotoImage(file=relative_to_assets('image_5.png'))
        canvas.create_image(7,7,image = canvas.plot_bg_image, anchor='nw')
        
        #Place plot option
        canvas.option_bg_image = PhotoImage(file=relative_to_assets('image_6.png'))
        canvas.create_image(873.67, 7, image = canvas.option_bg_image, anchor='nw')
