#!/usr/bin/env python
'''
Written by Greg Meyer and Allison Hsiang
'''

from __future__ import division

import Tkinter as tk
import tkMessageBox
import csv
from os.path import isfile,splitext
from os import getcwd, listdir, system, chdir
import myTkObjects as mtk
from string import lowercase
from PIL import ImageTk, Image
import tkFileDialog
import glob


class GUI:

    def __init__(self,root):

        self.root = root
        self.scan = ''
        self.ext = ''
        self.data = {}

        # check if restarting from existing file
        self.files_in_dir = glob.glob('*classification*')

        if len(self.files_in_dir) >= 1:
            if tkMessageBox.askyesno('Classify','Classify file exists; load and continue from last object?'):
                if len(self.files_in_dir) == 1:
                    self.filename = self.files_in_dir[0]
                else:
                    tkMessageBox.showerror('Classify','Multiple Classify files exist; please choose which file you would like to load.')
                    self.filename = tkFileDialog.askopenfilename()

                f = open(self.filename)
                reader = csv.reader(f)

                # get image extension from file
                line1 = reader.next()
                line2 = reader.next()
                self.ext = splitext(line2[0])[1]

                num_rows = sum(1 for row in reader)
                self.image_ind = num_rows + 1
                self.append = True
                print 'Restarting from file.'
                self.setup_data_entry()
                
            else:
                self.image_ind = 0
                self.append = False
                self.get_scan_name()
        else:
            self.image_ind = 0
            self.append = False
            self.get_scan_name()


    def get_scan_name(self):

        def set_scan_name(event=None):
            if self.scan_in.get().strip() == "":
                tkMessageBox.showerror("Classify", "Enter a scan name.")
            elif self.ext_in.get().strip() == "":
                tkMessageBox.showerror("Classify", "Enter an image file extension.")
            else:
                self.scan = self.scan_in.get().strip()
                self.ext = self.ext_in.get().strip()
                print 'Scan name set to \'' + self.scan + '\''
                print 'File extension set to \'' + self.ext + '\''
                self.frame.destroy()
                self.frame2.destroy()
                del self.scan_in, self.ext_in, self.submit
                self.setup_data_entry()

        # get the scan name from the user
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.scan_input_text = mtk.Title(self.frame,text='Enter scan name:')
        self.scan_input_text.pack()

        self.scan_in = mtk.Entry(self.frame)
        self.scan_in.insert(0, self.scan)
        self.scan_in.pack()

        # Get file extension from user
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack()

        self.ext_input_text = mtk.Title(self.frame2,text="Enter file extension:")
        self.ext_input_text.pack()

        self.ext_in = mtk.Entry(self.frame2)
        self.ext_in.insert(0,self.ext)
        self.ext_in.pack()

        self.submit = mtk.Button(self.frame2,text='Done',command=set_scan_name)
        self.submit.pack()


