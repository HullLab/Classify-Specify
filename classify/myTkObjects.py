#!/usr/bin/env python
'''
Written by Greg Meyer
'''

import tkinter as tk
import tkinter.font
import string

FONT_FAMILY = ''

class Button( tk.Text, object ):

	def __init__(self,master,text='',command=None,color='green',disabled=False,staydown=False,down=False,*args,**kwargs):

		tk.Text.__init__(self,master,*args,**kwargs)

		self.tag_configure("center", justify='center')
		self.insert(tk.END,text,"center")
		self.command = command
		self.disabled = disabled
		self.state = 'inactive'
		self.staydown = staydown
		self.down = down
		if self.down and not self.staydown:
			raise Exception('Can\'t start down if staydown flag is False!')

		if color == 'green':
			self.bg = 'dark green'
			self.fg = 'papaya whip'
			self.activeColor = 'forest green'
			pass
		elif color == 'gray':
			self.bg = 'gray30'
			self.fg = 'papaya whip'
			self.activeColor = 'gray45'
			self.highlight = 'light sky blue'
			self.disabledFg = 'slate gray'
			self.disabledBg = 'gray20'
			pass
		elif color == 'light gray':
			self.bg = 'gray70'
			self.fg = 'dark slate gray'
			self.activeColor = 'gray85'
			self.disabledFg = 'slate gray'
			self.disabledBg = 'gray78'
		elif color == 'dark blue':
			self.bg = 'navy'
			self.fg = 'light sky blue'
			self.activeColor = 'RoyalBlue4'
		else:
			raise Exception(color+' is not a valid color.')
			pass

		self.config(
			font=(FONT_FAMILY,20),
			state='disabled',
			cursor='arrow',
			height=1,
			relief='flat',
			bd=2,
			width=20,
			pady=2,
			highlightthickness=2,
			highlightcolor=self.bg,
			highlightbackground=self.bg,
			)
		if self.disabled:
			self.config(
				bg=self.disabledBg,
				fg=self.disabledFg,
				)
		else:
			self.config(
				bg=self.bg,
				fg=self.fg,
				)
		self.config(*args,**kwargs)

		if not self.disabled:
			self.bind('<Enter>',self._MouseIn)
			self.bind('<Leave>',self._MouseOut)
			self.bind('<Button-1>',self._MouseDown)
			self.bind('<ButtonRelease-1>',self._MouseUp)
			pass

		self.mouse = {
			'in':False,
			'down':False
		}

		self.active = False

	def _MouseIn(self,event):

		#print 'Mouse in.'
		self.mouse['in'] = True
		self.config(bg=self.activeColor,)
		if not self.active:
			self.config(highlightcolor=self.activeColor,highlightbackground=self.activeColor)
		if self.state == 'clicking':
			self.config(relief='sunken')
		pass

	def _MouseOut(self,event):

		#print 'Mouse out.'
		self.mouse['in'] = False
		if not self.staydown:
			self.config(relief='flat')
		self.config(bg=self.bg,)
		if not self.active:
			self.config(highlightcolor=self.bg,highlightbackground=self.bg)
		pass

	def _MouseDown(self,event):

		#print 'Mouse down.'
		self.mouse['down'] = True
		if self.mouse['in']:
			self.config( relief='sunken' )
			self.state = 'clicking'
			pass
		else:
			if not self.staydown:
				self.config( relief='flat' )
			elif self.state == 'down':
				self.config( relief='sunken')
		pass

	def _MouseUp(self,event):

		#print 'Mouse up.'
		self.mouse['down'] = False
		if not self.staydown:
			self.config(relief='flat')
		if self.mouse['in']:
			if self.staydown:
				self.state = 'down'
			else:
				self.state = 'active'
			pass
		else:
			self.state = 'inactive'
			pass
		if self.mouse['in'] and self.command:
			self.command( event )
			pass
		pass

	def unSet(self):

		if not self.staydown:
			raise Exception('Can\'t call unSet on a button without staydown=True.')

		self.state = 'inactive'
		self.config( relief = 'flat')

	def set(self):

		self.state = 'down'
		self.config( relief = 'sunken' )

	def makeActive(self):

		self.active = True

		self.config(highlightcolor=self.highlight)
		self.config(highlightbackground=self.highlight)
		pass

	def makeInactive(self):

		self.active = False

		self.config(highlightcolor=self.bg)
		self.config(highlightbackground=self.bg)

		pass

	def disable(self):

		self.config(
				bg=self.disabledBg,
				fg=self.disabledFg,
				)

		self.unbind('<Enter>',)
		self.unbind('<Leave>',)
		self.unbind('<Button-1>',)
		self.unbind('<ButtonRelease-1>',)

	def enable(self):

		self.config(
				bg=self.bg,
				fg=self.fg,
				)

		self.bind('<Enter>',self._MouseIn)
		self.bind('<Leave>',self._MouseOut)
		self.bind('<Button-1>',self._MouseDown)
		self.bind('<ButtonRelease-1>',self._MouseUp)

	def changeText(self, newtext):

		self.config(state='normal')
		self.delete(1.0,tk.END)
		self.insert(tk.END,newtext,"center")
		self.config(state='disabled')


	def pack(self,*args,**kwargs):

		kwargs['fill'] = 'x'

		super(Button,self).pack(*args,**kwargs)
		pass



