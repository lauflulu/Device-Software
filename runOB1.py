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
import scipy.signal as spsg
import time
from collections import deque
#from tkinter import ttk
#from tkinter import messagebox
#import Elveflow32 as ork

style.use('dark_background')



class MenuBar(tk.Frame):
    def __init__(self, parent, friend, *args, **kwargs):
        # inherit from Frame
        tk.Frame.__init__(self, parent, friend, *args, *kwargs)
        self.parent = parent
        self.friend = friend
        # initialize child for correct function of close button 'X'
        self.settings_child = None

        # create a frame. enables to group widgets
        self.frame = tk.Frame(self)

        # create buttons, labels and other widgets
        self.var = tk.IntVar()
        self.mainToggle = tk.Checkbutton(self.frame, text = 'OFF', bg = 'red',
                                         indicatoron=0, command = self.main_toggle_cb,
                                         variable = self.var)
        self.title = tk.Label(self.frame, text='Custom app for Elveflow OB1 pressure controller')
        self.settings = tk.Button(self.frame, text = 'Settings', command = self.settings_open_cb)
        self.apply = tk.Button(self.frame, text = 'Apply', command = self.apply_cb)
        self.close = tk.Button(self.frame, text = 'close', command = self.close_cb)
        
        # buttons need to be placed by a geometry manager (pack, grid, place, ...)
        self.mainToggle.pack(side = 'left')
        self.settings.pack(side= 'left')
        self.apply.pack(side= 'left')
        self.title.pack(side = 'left')
        self.close.pack(side = 'left')
        self.frame.pack()
        
    def apply_cb(self):
        self.friend.apply_set_cb()
        
    def main_toggle_cb(self):
        global mainToggle
        if self.var.get() == 1:
            self.mainToggle.configure(text = 'ON')
        else:
            self.mainToggle.configure(text = 'OFF')
        mainToggle  = self.var.get()

    
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
        
        self.frame = tk.Frame(self) 
        
        
        # header
        self.labelChannels = tk.Label(self.frame, text = 'channel')
        self.labelFunction = tk.Label(self.frame, text = 'function')
        self.applySetPressure = tk.Label(self.frame, text = 'Pressure')
        self.labelAmplitude = tk.Label(self.frame, text = 'amplitude')
        self.labelPeriod = tk.Label(self.frame, text = 'period')
        self.labelPhase = tk.Label(self.frame, text = 'phase (°)')
        self.labelGetPressure = tk.Label(self.frame, text = 'pressure (mbar)')
        
        self.labelChannels.grid(row=0, column = 0)
        self.labelFunction.grid(row=0, column = 1)
        self.applySetPressure.grid(row=0, column = 2)
        self.labelAmplitude.grid(row= 0, column = 3)
        self.labelPeriod.grid(row= 0, column = 4)
        self.labelPhase.grid(row= 0, column = 5)
        self.labelGetPressure.grid(row=0, column = 6)
                
        # initialize variables for buttons
        self.stateVar = {}  
        self.optionsVar = {}
        self.pressureVar = {}
        self.amplitudeVar = {}
        self.periodVar = {}
        self.phaseVar = {}
        
        self.pressureSets = []
        self.amplitudeSets = []
        self.periodSets = []
        self.phaseSets = []
        self.pressureGets = []
        
        self.colours = {'1':'orange','2':'lightgreen','3':'lightblue','0':'yellow'}
        
        
        for ch in range(4):
            # initialize channels
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
            
            self.phaseVar[str(ch)] = tk.StringVar()
            self.phaseVar[str(ch)].set(channels[ch].phase)
            
            self.toggle = tk.Checkbutton(self.frame, text = str(ch), bg = self.colours[str(ch)],
                                        indicatoron=1, command = self.toggle_cb,
                                        variable = self.stateVar[str(ch)])
                                        
            # options menu to select the function for the channel
            self.options = tk.OptionMenu(self.frame, self.optionsVar[str(ch)], 'const.', 'sine', 'triangle','square')
            
            
            # allow only floats in entry fields
            vcmd = (root.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
            # input boxes to enter pressures        
            self.pressureSet = tk.Spinbox(self.frame, textvariable = self.pressureVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd,
                                        from_ = 0, to = 2000, increment  = 1)
            self.amplitudeSet = tk.Spinbox(self.frame, textvariable = self.amplitudeVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd,
                                        from_ = 0, to = 2000, increment  = 1)
            self.periodSet = tk.Spinbox(self.frame, textvariable = self.periodVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd,
                                        from_ = 0, to = 2000, increment  = 1)
            self.phaseSet = tk.Spinbox(self.frame, textvariable = self.phaseVar[str(ch)],
                                        validate = 'key', validatecommand = vcmd,
                                        from_ = 0, to = 2000, increment  = 1)
            self.pressureGet = tk.Label(self.frame, text = '0')
            
            self.pressureSets.append(self.pressureSet)
            self.amplitudeSets.append(self.amplitudeSet)
            self.periodSets.append(self.periodSet)
            self.pressureGets.append(self.pressureGet) 
            self.phaseSets.append(self.phaseSet)
                        
            self.toggle.grid(row=ch+1, column = 0)
            self.options.grid(row=ch+1, column = 1)
            self.pressureSet.grid(row=ch+1, column = 2)
            self.amplitudeSet.grid(row=ch+1, column = 3)
            self.periodSet.grid(row=ch+1, column = 4)
            self.phaseSet.grid(row=ch+1, column = 5)
            self.pressureGet.grid(row=ch+1, column = 6)
            

            
        
        self.frame.pack() 
        #self.apply_set_cb() # this resets channel objects properly ?
        
    def toggle_cb(self):
        for key in self.stateVar:
#            if self.stateVar[key].get() == 0:
#                print('Channel ', key, ': OFF')
#            elif self.stateVar[key].get() == 1:
#                print('Channel ', key, ': ON')
            channels[int(key)].state = self.stateVar[key].get()

            
    def apply_set_cb(self):
        for ch in range(len(self.pressureGets)):
            self.pressureGets[ch].configure(text = self.pressureSets[ch].get())
            # write the settings to the channel objects
            
            channels[ch].function = self.optionsVar[str(ch)].get()
            channels[ch].pressure = float(self.pressureSets[ch].get())
            channels[ch].amplitude = float(self.amplitudeSets[ch].get())
            channels[ch].period = float(self.periodSets[ch].get())
            channels[ch].phase = float(self.phaseSets[ch].get())
            # print(ch, channels[ch].pressure, channels[ch].amplitude, channels[ch].period)
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
        self.frame = tk.Frame(self)   

        self.canvas = FigureCanvasTkAgg(f, master = self.frame)

        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.show()

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frame.pack() 
        
    def realtime_data(ch):
        tNow = time.time()-startTime
        t[ch].append(tNow)
        t[ch].popleft()
        
        p[ch].append(int(Channel.wave_pattern(channels[ch]))+np.random.randn(1)*.5)
        p[ch].popleft()
            
        
        return t[ch], p[ch]
        
    def realtime_setting(ch):
        tNow = time.time()-startTime
        tSet[ch].append(tNow)
        tSet[ch].popleft()
        
        pSet[ch].append(int(Channel.wave_pattern(channels[ch])))
        pSet[ch].popleft()
        
        return tSet[ch], pSet[ch]

class MainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, *kwargs)
        self.parent = parent

        self.mainPanel = MainPanel(self.parent)
        self.menuBar = MenuBar(self.parent, self.mainPanel)
        self.realTimeGraph = RealTimeGraph(self.parent)
        
        self.menuBar.pack(side = 'top')
        self.mainPanel.pack(side = 'top')
        self.realTimeGraph.pack(side = 'top')
        
        # change default close behaviour, so device is shut off cleanly
        root.protocol("WM_DELETE_WINDOW", self.close_cb)
        
        
    def close_cb(self):
        print('close')
        # ork.OB1_Close(OB1)
        root.destroy()
        
