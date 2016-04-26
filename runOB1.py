# -*- coding: utf-8 -*-
'''
### this script enables to use custom programs for Elvefow OB1

### installation
- for Elveflow need Labview runtime environment!
- need Elveflow32.py in wdir
- do not run with IPython console since Checkbuttons do not work (run '%gui tk' first)
- for implementation of matplotlib into tkinter (in Anaconda) reinstall matplotlib by
'pip uninstall matplotlib'
'pip install matplotlib'
in cmd

'''
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
import numpy as np
import scipy as sp
import time
from collections import deque
#from tkinter import ttk
#from tkinter import messagebox
#import Elveflow32 as ork

style.use("ggplot")



class MenuBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        # inherit from Frame
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.parent = parent

        # initialize child for correct function of close button 'X'
        self.settings_child = None

        # create a frame. enables to group widgets
        self.frame = tk.Frame(self.parent)

        # create buttons, labels and other widgets
        self.var = tk.IntVar()
        self.mainToggle = tk.Checkbutton(self.frame, text = 'OFF', bg = 'red',
                                         indicatoron=0, command = self.main_toggle_cb,
                                         variable = self.var)
        self.title = tk.Label(self.frame, text='Custom app for Elveflow OB1 pressure controller')
        self.settings = tk.Button(self.frame, text = 'settings', command = self.settings_open_cb)
        self.close = tk.Button(self.frame, text = 'close', command = self.close_cb)
        
        # buttons need to be placed by a geometry manager (pack, grid, place, ...)
        self.mainToggle.pack(side = 'left')
        self.settings.pack(side= 'left')
        self.title.pack(side = 'left')
        self.close.pack(side = 'left')
        self.frame.pack()
        
        
    def main_toggle_cb(self):
        if self.var.get() == 0:
            print('MAIN TOGGLE: OFF')
            self.mainToggle.configure(text = 'OFF')
        elif self.var.get() == 1:
            print('MAIN TOGGLE: ON')
            self.mainToggle.configure(text = 'ON')
    
    def settings_open_cb(self):
        def close_settings(): # reset child variable on close, for correct function of close button 'X'
            #if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.settings_child.destroy()
            self.settings_child = None
        if not self.settings_child:
            self.settings_child = Settings()
            self.settings_child.protocol("WM_DELETE_WINDOW", close_settings)
            
    def close_cb(self):
        MainApp.close_cb(self)

        

        

class Settings(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)

        self.geometry("400x300")
        self.title("Settings")

        

