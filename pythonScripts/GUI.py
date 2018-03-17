#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, subprocess,os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
#from tkinter.tix import *
from tkinter import ttk
from tooltip import CreateToolTip
from scrollframe import ScrollFrame
import webbrowser
import platform
import convertCSV_TXT
import createUpgradedBuildings
import copySubTag
import createAIVarsFromModifiers
import pickle

class Logger(object):
    def __init__(self, tabControl,error=False):
        if error:
          self.terminal=sys.stderr
        else:
          self.terminal = sys.stdout
        self.tabControl=tabControl
        # self.tabs=tabs
        self.error=error
        

    def write(self, message):
        # if self.error:
          # sys.stdout.write(self.error)
        self.terminal.write(message)
        txt=self.tabControl.getActiveTabClass().txt
        txt.config(state=NORMAL)
        if self.error:
          txt.tag_config("n", background="yellow", foreground="red")
          txt.insert(tk.END,message,("n"))
        else:
          txt.insert(tk.END,message)
        txt.see(tk.END)
        txt.config(state=DISABLED)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass  
      
 
  

def startEditor(filename, forceEditor=False):
  if not os.path.exists(filename):
    with open(filename,'w') as file:
      pass
  if platform.system()=='Windows':
    if forceEditor:
      subprocess.Popen("notepad "+filename, shell=True)
    else:
      subprocess.Popen('"'+filename+'"', shell=True)
  else:
    if (filename.find(".ods")!=-1):
      subprocess.Popen("xdg-open "+filename, shell=True)
    else:
      editor = os.getenv('EDITOR')
      if editor:
          subprocess.Popen(editor + ' ' + filename, shell=True)
      else:
          webbrowser.open(filename)