class Entry( tk.Entry, object ):

	def __init__(self,master,text='',default_text=True,isPassword=False,*args,**kwargs):

		tk.Entry.__init__(self,master,*args,**kwargs)

		self.bg='light sky blue'
		self.default_text = default_text

		self.config(
			font=(FONT_FAMILY,20),
			width=20,
			relief='flat',
			bg='light sky blue',
			highlightthickness=2,
			highlightcolor=self.bg,
			highlightbackground=self.bg,
			fg='dodger blue',
			)
		self.config(
			*args,
			**kwargs
			)


		self.text = text
		self.empty = not default_text
		self.insert(tk.END,self.text)
		if self.default_text:
			self.config(fg='navy')

		self.bind('<FocusIn>', self.FocusIn )
		self.bind('<FocusOut>', self.FocusOut )

	def FocusIn( self, event ):

		if self.empty:
			self.delete(0,tk.END)
			self.config(fg='navy')
			self.empty = False

		pass

	def FocusOut( self, event ):

		if not self.get():

			self.empty = True

			if not self.default_text:
				self.config(fg='dodger blue')
				self.insert(tk.END,self.text)

		else:

			self.empty = False
			pass

	# FUNCTIONS FOR EXTERNAL USE

	def pack(self,*args,**kwargs):

		if not 'ipady' in kwargs.keys():
			kwargs['ipady'] = 5
			pass

		kwargs['fill'] = 'x'

		super(Entry,self).pack(*args,**kwargs)
		pass

	def get(self,*args,**kwargs):

		if self.empty:
			return ''
		else:
			return super(Entry,self).get(*args,**kwargs)
			pass


class Title( tk.Text ):

	def __init__(self,master,text='',**options):

		tk.Text.__init__(self,master,**options)

		self.tag_configure("center", justify='center')
		self.insert(tk.END,text,"center")

		self.bg='old lace'

		self.config(
			font=(FONT_FAMILY,25),
			state='disabled',
			cursor='arrow',
			height=1,
			relief='flat',
			bd=1,
			width=20,
			pady=10,
			bg='old lace',
			highlightthickness=2,
			highlightcolor=self.bg,
			highlightbackground=self.bg,
			fg='OrangeRed4',
			)


class Message( tk.Text, object ):

	def __init__(self,master,text='',*args,**kwargs):

		tk.Text.__init__(self,master,*args,**kwargs)

		self.tag_configure("center", justify='center')
		self.insert(tk.END,text,"center")

		self.bg='old lace'

		self.config(
			font=(FONT_FAMILY,15),
			state='disabled',
			cursor='arrow',
			relief='flat',
			bd=1,
			height=1,
			width=30,
			bg='old lace',
			highlightthickness=2,
			highlightcolor=self.bg,
			highlightbackground=self.bg,
			fg='OrangeRed4',
			)
		self.config(*args,**kwargs)

	def pack( self,*args,**kwargs ):

		kwargs[ 'fill' ] = 'x'

		super(Message,self).pack(*args,**kwargs)


class DoubleButton( tk.Frame, object):

	def __init__(self, master, leftText='', rightText='', leftCommand=None, rightCommand=None, leftDisabled=True, rightDisabled=False, width=20,):

		self.master = master

		color='light gray'

		tk.Frame.__init__(self, self.master, borderwidth=0) # this is only OK for light gray... yeah

		self.button0 = myButton(self, width=width/2, color=color, text=leftText, command=leftCommand, highlightthickness=0, bd=1, disabled=leftDisabled)
		self.button0.pack(side='left',fill='x',expand=True)

		self.button1 = myButton(self, width=width/2, color=color, text=rightText, command=rightCommand, highlightthickness=0, bd=1, disabled=rightDisabled)
		self.button1.pack(side='left',fill='x',expand=True)

		pass

	def SetLeftDisabled(self, val = True):

		if val:
			self.button0.disable()
			#print 'disable left'
			pass
		else:
			self.button0.enable()
			#print 'enable left'
			pass

		return

	def SetRightDisabled(self, val = True):

		if val:
			self.button1.disable()
			#print 'disable right'
			pass
		else:
			self.button1.enable()
			#print 'enable right'
			pass


class WarningManager( tk.Frame, object ):

	def __init__(self, master):

		self.master = master

		tk.Frame.__init__(self,self.master,height=0)

		self.warnings = {}

	# show a new warning
	def displayWarning(self, name, text):

		# if this one already exists, it is cleared and replaced.
		if name in self.warnings.keys():
			self.warnings[ name ].pack_forget()
			self.warnings[ name ].destroy()
			pass

		numLines = text.count('\n') + 1

		self.warnings[ name ] = myMessage( self, text = text, height = numLines)
		self.warnings[ name ].pack(fill='x')

		if not self.winfo_ismapped():
			self._myPack()
			pass

	# clear warning with name 'name'
	def clear(self, name):

		if not name in self.warnings.keys():

			raise Exception('There is no warning with name \''+name+'\'.')

		self.warnings[ name ].pack_forget()
		self.warnings[ name ].destroy()

		self.warnings.pop( name )

		if not self.warnings:
			self.pack_forget()
			pass


	# try to clear warning with name 'name', if it doesn't exist, that's fine.
	def tryClear(self, name):

		if not name in self.warnings.keys():

			return

		self.warnings[ name ].pack_forget()
		self.warnings[ name ].destroy()

		self.warnings.pop( name )

		if not self.warnings:
			self.pack_forget()
			pass


	# clear all warnings present.
	def clearAll(self):

		for child in self.winfo_children():
			child.pack_forget()
			child.destroy()

		self.warnings = {}

		self.pack_forget()


	def _myPack(self):

		if self.packing:
			super(myWarningManager,self).pack(*self.pack_args,**self.pack_kwargs)
			pass

		return


	def pack(self,*args,**kwargs):

		self.pack_args = args
		self.pack_kwargs = kwargs

		self.packing = True
