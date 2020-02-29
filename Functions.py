import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl 
from matplotlib import rc
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from numpy import *
from fractions import Fraction as Frct
import sqlite3 as sql
from scipy.integrate import quad
from threading import Thread
from time import sleep
mpl.use("TkAgg")

def secante(f, a, b, erreur=10**(-10), x=0) :
    """recherche de la zero de la fonction f entre a0 et b"""
    x += 1
    if x > 900:
        return None# pas de zero dans cette intervalle 
    if abs(f(a))>erreur :
        a-= (a-b)*f(a)/(f(a)-f(b))
        return secante(f , a , b , erreur , x)
    return a , x


class Widget():
    def __init__(self) :
        """
        the initiation function  :
        definnig a tkinter widget 
        """
        self.dictionnare = {
        "Zero" : lambda *args :  secante(*args)[0] , 
        "Integrate" : lambda *args : quad(*args)[0] ,
        "DLimité" : lambda x , y : polyfit(x , y , 5) }
        self.once = True 
        self.root = tk.Tk()
        self.root.title("Embedding in Tk")
        self.Main_Function()
        tk.mainloop()



    def Main_Function(self) :
        # self.historique()
        #self.Lis = tk.Listbox(frame )
        #self.Lis.pack(side = tk.TOP , expand = True , fill = tk.BOTH)
        
        self._FunctionEntry = tk.StringVar()
        self._FunctionEntry.set("sin(x) ")
        self._XIntervalEntry = tk.StringVar()
        self._YIntervalEntry = tk.StringVar()
        self.D3but = tk.BooleanVar()
        self._ShowData= tk.BooleanVar()
        self.D3but.set(False)
        # self._XIntervalEntry.set(" ")
        # self._YIntervalEntry.set(" ")

        frame = ttk.Frame(self.root)
        
        self._buttons = ttk.Frame(frame)
        _entries = tk.Frame(self._buttons)
        
        _PlotButton = ttk.Button(master=self._buttons, text="Plot", command=self.Plot)
        _PlotButton.pack( padx = 10 )
        _PlotButton.bind("<Return>" , self.Plot)
        self._Warning_Label = ttk.Label(self._buttons)
        self._Warning_Label["foreground"] = "red"
        self._Warning_Label["font"] = "Helvetica 10 bold underline"
        
        tk.Entry(_entries  ,font = "Courier 15 bold roman" , textvariable = self._FunctionEntry ).pack()
        tk.Entry(_entries  ,font = "Courier 15 bold italic" , textvariable = self._XIntervalEntry ).pack()
        self.yentr = tk.Entry(_entries  ,font = "Courier 13 bold italic" , textvariable = self._YIntervalEntry )
        self.shdat = tk.Checkbutton(_entries ,variable = self._ShowData ,font = "Helvetica 12 bold",  text = "Show data")
        self.shdat.pack()

        tk.Checkbutton(_entries , variable = self.D3but , 
            text = "3Dimensionnal" ,
            font = "Helvetica 12 bold" ,
            command = self.update).pack(side = tk.BOTTOM)
        _entries.pack()
        _results = tk.Frame(self._buttons)
        self.Results  = {"Zero" : tk.Label(_results , fg = "blue"),"Integrate" : tk.Label(_results ,fg = "blue") , "Dlimité" : tk.Label(_results , fg = "blue") }
        _results.pack(side = tk.BOTTOM)
        self._buttons.pack(side = tk.LEFT)

        _plotting = tk.Frame(frame)
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=_plotting)  # A tk.DrawingArea.
        self.sub = self.fig.add_subplot(111)
        _plotting.pack(side = tk.RIGHT)

        frame.pack()
    def showdata(self , *args)  :
        function , x  = args
        f = lambda x : eval(function)
        if self._ShowData.get() :
            try : 
                zero = self.dictionnare["Zero"](f , min(x) , max(x))
            except : 
                zero = "There isn't !!"
            integ = self.dictionnare["Integrate"](f , min(x) , max(x))
            x = linspace(min(x) , max(x) , 100) ; y = f(x)
            DL = self.dictionnare["DLimité"](x , y)
            DLIM = ""
            for i in range(len(DL)) :
                s = Frct(DL[i]).limit_denominator((i+2)**3)
                if s != 0 :
                    DLIM += f'{s} * x**{i}  \n'
            Data = {"Zero" :"le zero     : " + str(zero) ,
            "Integrate" :  "l'integrale : " + str(integ) , 
            "Dlimité" : "le Dlimité 5: " + str(DLIM) }
            for dt in Data.keys() : 
                self.Results[dt]["text"] = Data[dt]
                self.Results[dt].configure(compound = tk.CENTER , padx = 14 , font = "Courier 15")
                self.Results[dt].pack()
            self.root.update()
        elif self.D3but.get() :
            for e in self.Results.values() :
                e["text"] == ""
                e.pack_forget()
                self.root.update()

    def Plot(self , event = None ) :
        function = self._FunctionEntry.get()
        x_interval , y_interval = self._XIntervalEntry.get() , self._YIntervalEntry.get()
        if 'y' in function : 
            self.D3but.set(True)
            self.update()
            if y_interval == "" :
                self.warn("Please Insert a value for X axis")
                return None 
        if x_interval == "" : 
            self.warn("Please Insert a value for X axis")
            return None 
        x_interval = eval(x_interval)
        if self.D3but.get() and y_interval != ""  :
            self._ShowData.set(False)
            y_interval = eval(y_interval)
            self.insert_data(function , [str(x) for x in x_interval], [str(x) for x in y_interval])
            self.historique()
            self.ploting3D(function , x_interval , y_interval)
            Thread(target = self.showdata ,args = (function , x_interval)  ).start()
        elif y_interval == '' :
            if self.D3but.get(): 
                self.warn("Please Insert a value for Y axis")
            else :
                self.insert_data(function ,[str(x) for x in x_interval])
                self.historique()
                self.ploting2D(function ,x_interval)
                Thread(target = self.showdata ,args = (function , x_interval)  ).start()

    def ploting2D(self ,function , x_int, n = 100) :
        """
        the plotting function 
        create a plot object 
        with function given in the entries
        x_int : the intervalle where to plot  
        """
        x0 , xf = x_int
        f = lambda x : eval(function)
        zero = secante(f , x0 , xf)
        x_values = linspace(x0 , xf , n+1)
        y_values = f(x_values)
        self.drawcourbe(x_values , y_values)
    
    def ploting3D(self ,function , x_int ,y_int , n = 100) :
        f = lambda x , y : eval(function)
        x0 , xf = x_int
        y0 , yf = y_int
        x_values = linspace(x0 , xf ,n+1)
        y_values = linspace(y0 , yf ,n+1)
        x_values , y_values = meshgrid(x_values, y_values)
        z_values = f(x_values , y_values)
        self.drawcourbe(x_values , y_values , z_values)


    def drawcourbe(self , x , y , z = None ) :
        self.fig.delaxes(self.sub)
        if type(z) not in (list , ndarray) :
            self.sub = self.fig.add_subplot(111)
            self.sub.set_ylabel(u"f(x)")
            self.sub.plot(x , y)
        else : 
            self.sub = self.fig.add_subplot(111 , projection = "3d")
            self.sub.plot_surface(x , y , z)
            self.sub.set_ylabel(u'Y' , 
                fontdict = {"family" : 'Courier' , 
                "size" : 14 , 
                "weight" : tk.NORMAL })
            self.sub.set_zlabel(u'f(x)')
        self.sub.grid()
        self.sub.set_xlabel(u"X")
        self.fig.suptitle(str(self._FunctionEntry.get()))
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1 , padx = 5)
        if self.once : 
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
            self.toolbar.update()
            self.once = False 
    def warn(self , message) : 
        self._Warning_Label["text"] = message
        self._Warning_Label.pack(side = tk.BOTTOM)
        def wait() : 
            sleep(2)
            self._Warning_Label.pack_forget()
        Thread(target = wait).start()
    def update(self) : 
        """
        update : 
            - show data
            - 3 dimensional plotting 
        """
        if self.D3but.get() :
            self.shdat.pack_forget()
            self.yentr.pack()
            self.root.update()
        else :
            self.yentr.pack_forget()
            self.shdat.pack()
            self.root.update()

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    def open_base(self , command , extract = False ) : 
        bd = sql.connect("Data_Functions.sqlite3")
        cur = bd.cursor()
        cur.execute(command)
        if extract : 
            return cur.fetchall()
        else : 
            bd.commit()
        bd.close()

    def historique(self) :
        command = """
        select * 
        from Examples """
        L = self.open_base(command)
        #self.Lis.insert(tk.END , L)

    def insert_data(self , function , x , y = "") : 
        x = ",".join(x)
        if y : 
            y = ",".join(y)
        function = str(function)
        command = f"""
        insert into Examples values 
        (
        '{function}' , 
        '{x}' ,
        '{y}' )  ; """
        self.open_base(command)
def request() : 
    bd = sql.connect("Data_Functions.sqlite3")
    cur = bd.cursor()
    try : 
        command = "Select * from Examples"
        cur.execute(command)
    except OperationalError : 
        cur.execute("""
            Create Table Examples (
            Name Varchar ,
            x_intervalle Varchar , 
            y_intervalle Varchar )""")
    try : 
        s = cur.fetchall()
    except : 
        bd.commit()
        s = None
    bd.close()
    return s 


if __name__ == '__main__':
    from pprint import pprint 
    pprint(request())
    Widget()