class Line:
  def openFile(self):
    current=self.getTxt()
    if current=='' or not os.path.exists(current):
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
    argList=[self.getTxt()]
    self.root.addArguments(argList, self)
    # argList+=self.root.fixedOptions
    # # +" "+" ".join(self.root.fixedOptions)
    
    # if self.root.optionWindow:
      # argList+=self.root.optionWindow.getOptions()
    # for i in range(len(self.root.options)):
      # if self.root.checkVars[i].get():
        # argList.append(self.root.options[i][1])
    # print(argList)
    # return 
    args=self.root.command.parse(argList)
    # args.buildingFileNames=[self.getTxt()]
    # args.fileNames=[self.getTxt()]
    self.result=self.root.command.main(args, argList)
    print(self.result)
  def getResultFileName(self):
    return self.result
  def focusNextTxt(self,event):
    txt=self.root.lines[(self.root.lines.index(self)+1)%len(self.root.lines)].txt
    txt.focus_set()
    txt.selection_range(0, END) 
    return "break"  
  def focusNextSubfolderTxt(self,event):
    txt=self.root.lines[(self.root.lines.index(self)+1)%len(self.root.lines)].subfolderTxt
    txt.focus_set()
    txt.selection_range(0, END) 
    return "break"
  def __init__(self,root):
    line= tk.Frame(root.mainFrame)
    self.lineFrame=line
    self.root=root
    #root.lines.append(line)
    line.pack(side=tk.TOP)
    self.lineCheckVar = IntVar()
    self.lineCheckButton=Checkbutton(line, text=root.singleEntryCheck, variable=self.lineCheckVar)
    #self.txt= tk.Text(line, bg="white",width=60, height=1)
    self.txt= tk.Entry(line, bg="white",width=85)
    
    self.txt.bind("<Tab>", self.focusNextTxt)
    self.result=""
    self.subfolderTxt=tk.Entry(line, bg="white", width=20)
    self.subfolderTxt.bind("<Tab>", self.focusNextSubfolderTxt)
        
    self.bConv = tk.Button(line, text="Convert", command=self.convert)
    #self.bConv = tk.Button(line, text="Convert", command=lambda:webbrowser.open_new(self.getTxt()))
    self.bEditS = tk.Button(line, text="Edit Source", command=lambda:startEditor(self.getTxt()))
    self.bEditF = tk.Button(line, text="Edit Filter", command=lambda:startEditor(self.getTxt().replace(".txt",".filter"),True))
    self.bEditR = tk.Button(line, text="Edit Result", command=lambda:startEditor(self.getResultFileName()))
    self.bFile = tk.Button(line, text="...", command=self.openFile)
    self.bDel = tk.Button(line, fg="red", text="X", command=lambda:root.removeLineByReference(line))
    if self.root.separateStart:
      self.bConv.pack(side=tk.LEFT)
    self.txt.pack(side=tk.LEFT)
    self.bFile.pack(side=tk.LEFT)
    if self.root.subfolder:
      self.subfolderTxt.pack(side=tk.LEFT)
    self.bDel.pack(side=tk.LEFT)
    self.bEditS.pack(side=tk.LEFT)
    # if ["Apply filter","--filter"] in root.options:
    if "filter" in [opt.name for opt in root.optionWindow.options]:
      self.bEditF.pack(side=tk.LEFT)
    # for option in root.options:
    #   if option[1]=="--filter":
    #     self.bEditF.pack(side=tk.LEFT)
    #     break
    self.bEditR.pack(side=tk.LEFT)


    if root.singleEntryCheck!="":
      self.lineCheckButton.pack(side=tk.LEFT)
    self.bConvTooltip= CreateToolTip(self.bConv, "Init")
    self.bEditSTooltip= CreateToolTip(self.bEditS, "Init")
    self.bEditFTooltip= CreateToolTip(self.bEditF, "Init")
    self.bEditRTooltip= CreateToolTip(self.bEditR, "Init")
    CreateToolTip(self.bDel, "Remove line. No files will be deleted!")
    #root.redoTabOrder()
  def getTxt(self):
    return self.txt.get().strip()
  def getTxt2(self):
    #return self.txt.get("1.0",END).strip()
    return '"'+self.txt.get().strip()+'"'
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
    files=filedialog.askopenfilenames(initialdir = self.lastPath,title = "Select file(s)",filetypes = (self.defaultFileFilter, ("all files","*")))
    if files:
      self.lastPath=os.path.dirname(files[0].strip())
      with open(".GUI_last_path",'w') as file:
        file.write(self.lastPath)
    for fileName in files:
      self.lines.append(Line(self))
      self.lines[-1].setTxt(fileName)
    #print (root.filename)
  # def redoTabOrder(self):
    # for line in self.lines:
      # print(line.txt.get())
      # line.txt.lower()  
    # if self.subfolder:
      # for line in self.lines:
        # print(line.subfolderTxt.get())
        # line.subfolderTxt.lower()
  def addMarkedFiles(self):
    curLine=len(self.lines)
    self.addFiles()
    for line in self.lines[curLine:]:
      line.lineCheckVar.set(1)
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
      # print(lineWidth)
      if lineWidth>1: #make sure we do not kill the init!
        self.scrollFrame.canvas.config(width=self.lines[-1].lineFrame.winfo_width())
      self.scrollFrame.canvas.config(height=min(-self.mainFrame.winfo_rooty()+self.lines[-1].lineFrame.winfo_rooty() + self.lines[-1].lineFrame.winfo_height(),self.tab.winfo_height()//3*2))
    else:
      elements=self.extraLineMain.winfo_children()
      lineWidth=0
      for element in elements:
        lineWidth=max(lineWidth,-self.mainFrame.winfo_rootx()+element.winfo_rootx() + element.winfo_width())
      # print(lineWidth)
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
    if self.separateStart:
      for line in self.lines:
        line.bConv.invoke()
    elif self.singleEntryCheck=="Source File":
      argList=[]
      self.addArguments(argList)
      sourceFiles=[]
      for line in self.lines:
        if line.lineCheckVar.get():  #Source File check
          sourceFiles.append(line.getTxt())
      for line in self.lines:
        if not line.lineCheckVar.get():  #Source File check
          args=self.command.parse([line.getTxt()]+sourceFiles+argList)
          line.result=self.command.main(args,[line.getTxt()]+sourceFiles+argList)

    else:
      argList=[]
      for line in self.lines:
        argList.append(line.getTxt())
      self.addArguments(argList)
      args=self.command.parse(argList)
      self.command.main(args,argList)
  def addArguments(self, argList,line=0):
    argList+=self.fixedOptions   
    if self.optionWindow:
      argList+=self.optionWindow.getOptions(line)
    for i in range(len(self.options)):
      if self.checkVars[i].get():
        argList+=self.options[i][1].split()
    if self.singleEntryCheck=="Helper File":
      argList.append("--helper_file_list")
      argList.append("")
      for line in reversed(self.lines):
        if line.lineCheckVar.get():
          argList[-1]+="1"
        else:
          argList[-1]+="0"
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
  def save(self):
    fileName=filedialog.asksaveasfilename(defaultextension=".pkl",initialdir = ".",title = "Select file to save to",filetypes = (("pickle files","*.pkl"), ("all files","*")))
    if fileName:
      with open(fileName, 'wb') as f:
        pickle.dump([var.get() for var in self.checkVars],f)
        if self.optionWindow:
          pickle.dump([var.get() for var in self.optionWindow.vals],f)
        else:
          pickle.dump([],f)
        pickle.dump([line.txt.get() for line in self.lines], f)
        pickle.dump([line.subfolderTxt.get() for line in self.lines], f)
        pickle.dump([line.lineCheckVar.get() for line in self.lines], f)
      # print("save")
  def load(self):
    fileName=filedialog.askopenfilename(initialdir = ".",title = "Select file to save to",filetypes = (("pickle files","*.pkl"), ("all files","*")))
    if fileName:
      for i in range(len(self.lines)):
        self.removeLineByIndex(0)
      with open(fileName, 'rb') as f:
        # print(pickle.load(f))
        # print(pickle.load(f))
        # print(pickle.load(f))
        # print(pickle.load(f))
        for i,val in enumerate(pickle.load(f)):
          self.checkVars[i].set(val)
        if self.optionWindow:
          for i,val in enumerate(pickle.load(f)):
            self.optionWindow.vals[i].set(val)
        else:
          pickle.load(f)
        self.loadLines(f)
  def loadAdd(self):
    fileName=filedialog.askopenfilename(initialdir = ".",title = "Select file to save to",filetypes = (("pickle files","*.pkl"), ("all files","*")))
    if fileName:
      with open(fileName, 'rb') as f:
        pickle.load(f)
        pickle.load(f)
        self.loadLines(f)
  def loadLines(self,f):
    try:
      i=len(self.lines)
      for entry in pickle.load(f):
        self.addLine()
        self.lines[-1].setTxt(entry)
      iLoc=i
      for entry in pickle.load(f):
        if self.subfolder:
          self.lines[iLoc].subfolderTxt.insert(0,entry)
          iLoc+=1
      iLoc=i
      for entry in pickle.load(f):
        self.lines[iLoc].lineCheckVar.set(entry)
        iLoc+=1
    except EOFError:
      print("Warning: File ended earlir than expected. File might be older version but still work perfectly or stuff is actually missing")

  def __init__(self,name,tab,root,command, fixedOptions, defaultFileFilter,optionWindow=0,extraAddButton=""):
    self.name=name
    self.root=root
    self.tab=tab
    self.lines=[]
    self.lineFrame = tk.Frame(tab)
    self.lineFrame.pack()
    self.scrollFrame=ScrollFrame(self.lineFrame)
    self.scrollFrame.pack(side="top", fill="both", expand=True)
    self.mainFrame=self.scrollFrame.frame
    self.optionWindow=optionWindow
    self.lastPath="."
    self.separateStart=True
    self.subfolder=False
    self.singleEntryCheck=""
    self.extraAddButton=extraAddButton
    # if name == "createUpgradedBuildings":
    #   self.helperFileCheck=True
    # else:
    #   self.helperFileCheck=False
    if os.path.exists(".GUI_last_path"):
      with open(".GUI_last_path") as file:
        self.lastPath=file.read().strip()
        #print(self.lastPath)
    self.options=[]#options
    self.command=command
    if platform.system()=="Linux":
      if ";" in defaultFileFilter[1]:
        splitList=defaultFileFilter[1].split(";")
        outString=""
        for entry in zip(*splitList):
          equal=1
          for e in entry:
            if e!=entry[0]:
              equal=0
          if equal:
            outString+=entry[0]
          else:
            outString+="["
            for e in entry:
              outString+=e
            outString+="]"
        defaultFileFilter=(defaultFileFilter[0],outString)
          # print(b)
          # if splitList[0][i]=="*" or splitList[0][i]==".":
            # outString+=spltL
    self.defaultFileFilter=defaultFileFilter
    self.checkVars=[]
    self.fixedOptions=fixedOptions
    
    
    #self.mainFrame=tk.Frame(self.lineFrame)
    #self.mainFrame.pack(side="top", fill="both", expand=True)
    #self.mainFrame.bind( '<Configure>', maxsize )
    self.extraLineMain=tk.Frame(self.mainFrame)
    self.extraLineMain.pack(side=tk.TOP)
    # for option in options:
    #   self.checkVars.append(IntVar())
    #   check=Checkbutton(self.extraLineMain, text=option[0], variable=self.checkVars[-1])
    #   check.pack(side=tk.RIGHT)
    #   CreateToolTip(check, option[2])
    #b = tk.Button(self.extraLineMain, text="(Un-)check all", command=self.checkAll)
    #b.pack(side=tk.RIGHT)
    #b = tk.Button(self.extraLineMain, text="Add line", command=self.addLine)
    #b.pack(side=tk.RIGHT)
    if optionWindow:
      b= tk.Button(self.extraLineMain, text="Options", command=self.optionWindow.window.deiconify)
      b.pack(side=tk.RIGHT)
    b = tk.Button(self.extraLineMain, text="Add file(s)", command=self.addFiles)
    b.pack(side=tk.RIGHT)
    if self.extraAddButton!="":
      b = tk.Button(self.extraLineMain, text=self.extraAddButton, command=self.addMarkedFiles)
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
    self.txt = tk.Text(txt_frm, borderwidth=3,bg="light grey", relief="sunken")
    self.txt.config(state=DISABLED)
    #self.txt.config(font=("consolas", 12), undo=True, wrap='word')
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

class Option:
  def __init__(self,  name='',description='', val=''):
    self.name=name
    if description=='':
      self.description=self.name.replace("_"," ")
    else:
      self.description=description
    self.val=val #boolean or string

class OptionWindow:
  def __init__(self,root,name, options,script):
    self.window=tk.Toplevel(root)
    self.window.withdraw()
    self.window.title(name)   
    self.window.protocol('WM_DELETE_WINDOW', self.window.withdraw)  # root is your root window
    self.vals=[]
    self.names=[]
    # frameL=tk.Frame(self.window)
    # frameL.pack(side="left", fill="both", expand=True)
    # frameR=tk.Frame(self.window)
    # frameR.pack(side="right", fill="both", expand=True)
    scriptArgs=vars(script.parse(" " " "))
    self.options=options

    parser=script.parse([],True)
    # parser=0
    # if script==createUpgradedBuildings:
    #   print("printing help")
    #   for option in options:
    #     for a in parser._actions:
    #       v=vars(a)
    #       if "--"+option.name in v['option_strings']:
    #         print(v["help"].replace("(default: %(default)s)",""))

    for i,option in enumerate(options):
      l=Label(self.window, text=option.description)
      # if parser:
      for a in parser._actions:
        v=vars(a)
        if "--"+option.name in v['option_strings']:
          # print()
          if v["help"]:
            CreateToolTip(l, v["help"].replace("(default: %(default)s)",""))
      # l.pack(side=tk.TOP)
      l.grid(row=i,column=0)
      option.defaultVal=scriptArgs[option.name]
      if isinstance(option.defaultVal, str) or isinstance(option.defaultVal, float):# or (isinstance(option.defaultVal, int) and option.defaultVal!=False and option.defaultVal!=True):
        self.vals.append(StringVar())
        self.vals[-1].set(str(option.defaultVal))
        e=Entry(self.window, bg="white",textvariable=self.vals[-1],width=40)
        # e.pack(side=tk.TOP)
        e.grid(row=i,column=1)
      else:
        self.vals.append(IntVar())
        self.vals[-1].set(option.defaultVal)
        c=Checkbutton(self.window,  text='', variable=self.vals[-1])
        # c.pack(side=tk.TOP)
        c.grid(row=i,column=1)
  def getOptions(self, line=0):
    outList=[]
    for option, val in zip(self.options, self.vals):
      if val.get():
        outList.append("--"+option.name)
        if isinstance(option.defaultVal, str) or isinstance(option.defaultVal, float):
          outList.append(val.get())
          if line and option.name=="output_folder" and line.root.subfolder:
            outList[-1]+="/"+line.subfolderTxt.get().strip()
        else:
          outList.append("--"+option.name)
    return outList
    #self.check=Checkbutton(line, text="filter", variable=self.checkvar)

class TabControlClass:
  def __init__(self,root):   
    nb = ttk.Notebook(root)          # Create Tab Control
    self.nb=nb
    self.root=root
    self.tabClasses=[]

    #def newTab(name, command, fileFilter, fixedOptions, options, extraAddButton, frame):

    of="output_folder"
    oll="one_line_level"
    jf="join_files"

    self.newTab("Txt To Ods",convertCSV_TXT,("text files",'*.txt;*.gfx'),[],["filter","manual_filter","create_new_file","use_csv"],"")
    self.tabClasses[-1].helpText="Creates an ods file from a Stellaris .txt file. Currently works for txt files that are lists of same top-tag entries (for example all components and sections."

    self.newTab("Ods To Txt",convertCSV_TXT,("table documents","*.ods"),["--to_txt"]
      ,["clean_header","changes_to_body","remove_header","forbid_additions","create_new_file",oll],"")
    self.tabClasses[-1].helpText="Uses an ods file to changes the accordingly named .txt file: Entries that are in the ods file are written into the txt file at the right place (overwriting what was there before or written directly in the header instead of overwriting a variable. \nEmpty or missing entries in the ods file remain unchanged! \n To delete something from the txt file, write '#delete' in the according cell in the ods file. If all subtags of a supertag are deleted, the supertag will also be deleted. Never delete a 'key'! It suffices to delete all other tags to delete a top-level tag (e.g. a whole component)"


    BUOptions=[of,"custom_mod_name","game_version","t0_buildings","languages","replacement_file","time_discount","cost_discount","remove_reduntant_upgrades","keep_lower_tier","custom_direct_build_AI_allow","simplify_upgrade_AI_allow","load_order_priority",jf,oll]
    self.newTab("Create Upgraded Buildings",createUpgradedBuildings,("text files","*.txt"),[]
      ,BUOptions,"Add Helper File(s)")
    self.tabClasses[-1].helpText='1. "Add file(s)": "Stellaris/common/buildings/00_buildings.txt" (unless you have no dependence on vanilla buildings at all, not even capital building requirements. Check "Helper file". Contents of such a file will be used, but the buildings wont be output.\n1b. If your buildings depend on any other buildings (other mods, other vanilla buildings): Add them the same way.\n2. Add all building files of the mod you want to make compatible. Do *not* check the "Helper file" checkbox\n3. In "Options", set a output folder, mod name and check "load order priority" and "join files".\n4. Convert All'
    self.tabClasses[-1].separateStart=False
    self.tabClasses[-1].singleEntryCheck="Helper File"

    self.newTab("Create Upgraded Buildings - Trigger files",createUpgradedBuildings,("text files","*.txt"),["--just_copy_and_check"]
      ,BUOptions,"")
    self.tabClasses[-1].helpText='Add any files that have "has_building" in your mod here. Give them each the right path to go to. And convert. This has to be done AFTER the main BU and into the same folder!'
    self.tabClasses[-1].subfolder=True

    self.newTab("Copy Subtag To Other Mod",copySubTag,("text files","*.txt"),[],[of,"tag_to_be_copied",oll],"Add Source File(s)")
    self.tabClasses[-1].helpText="Not finished yet!" #createUpgradedBuildings - Trigger files
    self.tabClasses[-1].separateStart=False
    self.tabClasses[-1].singleEntryCheck="Source File"

    #self.newTab("Create AI Vars",createAIVarsFromModifiers,("text files","*.txt"),[],[of,"effect_name","type",oll],"")
    #self.tabClasses[-1].helpText="Creates weight files to be used in AI buiding weights. Since options are global, it's best to create one 'project' for different tpyes, e.g. one for planet modifiers, one for buildings, one for blocker"


    nb.pack(expand=1, fill="both")  # Pack to make visible
  def newTab(self,name, command, fileFilter, fixedOptions, options, extraAddButton):
    frame=ttk.Frame(self.root)
    self.nb.add(frame,text=name)
    optionClasses=[]
    for option in options:
      optionClasses.append(Option(option))
    optionWindow=OptionWindow(self.root,name+" Options",optionClasses,command)
    self.tabClasses.append(TabClass(name,frame,self.root,command,fixedOptions, fileFilter,optionWindow,extraAddButton))

  def getActiveTabClass(self):
    return self.tabClasses[self.nb.index(self.nb.select())]
  def save(self):
    self.getActiveTabClass().save()
  def load(self):
    tab=self.getActiveTabClass()
    if (len(tab.lines)==0) or messagebox.askquestion("Overwrite", "This will overwrite current content. Are you sure?", icon='warning') == 'yes':
      self.getActiveTabClass().load()  
  def loadAdd(self):
    self.getActiveTabClass().loadAdd()

def repeatedChecks(tabClasses, root):
  for tab in tabClasses:
    tab.checkValid()
  root.after(100, lambda:repeatedChecks(tabClasses,root))

def about():
  #window=tk.Toplevel(root)
  print("Created by Gratak for Stellaris")
  print("Feel free to use for your mod project but please mention me including the links to my mods ")
  print("http://steamcommunity.com/profiles/76561198087073498/myworkshopfiles")
  print("and our git repository:")
  print("https://github.com/Goldziher/ExOverhaul")
  
def help(tabControl):
  #window=tk.Toplevel(root)
  print("Help for '"+str(tabControl.getActiveTabClass().name)+"':")
  print(tabControl.getActiveTabClass().helpText)
  print("For more help, visit:")
  print("https://discord.gg/mVerKF5")
  parser=tabControl.getActiveTabClass().command.parse([],True)
  for a in parser._actions:
    v=vars(a)
    if "--cost_discount" in v['option_strings']:
      print(v["help"])
  # try:
  #   tabControl.getActiveTabClass().command.parse(["-h"])
  # except:
  #   pass
  
def main():
  root = Tk()
  root.title("Stellaris Python Script Helper")
  screen_width = root.winfo_screenwidth()
  screen_height = root.winfo_screenheight()
  root.geometry("{!s}x{!s}".format(1400,screen_height*2//3))
  # create a toplevel menu
  menubar = Menu(root)

  # create a pulldown menu, and add it to the menu bar
  filemenu = Menu(menubar, tearoff=0)
  tabControl=TabControlClass(root)
  
  
  filemenu.add_command(label="Load Current Tab", command=tabControl.load)
  filemenu.add_command(label="Load Current Tab (add files, no options changed)", command=tabControl.loadAdd)
  filemenu.add_command(label="Save Current Tab", command=tabControl.save)
  filemenu.add_separator()
  filemenu.add_command(label="Exit", command=root.quit)
  menubar.add_cascade(label="File", menu=filemenu)

  # create more pulldown menus
  #editmenu = Menu(menubar, tearoff=0)
  #editmenu.add_command(label="Cut", command=hello)
  #editmenu.add_command(label="Copy", command=hello)
  #editmenu.add_command(label="Paste", command=hello)
  #menubar.add_cascade(label="Edit", menu=editmenu)

  helpmenu = Menu(menubar, tearoff=0)
  helpmenu.add_command(label="About", command=about)
  helpmenu.add_cascade(label="Help", command=lambda:help(tabControl))  
  # helpmenu.add_command(label="About", command=lambda:about(root))
  # helpmenu.add_cascade(label="Help", command=lambda:help(root))
  menubar.add_cascade(label="Help", menu=helpmenu)

  # display the menu
  root.config(menu=menubar)

  if os.path.exists("python.ico") and platform.system()=='Windows':
    root.iconbitmap('python.ico')
        # root.iconbitmap(os.path.abspath("python.ico"))



  
  #b = tk.Button(tabClasses[0].scrollFrame, text="hide", command=optionWindow.window.withdraw)
  #b.pack(side=tk.TOP)
  #b = tk.Button(tabClasses[0].scrollFrame, text="show", command=optionWindow.window.deiconify)
  #b.pack(side=tk.TOP)
  


  sys.stdout = Logger(tabControl) #ensures output goes to right tab and console
  sys.stderr = Logger(tabControl,True) #ensures output goes to right tab and console

  root.minsize(1000, 0)
  root.after(5, lambda:repeatedChecks(tabControl.tabClasses,root))
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