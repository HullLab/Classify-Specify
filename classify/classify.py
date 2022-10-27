#!/usr/bin/env python
'''
Written by Greg Meyer and Allison Hsiang
'''

from __future__ import division

import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import csv
from os.path import isfile,splitext
from os import getcwd, listdir, system, chdir, remove
import myTkObjects as mtk
import string
from PIL import ImageTk, Image
import glob


class GUI:
    def __init__(self,root):
        self.root = root
        self.scan = ''
        self.ext = ''
        self.data = {}
        self.start_from_beginning = None

        # Check if restarting from existing file
        self.files_in_dir = glob.glob('*classification*')

        if len(self.files_in_dir) >= 1: # Restart file exists
            if tkinter.messagebox.askyesno('Classify','Classify file exists; load and continue from last object?'):
                if len(self.files_in_dir) == 1:
                    self.filename = self.files_in_dir[0]
                else:
                    tkinter.messagebox.showerror('Classify','Multiple Classify files exist; please choose which file you would like to load.')
                    self.filename = tkinter.filedialog.askopenfilename()

                # Get image extension from file
                with open(self.filename, 'r') as f:
                    lines = f.readlines()
                    self.ext = splitext(lines[1].split(',')[0])[1]
                    num_rows = len(lines) - 1

                    if num_rows == 0: # Exception for empty file
                        print( 'File is empty. Restarting from scratch.' )
                        remove(self.filename)
                        self.start_from_beginning = True
                    else:
                        print( 'Restarting from file.' )
                        self.image_ind = num_rows
                        self.append = True
                        self.setup_data_entry()

            else: # Don't load existing file (user inputs "no")
                self.start_from_beginning = True

        else: # Restart file doesn't exist
            self.start_from_beginning = True

        # Start classification from scratch
        if self.start_from_beginning:
            self.image_ind = 0
            self.append = False
            self.get_scan_name()


    def get_scan_name(self):
        def set_scan_name(event=None):
            if self.scan_in.get().strip() == "":
                tkinter.messagebox.showerror("Classify", "Enter a scan name.")
            elif self.ext_in.get().strip() == "":
                tkinter.messagebox.showerror("Classify", "Enter an image file extension.")
            else:
                self.scan = self.scan_in.get().strip()
                self.ext = self.ext_in.get().strip()
                print( 'Scan name set to \'' + self.scan + '\'' )
                print( 'File extension set to \'' + self.ext + '\'' )
                self.frame.destroy()
                self.frame2.destroy()
                del self.scan_in, self.ext_in, self.submit
                self.setup_data_entry()

        # Get the scan name from the user
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

        # Confirm button
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


    def display_undo_button(self):
        if self.image_ind == 0:
            try:
                self.undo_frame.destroy()
            except:
                pass
        else:
            self.undo_frame = tk.Toplevel()
            self.undo_frame.geometry('+900+200')
            self.undo_button = tk.Button(self.undo_frame,text='Undo',width=20,pady=2,height=1,bd=2,command=self.previous_image)
            self.undo_button.pack()


    def setup_data_entry(self):
        self.image_list = sorted([x for x in listdir('.') if splitext(x)[1] == self.ext or splitext(x)[1][1:] == self.ext])
        self.num_objects = len(self.image_list)

        self.display_image()
        self.display_object_name()
        self.display_undo_button()

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
        keys = string.ascii_lowercase

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
                    tkinter.messagebox.showerror("Fragment", "Choose a type first!")

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
        # Save previous selections
        obj_name = self.image_list[self.image_ind]
        self.data[ obj_name ] = ( self.selection, self.confidence )

        # Reset buttons
        self.buttons[self.selection].unSet()
        self.buttons[self.confidence].unSet()
        self.selection = self.confidence = None

        # Write selections to file
        if self.image_ind > 0:
            self.append = True
        self.write_data(obj_name)
        self.image_ind += 1

        # Display message and quit if all images complete
        if self.image_ind == len(self.image_list):
            if tkinter.messagebox.askyesno('Classify','All done! Exit program?'):
                self.root.quit()
                return
            else:
                return

        # Close windows for previous object
        self.image_window.destroy()
        self.object_name.destroy()
        try:
            self.undo_frame.destroy()
        except:
            pass

        # Display windows for next object
        self.display_image()
        self.display_object_name()
        self.display_undo_button()


    def previous_image(self):
        # Move image index back by one (unless first image)
        if self.image_ind == 0:
            self.undo_frame.destroy()
            print( 'You are at the first image; cannot undo!' )
        else:
            self.image_ind -= 1

        # Reset buttons if necessary
        try:
            self.buttons[self.selection].unSet()
        except:
            pass
        self.selection = self.confidence = None

        # Close windows of current object
        self.image_window.destroy()
        self.object_name.destroy()
        try:
            self.undo_frame.destroy()
        except:
            pass

        # Display windows of previous object
        self.display_image()
        self.display_object_name()
        self.display_undo_button()

        # Save selections for previous object
        obj_name = self.image_list[self.image_ind]
        self.data[ obj_name ] = ( self.selection, self.confidence )

        # Rewrite previously saved selections for previous object
        self.rewrite_data()


    def rewrite_data(self):
        lines = open(self.filename).readlines()
        f = open(self.filename,'w').writelines(lines[:-1])


    def write_data(self, obj=None):
        if self.append: # Write to existing file
            f = open(self.filename,'a')
            writer = csv.writer(f)
            writer.writerow([obj,self.data[obj][0],self.data[obj][1]])
        else: # Initialize and write to new file
            self.filename = self.scan + '_classification.csv'
            f = open(self.filename,'w')
            f.write('object,id,confidence\n')
            writer = csv.writer(f)
            #for obj in sorted(self.data.keys()):
            writer.writerow([obj,self.data[obj][0],self.data[obj][1]])

        f.close()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Classify')
    root.update() # Inexplicable fix for hanging file dialog window and images not appearing

    # get directory of images from user
    image_dir = tkinter.filedialog.askdirectory()
    chdir(image_dir)

    app = GUI(root)
    root.mainloop()
