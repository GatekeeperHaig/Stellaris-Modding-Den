#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
import tkinter as tk
from tkinter import filedialog
from tkinter import *
#from tkinter.tix import *
from tkinter import ttk
from tooltip import CreateToolTip
from scrollframe import ScrollFrame
import webbrowser
import platform
import convertCSV_TXT

class Logger(object):
    def __init__(self, nb, tabs):
        self.terminal = sys.stdout
        self.nb = nb
        self.tabs=tabs
        

    def write(self, message):
        self.terminal.write(message)
        self.tabs[self.nb.index(self.nb.select())].txt.insert(tk.END,message)
        self.tabs[self.nb.index(self.nb.select())].txt.see(tk.END)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass  
      
 
  

def startEditor(filename, forceEditor=False):
  if platform.system()=='Windows':
    if forceEditor:
      subprocess.Popen("notepad "+filename, shell=True)
    else:
      subprocess.Popen(filename, shell=True)
  else:
    editor = os.getenv('EDITOR')
    if editor:
        subprocess.Popen(editor + ' ' + filename, shell=True)
    else:
        webbrowser.open(filename)

class Line:
  def openFile(self):
    current=self.getTxt2()#("1.0",END).strip()
    if current=='""' or not os.path.exists(current):
      fileName=filedialog.askopenfilename(initialdir = self.root.lastPath,title = "Select file",filetypes = (self.root.defaultFileFilter, ("all files","*")))
    else:
      fileName=filedialog.askopenfilename(initialdir = os.path.dirname(current),title = "Select file",filetypes = (self.root.defaultFileFilter, ("all files","*")))
    if fileName:
      self.setTxt(fileName.strip())
      #txt.delete("1.0",END)
      #txt.insert("1.0", fileName.strip())
      self.root.lastPath=os.path.dirname(fileName.strip())
      with open(".GUI_last_path",'w') as file:
        file.write(self.root.lastPath)
  def convert(self):
    argString=self.getTxt2()+" "+" ".join(self.root.fixedOptions)
    for i in range(len(self.root.options)):
      if self.root.checkVars[i].get():
        argString+=" --"+self.root.options[i]
    args=self.root.command.parse(argString)
    args.fileNames=[self.getTxt()]
    self.result=self.root.command.main(args)
  def getResultFileName(self):
    return self.result
  def __init__(self,root):
    line= tk.Frame(root.mainFrame)
    self.lineFrame=line
    self.root=root
    #root.lines.append(line)
    line.pack(side=tk.TOP)
    #self.checkvar = IntVar()
    #self.check=Checkbutton(line, text="filter", variable=self.checkvar)
    #self.txt= tk.Text(line, bg="white",width=60, height=1)
    self.txt= tk.Entry(line, bg="white",width=60)
    self.result=""
        
    self.bConv = tk.Button(line, text="Convert", command=self.convert)
    #self.bConv = tk.Button(line, text="Convert", command=lambda:webbrowser.open_new(self.getTxt()))
    self.bEditS = tk.Button(line, text="Edit Source", command=lambda:startEditor(self.getTxt()))
    self.bEditF = tk.Button(line, text="Edit Filter", command=lambda:startEditor(self.getTxt().replace(".txt",".filter"),True))
    self.bEditR = tk.Button(line, text="Edit Result", command=lambda:startEditor(self.getResultFileName()))
    self.bFile = tk.Button(line, text="...", command=self.openFile)
    self.bDel = tk.Button(line, fg="red", text="X", command=lambda:root.removeLineByReference(line))
    self.bConv.pack(side=tk.LEFT)
    self.txt.pack(side=tk.LEFT)
    self.bFile.pack(side=tk.LEFT)
    self.bDel.pack(side=tk.LEFT)
    self.bEditS.pack(side=tk.LEFT)
    if "filter" in root.options:
      self.bEditF.pack(side=tk.LEFT)
    self.bEditR.pack(side=tk.LEFT)
    #self.check.pack(side=tk.LEFT)
    self.bConvTooltip= CreateToolTip(self.bConv, "Init")
    self.bEditSTooltip= CreateToolTip(self.bEditS, "Init")
    self.bEditFTooltip= CreateToolTip(self.bEditF, "Init")
    self.bEditRTooltip= CreateToolTip(self.bEditR, "Init")
    CreateToolTip(self.bDel, "Remove line. No files will be deleted!")
  def getTxt(self):
    return self.txt.get().strip()
  def getTxt2(self):
    #return self.txt.get("1.0",END).strip()
    return "'"+self.txt.get().strip()+"'"
  def setTxt(self, string):
    self.txt.delete(0,END)
    self.txt.insert(0, string.strip())
    self.txt.xview_moveto(1)
    self.root.fixedOptions.append("--test_run")
    self.convert()
    self.root.fixedOptions=self.root.fixedOptions[:-1]
    #args=convertCSV_TXT.parse(self.getTxt2()+" --test_run")
    #args.fileNames=[self.getTxt()]
    #self.result=convertCSV_TXT.main(args)
    