class MainPanel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.parent = parent
        
        self.frame = tk.Frame(self.parent) 
        
        # header
        self.labelChannels = tk.Label(self.frame, text = ['channel'])
        self.labelFunction = tk.Label(self.frame, text = ['function'])
        self.applySetPressure = tk.Button(self.frame, text = ['Apply'], command = self.apply_set_cb)
        self.labelAmplitude = tk.Label(self.frame, text = 'amplitude')
        self.labelPeriod = tk.Label(self.frame, text = 'period')
        self.labelGetPressure = tk.Label(self.frame, text = 'pressure (mbar)')
        
        self.labelChannels.grid(row=0, column = 0)
        self.labelFunction.grid(row=0, column = 1)
        self.applySetPressure.grid(row=0, column = 2)
        self.labelAmplitude.grid(row= 0, column = 3)
        self.labelPeriod.grid(row= 0, column = 4)
        self.labelGetPressure.grid(row=0, column = 5)
                
        # initialize variables for buttons
        self.stateVar = {}  
        self.optionsVar = {}
        self.pressureVar = {}
        self.amplitudeVar = {}
        self.periodVar = {}
        
        self.pressureSets = []
        self.amplitudeSets = []
        self.periodSets = []
        self.pressureGets = []
        
        self.colours = {'1':'orange','2':'lightgreen','3':'lightblue','0':'yellow'}
        channels = []
        
        for ch in range(4):
            # initialize channels
            channels.append(Channel(ch)) 
            channels[ch].colour = self.colours[str(ch)]

            # assign variables, set default values
            self.stateVar[str(ch)]= tk.IntVar()
            self.stateVar[str(ch)].set(channels[ch].state)
            
            self.optionsVar[str(ch)] = tk.StringVar()
            self.optionsVar[str(ch)].set(channels[ch].function) 
            
            self.pressureVar[str(ch)] = tk.StringVar()
            self.pressureVar[str(ch)].set(channels[ch].pressure)
            
            self.amplitudeVar[str(ch)] = tk.StringVar()
            self.amplitudeVar[str(ch)].set(channels[ch].amplitude)
            
            self.periodVar[str(ch)] = tk.StringVar()
            self.periodVar[str(ch)].set(channels[ch].period)
            
            self.toggle = tk.Checkbutton(self.frame, text = str(ch), bg = self.colours[str(ch)],
                                        indicatoron=1, command = self.toggle_cb,
                                        variable = self.stateVar[str(ch)])
                                        
            # options menu to select the function for the channel
            self.options = tk.OptionMenu(self.frame, self.optionsVar[str(ch)], 'const.', 'sine', 'triangle','square')
            
            
            # allow only floats in entry fields
            vcmd = (root.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
            # input boxes to enter pressures        
            self.pressureSet = tk.Entry(self.frame, textvariable = self.pressureVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd)
            self.amplitudeSet = tk.Entry(self.frame, textvariable = self.amplitudeVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd)
            self.periodSet = tk.Entry(self.frame, textvariable = self.periodVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd)
            self.pressureGet = tk.Label(self.frame, text = '0')
            
            self.pressureSets.append(self.pressureSet)
            self.amplitudeSets.append(self.amplitudeSet)
            self.periodSets.append(self.periodSet)
            self.pressureGets.append(self.pressureGet)  
                        
            self.toggle.grid(row=ch+1, column = 0)
            self.options.grid(row=ch+1, column = 1)
            self.pressureSet.grid(row=ch+1, column = 2)
            self.amplitudeSet.grid(row=ch+1, column = 3)
            self.periodSet.grid(row=ch+1, column = 4)
            self.pressureGet.grid(row=ch+1, column = 5)
            

            
        
        self.frame.pack() 
        
    def toggle_cb(self):
        for key in self.stateVar:
            if self.stateVar[key].get() == 0:
                print('Channel ', key, ': OFF')
            elif self.stateVar[key].get() == 1:
                print('Channel ', key, ': ON')
            print('Function: ', self.optionsVar[key].get())     

            
    def apply_set_cb(self):
        for ch in range(len(self.pressureGets)):
            self.pressureGets[ch].configure(text = self.pressureSets[ch].get())
            # write the settings to the channel objects
            channels[ch].pressure = self.pressureSets[ch].get()
            channels[ch].amplitude = self.amplitudeSets[ch].get()
            channels[ch].period = self.periodSets[ch].get()
            print(ch, channels[ch].pressure, channels[ch].amplitude, channels[ch].period)
            # ork.OB1_SetPressure(OB1, int(self.pressureSets[read].get()), ch, 2000)
            # self.pressureReads[ch].configure(text = str(ork.OB1_GetPressure(OB1, ch, 2000)))
            
    def validate(self, action, index, value_if_allowed,
                       prior_value, text, validation_type, trigger_type, widget_name):
        # this function prevents entering anything but float numbers in Entry fields
        if text in '0123456789.':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
            
class RealTimeGraph(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)   

        self.canvas = FigureCanvasTkAgg(f, master = self.frame)

        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.show()

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frame.pack() 
        
    def realtime_data():
        # all time in seconds
        period = 30
        tNow = time.time()-startTime
        t.append(tNow)
        t.popleft()
        
        p.append(np.sin((tNow)/period*2*np.pi)+np.random.randn(1)*.05)
        p.popleft()
        
        return t, p
        
    def realtime_setting():
        # all time in seconds
        period = 30
        tNow = time.time()-startTime
        tSet.append(tNow)
        tSet.popleft()
        
        pSet.append(np.sin((tNow)/period*2*np.pi))
        pSet.popleft()
        
        return tSet, pSet

class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        
        self.menuBar = MenuBar(self)
        self.mainPanel = MainPanel(self)
        self.realTimeGraph = RealTimeGraph(self)


        self.menuBar.pack(side="bottom", fill="x") 
        self.mainPanel.pack(side="top", fill="both", expand=True)
        self.realTimeGraph.pack(side="top", fill="y")
        
        # change default close behaviour, so device is shut off cleanly
        root.protocol("WM_DELETE_WINDOW", self.close_cb)
        
        
        
    def close_cb(self):
        print('close')
        # ork.OB1_Close(OB1)
        root.destroy()
        
class Channel():
    def __init__(self, index, state = 0, function = 'const.', pressure = 0, 
                 amplitude = 0, period = 30, colour = 'red'):
        self.index = index
        self.state = state
        self.function = function
        self.pressure = pressure
        self.amplitude = amplitude
        self.period = period
        
    def wave_pattern(self):
        if self.state == 1:
            if self.state == 'const.':
                p = self.pressure
            elif self.state == 'sine':
                tNow = time.time()-startTime
                p = self.pressure + self.amplitude*np.sin(tNow/self.period*2*np.pi)
            elif self.state == 'triangle':
                tNow = time.time()-startTime
                p = self.pressure + self.amplitude*sp.signal.sawtooth(tNow/self.period*2*np.pi, 0.5)
            elif self.state == 'square':
                tNow = time.time()-startTime
                p = self.pressure + self.amplitude*sp.signal.square(tNow/self.period*2*np.pi, 0.5)
        else:
            p = 0
            
        return p


f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

startTime = time.time()
t = deque(np.linspace(0, 60, 60))
p = deque(np.empty(60) * np.nan)
tSet = deque(np.linspace(0, 60, 60))
pSet = deque(np.sin((np.linspace(0, 60, 60))/30*2*np.pi))

def animate(i): 
    t, p = RealTimeGraph.realtime_data()
    tSet, pSet = RealTimeGraph.realtime_setting()
    a.clear()
    a.plot(t, p)
    a.plot(tSet, pSet)
        
if __name__ == '__main__':
    root = tk.Tk() # create window
    app = MainApp(root).pack(side="top", fill="both", expand=True)
    ani = animation.FuncAnimation(f, animate, interval=1000)
    root.mainloop()