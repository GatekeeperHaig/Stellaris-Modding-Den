import tkinter as tk

class ScrollFrame(tk.Frame):
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(root, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", 
                                  tags="self.frame")
        #self.canvas.config(height=500)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.frame.bind('<Enter>', self._bound_to_mousewheel)
        self.frame.bind('<Leave>', self._unbound_to_mousewheel)
        self.vsb.bind('<Enter>', self._bound_to_mousewheel)
        self.vsb.bind('<Leave>', self._unbound_to_mousewheel)


    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _bound_to_mousewheel(self, event):
        #print("e")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        #print("l")
        self.canvas.unbind_all("<MouseWheel>") 
        self.canvas.unbind_all("<Button-4>") 
        self.canvas.unbind_all("<Button-5>") 
        
    def _on_mousewheel(self, event):
        #print("m")
        scroll=0
        if event.num == 5 or event.delta == -120:
          scroll = 1
        if event.num == 4 or event.delta == 120:
          scroll = -1
        self.canvas.yview_scroll(scroll, "units")  

if __name__ == "__main__":
    root=tk.Tk()
    ScrollFrame(root).pack(side="top", fill="both", expand=True)
    root.mainloop()