class Channel():
    def __init__(self, index, state = 0, function = 'const.', pressure = 0, 
                 amplitude = 0, period = 30, phase = 0, colour = 'red'):
        self.index = index
        self.state = state
        self.function = function
        self.pressure = pressure
        self.amplitude = amplitude
        self.period = period
        self.phase = phase
        self.colour = colour
        
    def wave_pattern(self):
        pNow = 0
        if mainToggle == 1:
            if self.state == 1:
                if self.function == 'const.':
                    pNow = self.pressure
                elif self.function == 'sine':
                    tNow = time.time()-startTime
                    pNow = self.pressure + self.amplitude*np.sin(tNow/self.period*2*np.pi-self.phase*np.pi/180.0)
                elif self.function == 'triangle':
                    tNow = time.time()-startTime
                    pNow = self.pressure + self.amplitude*spsg.sawtooth(tNow/self.period*2*np.pi-(self.phase + 270.0)*np.pi/180.0, 0.5)
                elif self.function == 'square':
                    tNow = time.time()-startTime
                    pNow = self.pressure + self.amplitude*spsg.square(tNow/self.period*2*np.pi-self.phase*np.pi/180.0, 0.5)
                else:
                    pass
            else:
                pass
        else:
            pass

        return pNow
        
    def calculated_pattern(self):
        pNow = 0
        input_ = '1=1-2-3'
        if mainToggle == 1:
            if self.state == 1:
                pass
                # need to work with channel objects in wave pattern?
                # need attribute with deque?
                


global channels
channels = []
global mainToggle
mainToggle = 0

p = [0,0,0,0]
t = [0,0,0,0]
pSet = [0,0,0,0]
tSet = [0,0,0,0]

for ch in range(4):
    # initialize channels
    channels.append(Channel(ch)) 
    
    p[ch] = deque(np.empty(60) * np.nan)
    t[ch] = deque(np.linspace(0, 60, 60))

    pSet[ch] = deque(np.zeros(60))
    tSet[ch] = deque(np.linspace(0, 60, 60))

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)



startTime = time.time()

#t = deque(np.linspace(0, 60, 60))
#p = deque(np.empty(60) * np.nan)


def animate(i): 
    a.clear()
    
    #tSet, pSet = RealTimeGraph.realtime_setting()
    for ch in range(4):
        t, p = RealTimeGraph.realtime_data(ch)
        a.plot(t, p, channels[ch].colour, marker = '.', linestyle = 'None')
        tSet, pSet = RealTimeGraph.realtime_setting(ch)
        a.plot(tSet, pSet, channels[ch].colour)
    #a.plot(tSet, pSet)
        
if __name__ == '__main__':
    root = tk.Tk() # create window
    
    app = MainApp(root).pack(side="top", fill="both", expand=True)
    ani = animation.FuncAnimation(f, animate, interval=1000)
    root.mainloop()