class TabClass:
  def addLine(self):
    self.lines.append(Line(self))
  def addFile(self):
    self.lines.append(Line(self))
    self.lines[-1].bFile.invoke()
  def addFiles(self):
    files=filedialog.askopenfilenames(initialdir = self.lastPath,title = "Select file",filetypes = (self.defaultFileFilter, ("all files","*")))
    if files:
      self.lastPath=os.path.dirname(files[0].strip())
      with open(".GUI_last_path",'w') as file:
        file.write(self.lastPath)
    for fileName in files:
      self.lines.append(Line(self))
      self.lines[-1].setTxt(fileName)
    #print (root.filename)
  def removeLineByIndex(self, index):
    self.lines[index].lineFrame.pack_forget()
    del self.lines[index]
    #del self.buttons[index]
  def removeLineByReference(self, line):
    lineFrames=[a.lineFrame for a in self.lines]
    index=lineFrames.index(line)
    self.removeLineByIndex(index)
  def setSize(self):
    if len(self.lines)>0:
      lineWidth=self.lines[-1].lineFrame.winfo_height()
      if lineWidth>1: #make sure we do not kill the init!
        self.scrollFrame.canvas.config(width=self.lines[-1].lineFrame.winfo_width())
      self.scrollFrame.canvas.config(height=min(-self.mainFrame.winfo_rooty()+self.lines[-1].lineFrame.winfo_rooty() + self.lines[-1].lineFrame.winfo_height(),self.tab.winfo_height()//3*2))
    else:
      elements=self.extraLineMain.winfo_children()
      lineWidth=0
      for element in elements:
        lineWidth=max(lineWidth,-self.mainFrame.winfo_rootx()+element.winfo_rootx() + element.winfo_width())
      if lineWidth>10: #make sure we do not kill the init!
        self.scrollFrame.canvas.config(width=lineWidth)
  def checkAll(self):
    for line in self.lines:
      if line.checkvar.get()==0:
        for line in self. lines:
          line.checkvar.set(1)
        return 0
    for line in self. lines:
      line.checkvar.set(0)
  def invokeAll(self):
    for line in self.lines:
      line.bConv.invoke()
  def checkValid(self):
    self.setSize()
    for line in self.lines:
      sourceR=1
      filterR=1
      resultR=1
      resultW=1
      if not os.access(line.getTxt(),os.R_OK):
        sourceR=0
      #if os.path.exists(line.result):
        #try:
          #open(line.result)
        #except IOError:
          #resultW=0
          
        ##and not os.access(line.result,os.W_OK):
        ##resultW=0
      if not os.access(line.result,os.W_OK):
        resultR=0
      #if not os.access(line.getTxt().replace(".txt","_filter.txt"),os.W_OK):
        #filterR=0
      if resultW and sourceR:
        line.bConv.config(state="normal")
        line.bConvTooltip.update("Start script")
      else:
        line.bConv.config(state="disabled")
        if not sourceR:
          line.bConvTooltip.update("Invalid source file")
        elif not resultW:
          line.bConvTooltip.update("Result file access problem. Might be locked by program that has it open")
      if sourceR:
        line.bEditS.config(state="normal")
        line.bEditSTooltip.update("Open source file in default editor")
      else:
        line.bEditS.config(state="disabled")
        line.bEditSTooltip.update("Invalid source file")
      if filterR:
        line.bEditF.config(state="normal")
        line.bEditFTooltip.update("Open or create and open filter file. Comma separated list of tags")
      else:
        line.bEditF.config(state="disabled")
        line.bEditFTooltip.update("Invalid")
      if resultR and resultW:
        line.bEditR.config(state="normal")
        line.bEditRTooltip.update("Open result file.")
      else:
        line.bEditR.config(state="disabled")
        line.bEditRTooltip.update("Missing result file. You probably need to create it first via 'Convert'")
        
    #os.F_OK − Value to pass as the mode parameter of access() to test the existence of path.
    #os.R_OK − Value to include in the mode parameter of access() to test the readability of path.
    #os.W_OK Value to include in the mode parameter of access() to test the writability of path.
    #os.X_OK Value to include in the mode parameter of access() to determine if path can be executed.

  def __init__(self,tab,root,command, fixedOptions, defaultFileFilter,options=[]):
    self.root=root
    self.tab=tab
    self.lines=[]
    self.lineFrame = tk.Frame(tab)
    self.lineFrame.pack()
    self.scrollFrame=ScrollFrame(self.lineFrame)
    self.scrollFrame.pack(side="top", fill="both", expand=True)
    self.mainFrame=self.scrollFrame.frame
    self.lastPath="."
    if os.path.exists(".GUI_last_path"):
      with open(".GUI_last_path") as file:
        self.lastPath=file.read().strip()
        #print(self.lastPath)
    self.options=options
    self.command=command
    self.defaultFileFilter=defaultFileFilter
    self.checkVars=[]
    self.fixedOptions=fixedOptions
    
    
    #self.mainFrame=tk.Frame(self.lineFrame)
    #self.mainFrame.pack(side="top", fill="both", expand=True)
    #self.mainFrame.bind( '<Configure>', maxsize )
    self.extraLineMain=tk.Frame(self.mainFrame)
    self.extraLineMain.pack(side=tk.TOP)
    for option in options:
      self.checkVars.append(IntVar())
      check=Checkbutton(self.extraLineMain, text=option, variable=self.checkVars[-1])
      check.pack(side=tk.RIGHT)
    #b = tk.Button(self.extraLineMain, text="(Un-)check all", command=self.checkAll)
    #b.pack(side=tk.RIGHT)
    #b = tk.Button(self.extraLineMain, text="Add line", command=self.addLine)
    #b.pack(side=tk.RIGHT)
    b = tk.Button(self.extraLineMain, text="Add file(s)", command=self.addFiles)
    b.pack(side=tk.RIGHT)
    b = tk.Button(self.extraLineMain, text="Convert All", command=self.invokeAll)
    b.pack(side=tk.LEFT)

    txt_frm = tk.Frame(tab, width=600, height=600)
    txt_frm.pack(fill="both", expand=True)
    # ensure a consistent GUI size
    txt_frm.grid_propagate(False)
    # implement stretchability
    txt_frm.grid_rowconfigure(0, weight=1)
    txt_frm.grid_columnconfigure(0, weight=1)
    
    # create a Text widget
    self.txt = tk.Text(txt_frm, borderwidth=3, relief="sunken")
    self.txt.config(font=("consolas", 12), undo=True, wrap='word')
    self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # create a Scrollbar and associate it with txt
    scrollb = tk.Scrollbar(txt_frm, command=self.txt.yview)
    scrollb.grid(row=0, column=1, sticky='nsew')
    self.txt['yscrollcommand'] = scrollb.set
#def maxsize( event=None ):
    #if(event.height>200):
      #print(event.height)
      #event.widget.grid_propagate(False)
      #event.widget.grid_rowconfigure(0, weight=1)
      #event.widget.grid_columnconfigure(0, weight=1)
    #scrollbar.ScrolledWindow(self.mainFrame)

  
def repeatedChecks(tabClasses, root):
  for tab in tabClasses:
    tab.checkValid()
  root.after(100, lambda:repeatedChecks(tabClasses,root))

def main():
  root = Tk()
  root.title("Stellaris Python Script Helper")
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  root.geometry("{!s}x{!s}".format(1000,screen_height*2//3))
  ## create a toplevel menu
  #menubar = Menu(root)

  ## create a pulldown menu, and add it to the menu bar
  #filemenu = Menu(menubar, tearoff=0)
  #filemenu.add_command(label="Open", command=hello)
  #filemenu.add_command(label="Save", command=hello)
  #filemenu.add_separator()
  #filemenu.add_command(label="Exit", command=root.quit)
  #menubar.add_cascade(label="File", menu=filemenu)

  ## create more pulldown menus
  #editmenu = Menu(menubar, tearoff=0)
  #editmenu.add_command(label="Cut", command=hello)
  #editmenu.add_command(label="Copy", command=hello)
  #editmenu.add_command(label="Paste", command=hello)
  #menubar.add_cascade(label="Edit", menu=editmenu)

  #helpmenu = Menu(menubar, tearoff=0)
  #helpmenu.add_command(label="About", command=hello)
  #menubar.add_cascade(label="Help", menu=helpmenu)

  ## display the menu
  #root.config(menu=menubar)


  tabControl = ttk.Notebook(root)          # Create Tab Control
  tabs=[]
  tabs.append([("text files","*.txt"),"txt to csv", ["filter"], convertCSV_TXT,[],ttk.Frame(tabControl)])
  tabs.append([("comma separated files","*.csv"),"csv to txt", ["allow_additions", "overwrite"], convertCSV_TXT,["--to_txt"], ttk.Frame(tabControl)])
  tabClasses=[]
  for defaultFileFilter,name,options,command,fixedOptions,tab in tabs:
    tabControl.add(tab, text=name)
    tabClasses.append(TabClass(tab,root,command,fixedOptions, defaultFileFilter,options))

  tabControl.pack(expand=1, fill="both")  # Pack to make visible


  sys.stdout = Logger(tabControl,tabClasses) #ensures output goes to right tab and console

  root.minsize(1000, 0)
  root.after(5, lambda:repeatedChecks(tabClasses,root))
  root.mainloop()
  
  
if __name__ == "__main__":
  #root = Tk()
  #frame=scrollbar.ScrolledWindow(root)
  #frame.pack()
  #frame2=frame.scrollwindow
  #b=tk.Button(frame2, text="Add", command=root.quit)
  #b.pack(side=tk.LEFT)
  #root.mainloop()
  main()