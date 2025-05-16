#Shebang
#encoding 

#root.tk.call('tk', 'windowingsystem') = 'x11'

from tkinter import *
from tkinter import ttk


class ViewTranscript:
	
	def __init__(self,root,q2):
		self.root=root
		self.transcriptQ = q2
		self.transcriptionStarted = None
		self.endprogFlag = False
		root.title("Voice to Text - View")
		
		mainFr = ttk.Frame(root,borderwidth=4,relief='ridge')
		self.txtV = Text(mainFr,width=90,height=30,borderwidth=4,relief='groove',wrap='word')
		txtYScroll = ttk.Scrollbar(mainFr, orient='vertical',command = self.txtV.yview)
		self.txtV['yscrollcommand'] = txtYScroll.set
		self.showBut = ttk.Button(mainFr,text='Show',command = self.transcript_insert)
		endBut = ttk.Button(mainFr,text='EndProgram',command = self.root.destroy())
		
		mainFr.grid(row=0,column=0)
		
		self.txtV.grid(row=0,column=0,columnspan=3,sticky=(N,W,E,S))
		txtYScroll.grid(row=0,column=1,sticky=(N,S))
		self.showBut.grid(row=1,column=0)
		endBut.grid(row=1,column=1)
		root.grid_columnconfigure(0,weight=1)
		root.grid_rowconfigure(0,weight=1)
		mainFr.columnconfigure(0,weight=1)
		mainFr.rowconfigure(0,weight=1)

	def endprog(self,*args):
		self.endprogFlag = True
		self.root.after(600)
		self.root.destroy()
	
	def transcript_insert(self,*args):
		self.transcriptionStarted = True
		self.showBut['text'] = 'CantUseShowinProgress'
		self.showBut['state'] = 'disabled'
		transcript = StringVar()
		tsStr=''
		try:
			while not self.transcriptQ.empty():
				tsStr.join(self.transcriptQ.get())
			if len(tsStr) > 30:
				self.txtV['state'] = 'normal'
				self.txtV.insert('end',tsStr)
				self.txtV['state'] = 'disabled'
				tsStr=''
			finally:
				self.txtV['state'] = 'normal'
				self.txtV.insert('end',tsStr)
				tsStr=''
				self.txtV['state'] = 'disabled'
				self.showBut['state'] = 'normal'
				self.showBut['text'] = 'Show'
'''
root = Tk()
ViewTranscript(root,q2)
root.mainloop()
'''
