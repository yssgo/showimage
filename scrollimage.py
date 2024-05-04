#!python3.10
#coding:utf-8

#Source Code From https://stackoverflow.com/a/56046307
'''
import tkinter as tk

# Import the package if saved in a different .py file else paste 
# the ScrollableImage class right after your imports.
from scrollimage import ScrollableImage   

root = tk.Tk()

# PhotoImage from tkinter only supports:- PGM, PPM, GIF, PNG format.
# To use more formats use PIL ImageTk.PhotoImage
img = tk.PhotoImage(file="logo.png")

image_window = ScrollableImage(root, image=img, scrollbarwidth=6, 
                               width=200, height=200)
image_window.pack()

root.mainloop()
'''

import tkinter
import platform

class ScrollableImageFrame(tkinter.Frame):    
    def __init__(self, master=None, **kw):
        self.image = kw.pop('image', None)
        sw = kw.pop('scrollbarwidth', 10)
        super().__init__(master=master, **kw)
        self.canvas = tkinter.Canvas(self, highlightthickness=0, **kw)
        
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.image)
        
        # Vertical and Horizontal scrollbars
        self.v_scroll = tkinter.Scrollbar(self, orient='vertical', width=sw)
        self.h_scroll = tkinter.Scrollbar(self, orient='horizontal', width=sw)
        # Grid and configure weight.
        self.canvas.grid(row=0, column=0,  sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Set the scrollbars to the canvas
        self.canvas.config(xscrollcommand=self.h_scroll.set, 
                           yscrollcommand=self.v_scroll.set)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        # Assign the region to be scrolled 
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind_class(self.canvas, "<MouseWheel>", self.mouse_scroll) # Windows, "MacOS Aqua"
        self.canvas.bind_class(self.canvas, "<Button-4>", self.mouse_scrollup) # X11
        self.canvas.bind_class(self.canvas, "<Button-5>", self.mouse_scrolldown) # X11
    
    def mouse_scrollup(self, evt): # X11
        self.mouse_scroll(evt)
        
    def mouse_scrolldown(self, evt): # X11
        self.mouse_scroll(evt)

    def mouse_scroll(self, evt): # Windows, "MacOS Aqua"
        if evt.state == 0 :
            if platform.system() != 'Windows':
                self.canvas.yview_scroll(-1*(evt.delta), 'units') # For MacOS, Linux
            else:
                self.canvas.yview_scroll(int(-1*(evt.delta/120)), 'units') # For windows
        if evt.state == 1:
            if platform.system() != 'Windows':
                self.canvas.xview_scroll(-1*(evt.delta), 'units') # For MacOS, Linux
            else:
                self.canvas.xview_scroll(int(-1*(evt.delta/120)), 'units') # For windows