##    def get_screen_size(self):
##        self.w = self.root.winfo_screenwidth()
##        self.h = self.root.winfo_screenheight()
##        return self.w,self.h


    def display_image(self):
        self.image_window = tk.Toplevel()
        self.image_window.geometry('+370+100')
        self.iw_frame = tk.Frame(self.image_window)

        # Open image and resize so that maximum width is 500px and aspect ratio is maintained
        self.img_original = Image.open(self.image_list[self.image_ind])
        self.size_original = self.img_original.size
        if self.size_original[0] > 500:
            self.ratio = 500 / self.size_original[0]
            self.img_resized = self.img_original.resize((500,int(self.size_original[1] * self.ratio)),Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.img_resized)
        else:
            self.img = ImageTk.PhotoImage(self.img_original)

        # Display image
        self.panel = tk.Label(self.image_window,image=self.img)
        self.panel.pack(side="bottom")


    def display_object_name(self):
        self.object_name = tk.Toplevel()
        self.object_name.geometry('+900+100')

        self.name = mtk.Message(self.object_name,text=str(self.image_ind + 1) + '/' + str(self.num_objects) + ': '+ self.image_list[self.image_ind])
        self.name.pack()


    def setup_data_entry(self):
        self.image_list = [x for x in listdir('.') if splitext(x)[1] == self.ext or splitext(x)[1][1:] == self.ext]
        self.num_objects = len(self.image_list)

        self.display_image()
        self.display_object_name()

        #root.wm_attributes("-topmost", 1)
        #root.focus_force()

        def make_selection_fn(new_selection):

            def _f(event=None):

                if self.selection is not None:
                    self.buttons[self.selection].unSet()
                self.selection = new_selection

                if self.buttons[self.selection].state != 'down':
                    self.buttons[self.selection].set()

            return _f

        self.selection = None
        self.confidence = None

        self.frame = tk.Frame(self.root)
        self.frame.pack(side="left")
        self.buttons = {}

        planktonic = ['complete','fragment','damaged']
        nonplankton = ['benthic','mollusk','ostracod','rock','junk image']
        other = ['echinoid spine','radiolarian','spicule','tooth','clipped image','unknown']
        colors = ['green','gray','dark blue']
        keys = lowercase

        button_count = 0

        for m,lst in enumerate([planktonic,nonplankton,other]):
            for n,name in enumerate(lst):
                self.buttons[name] = mtk.Button(self.frame,
                    text=keys[button_count]+'. '+name,
                    command=make_selection_fn(name),
                    color=colors[m],
                    staydown=True)
                self.buttons[name].pack()
                # attach key to button
                self.frame.bind_all(keys[button_count],make_selection_fn(name))
                button_count += 1

        self.confidence_label = mtk.Title(self.frame,text='Confidence:')
        self.confidence_label.pack()

        def make_confidence_callback(conf):

            def _f(event=None):

                if not self.selection:
                    tkMessageBox.showerror("Fragment", "Choose a type first!")

                if self.confidence is not None:
                    self.buttons[conf].unSet()

                self.confidence = conf
                self.next_image()

            return _f

        confidence = ['very','somewhat','not']
        conf_keys = ['1','2','3']
        for n,name in enumerate(confidence):
            # fix command here
            self.buttons[name] = mtk.Button(self.frame,
                text=conf_keys[n]+'. '+name,
                color='light gray',
                command=make_confidence_callback(name),
                staydown=True)
            self.frame.bind_all(conf_keys[n],make_confidence_callback(name))
            self.buttons[name].pack()


    def next_image(self):

        obj_num = self.image_list[self.image_ind].split('_')[1]
        self.data[ obj_num ] = ( self.selection, self.confidence )

        self.buttons[self.selection].unSet()
        self.buttons[self.confidence].unSet()
        self.selection = self.confidence = None

        self.write_data()

        self.image_ind += 1

        if self.image_ind == len(self.image_list):
            tkMessageBox.showinfo('Classify','All done!')
            self.root.quit()
            return

        self.image_window.destroy()
        self.object_name.destroy()

        self.display_image()
        self.display_object_name()

        #self.root.wm_attributes("-topmost", 1)
        #self.root.focus_force()


    def write_data(self):
        if self.append:
            f = open(self.filename,'ab')
            writer = csv.writer(f)
            obj = sorted(self.data.keys())[-1]
            writer.writerow([obj,self.data[obj][0],self.data[obj][1]])
        else:
            self.filename = self.scan + '_classification.csv'
            f = open(self.filename,'wb')
            f.write('object,id,confidence\n')
            writer = csv.writer(f)
            for obj in sorted(self.data.keys()):
                writer.writerow([obj,self.data[obj][0],self.data[obj][1]])

        f.close()



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Classify')
    root.update() # Inexplicable fix for hanging file dialog window and images not appearing

    # get directory of images from user
    image_dir = tkFileDialog.askdirectory()
    chdir(image_dir)

    app = GUI(root)
    root.mainloop()
