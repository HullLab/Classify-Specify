#!/usr/bin/env python
'''
Original version written by Greg Meyer.
Updated and maintained by Allison Hsiang.
'''

from __future__ import division

import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import csv
from os.path import isfile,splitext
from os import getcwd, listdir, system, chdir, remove, linesep
import myTkObjects as mtk
import string
from PIL import ImageTk, Image
import glob
from datetime import datetime


class GUI:
    def __init__(self,root):
        self.root = root

        # Get screen size
        self.screensize = self.get_screen_size()
        self.x = self.screensize[0]
        self.y = self.screensize[1]

        # Config window
        self.config = tk.Toplevel(root)
        self.config.geometry('+{:.0f}+{:.0f}'.format(int(self.x * 0.15), 0)) # POSITION configuration window
        self.config.title('Configuration')

        # Console window
        self.console = tk.Listbox(root, width=25)
        self.console_idx = 1
        self.console.insert(self.console_idx, "Welcome to Classify!")
        self.console.pack(fill=tk.X, expand=True)

        # Important variables
        self.scan = ''
        self.ext = ''
        self.data = {}
        self.start_from_beginning = None
        self.filename = ''

        # Set up configuration
        self.update_console(self.console_idx, "Please configure this session.")
        self.configuration()


    def update_console(self, idx, message):
        self.console_idx += 1
        self.console.insert(self.console_idx, message)
        self.console.pack()

    
    def checkpoint(self):
        # Check if restarting from existing file
        self.files_in_dir = glob.glob('*classification*')
        
        if len(self.files_in_dir) >= 1: # Restart file exists
            if tkinter.messagebox.askyesno('Classify','Classify file exists.' + linesep + 'Load and continue from last object?'):
                if len(self.files_in_dir) == 1:
                    self.filename = self.files_in_dir[0]
                else:
                    tkinter.messagebox.showerror('Classify','Multiple Classify files exist.' + linesep + 'Please choose which file you would like to load.')
                    self.filename = tkinter.filedialog.askopenfilename()
        
                # Parse existing file
                with open(self.filename, 'r') as f:
                    lines = f.readlines()
                    num_rows = len(lines) - 1
        
                if num_rows == 0: # Exception for empty file
                    self.update_console(self.console_idx, 'File is empty.' + linesep + 'Restarting from scratch.')
                    remove(self.filename)
                    self.start_from_beginning = True
                else:
                    self.update_console(self.console_idx, 'Restarting from file.')
                    self.image_ind = num_rows
                    self.append = True
                    self.start_from_beginning = False
        
            else: # Don't load existing file (user inputs "no")
                self.start_from_beginning = True
        
        else: # Restart file doesn't exist
            self.start_from_beginning = True

        # Start classification from scratch
        if self.start_from_beginning:
            self.image_ind = 0
            self.append = False


    def start(self):
        # Checkpointing
        self.checkpoint()

        # Start data entry process
        self.setup_data_entry()


    def get_screen_size(self):
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        return (self.w, self.h)


    def configuration(self):
        def end_config(event=None):
            # Change to user-input directory
            chdir(self.input_dir_path)
            
            # Check that scan name and image extensions are properly set
            if self.scan_in.get().strip() == '':
                tkinter.messagebox.showerror('Classify', 'Enter a scan name.')
                self.update_console(self.console_idx, 'Scan name missing.')
            elif self.ext_in.get().strip() == '':
                tkinter.messagebox.showerror('Classify', 'Enter an image file extension.')
                self.update_console(self.console_idx, 'File extension missing.')
            else:
                self.scan = self.scan_in.get().strip()
                self.ext = self.ext_in.get().strip()
                if self.cv.get() == 0:
                    self.update_console(self.console_idx, 'Default categories specified.')
                self.update_console(self.console_idx, 'Scan name set to \'' + self.scan + '\'.')
                self.update_console(self.console_idx, 'File extension set to \'' + self.ext + '\'.')
                del self.scan_in, self.ext_in, self.submit
                self.start_from_beginning = True

            # Destroy config window
            self.config.destroy()

            # Start the program
            self.start()

        def load_dir(event=None):
            self.input_dir_path = tkinter.filedialog.askdirectory()
            self.input_dir_label.config(text=self.input_dir_path, wraplength=300)
            self.input_dir_label.pack()
            self.update_console(self.console_idx, 'Input directory set to \'' + self.input_dir_path + '\'.')

        def load_class_file(event=None):
            self.class_file_path = tkinter.filedialog.askopenfilename()
            self.class_file_label.config(text=self.class_file_path, wraplength=300)
            self.class_file_label.pack()
            self.update_console(self.console_idx, 'User-specified category file set to \'' + self.class_file_path + '\'')

        def update_class_button():
            ### Activates/deactivates class file button and selected file label
            if self.cv.get():
                self.load_class_file.enable()
                self.frame4 = tk.Frame(master=self.config) # Class file label
                self.frame4.grid(row=6, column=0) 
                self.class_file_label = tkinter.Label(master=self.frame4)
                self.class_file_label.pack()
            else:
                self.load_class_file.disable()
                self.frame4.grid_forget()
                if self.class_file_path:
                    self.update_console(self.console_idx, 'Default categories specified.')

        # Get input directory
        self.frame = tk.Frame(master=self.config) 
        self.frame.grid(row=0, column=0) # Input title
        self.input_dir_text = mtk.Title(master=self.frame, text='Input Directory').pack()

        self.frame.grid(row=1, column=0) # Load directory button
        self.input_dir = mtk.Button(master=self.frame, text='Select', color='gray', command=load_dir).pack()

        self.frame.grid(row=2, column=0) # Directory label
        self.input_dir_label = tkinter.Label(master=self.frame)

        # Get class setting/input
        self.class_file_path = None

        self.frame2 = tk.Frame(master=self.config)

        self.frame2.grid(row=3, column=0) # Class title
        self.input_dir_text = mtk.Title(master=self.frame2, text='Classes').pack()

        self.frame2.grid(row=4, column=0) # Radio buttons
        self.cv = tk.IntVar()
        self.cv.set(0)
        self.button1 = tk.Radiobutton(master=self.frame2, text='Default', value=0, command=update_class_button, variable=self.cv).pack()
        self.button2 = tk.Radiobutton(master=self.frame2, text='User-defined', value=1, command=update_class_button, variable=self.cv).pack()

        self.frame3 = tk.Frame(master=self.config) # Load class file button
        self.frame3.grid(row=5, column=0)
        self.load_class_file = mtk.Button(master=self.frame3, text='Load Class File', color='gray', disabled=True, command=load_class_file)
        self.load_class_file.pack()

        # Get scan name from user
        self.frame5 = tk.Frame(master=self.config)
        self.frame5.grid(row=7, column=0) # Scan name title
        self.scan_input_text = mtk.Title(self.frame5,text='Enter scan name:').pack()

        self.frame5.grid(row=8, column=0) # Input panel
        self.scan_in = mtk.Entry(self.frame5)
        self.scan_in.insert(0, self.scan)
        self.scan_in.pack()
        
        # Get file extension from user
        self.frame6 = tk.Frame(master=self.config)
        self.frame6.grid(row=9, column=0) # File ext title
        self.ext_input_text = mtk.Title(self.frame6,text="Enter file extension:").pack()
        
        self.frame6.grid(row=10, column=0) # Input panel
        self.ext_in = mtk.Entry(self.frame6)
        self.ext_in.insert(0,self.ext)
        self.ext_in.pack()
        
        # Confirm button
        self.frame7 = tk.Frame(master=self.config)
        self.frame7.grid(row=11, column=0)
        self.submit = mtk.Button(self.frame7,text='Start',command=end_config)
        self.submit.pack(pady=20)


    def display_image(self):
        self.image_window = tk.Toplevel()
        self.image_window.geometry('+{:.0f}+{:.0f}'.format(int(self.x * 0.50), int(self.y * 0.10))) # POSITION image window
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
        self.panel = tk.Label(self.image_window, image=self.img)
        self.panel.pack(side="bottom")


    def display_object_name(self):
        self.object_name = tk.Toplevel()
        self.object_name.geometry('+{:.0f}+{:.0f}'.format(int(self.x * 0.50), 0)) # POSITION object name window

        self.name = tk.Label(self.object_name, 
                                text = str(self.image_ind + 1) + '/' + str(self.num_objects) + ': '+ self.image_list[self.image_ind],
                                wraplength = 500,
                                padx = 5,
                                pady = 5
                                )
        self.name.pack()


    def display_undo_button(self):
        if self.image_ind == 0:
            try:
                self.undo_frame.destroy()
            except:
                pass
        else:
            self.undo_frame = tk.Toplevel()
            self.undo_frame.geometry('+{:.0f}+{:.0f}'.format(int(self.x * 0.01), int(self.y * 0.30))) # POSITION undo window
            self.undo_button = tk.Button(self.undo_frame,text='Undo',width=20,pady=2,height=1,bd=2,command=self.previous_image)
            self.undo_button.pack()


    def setup_data_entry(self):
        self.image_list = sorted([x for x in listdir('.') if splitext(x)[1] == self.ext or splitext(x)[1][1:] == self.ext])
        self.num_objects = len(self.image_list)
        self.update_console(self.console_idx, 'Found {0} total images.'.format(self.num_objects))

        # Print checkpointing message if relevant
        if self.start_from_beginning == False:
            if self.image_ind == self.num_objects: # Existing file already has all images classified
                tkinter.messagebox.showerror('Classify', 'Selected classification file already contains all found images!')
                self.update_console(self.console_idx, 'Selected classification file already contains all found images.')
                self.exit()
                return
            else:
                self.update_console(self.console_idx, 'Starting from image {0}/{1}.'.format(self.image_ind+1, self.num_objects))

        self.display_image()
        self.display_object_name()
        self.display_undo_button()

        def make_selection_fn(new_selection):

            def _f(event=None):

                def make_subcat_callback(subcat):
                    def _f(event=None):
                        if not self.selection:
                            tkinter.messagebox.showerror('Classify', 'Choose a type first!')

                        if self.subcategory is not None:
                            self.subcat_buttons[subcat].unSet()

                        self.subcategory = subcat
                        self.next_image()
                    return _f

                if self.selection is not None:
                    self.buttons[self.selection].unSet()
                self.selection = new_selection

                if self.buttons[self.selection].state != 'down':
                    self.buttons[self.selection].set()

                setup_subcat_frame()

                if self.cv.get() == 0:
                    subcats = self.subcat_dict['all']
                else:
                    subcats = self.subcat_dict[self.selection]

                subcat_keys = list(map(str,range(1,len(subcats)+1)))
                for n,name in enumerate(subcats):
                    # fix command here
                    self.subcat_buttons[name] = mtk.Button(self.subcat_frame,
                        text = subcat_keys[n] + '. ' + name,
                        color = 'light gray',
                        command = make_subcat_callback(name),
                        staydown = True)
                    self.subcat_frame.bind_all(subcat_keys[n], make_subcat_callback(name))
                    self.subcat_buttons[name].pack()

            return _f

        self.selection = None
        self.subcategory = None

        self.categories = tk.Toplevel(root)
        self.categories.geometry('+{:.0f}+{:.0f}'.format(int(self.x * 0.15), 0)) # POSITION category window
        self.cat_frame = tk.Frame(self.categories)
        self.cat_frame.pack(side="left")

        self.buttons = {}
        self.subcat_buttons = {}
        self.subcat_dict = {}

        def setup_subcat_frame():
            if self.subcat_buttons: # Remove subcat frame if it already exists
                self.subcat_frame.destroy()

            self.subcat_frame = tk.Frame(master=self.categories)
            self.subcat_frame.pack()
            self.subcat_label = mtk.Title(self.subcat_frame, text='Subcategories').pack()
            self.subcat_buttons = {}


        if self.cv.get() == 0: # Default categories
            planktonic = ['complete','fragment','damaged']
            nonplankton = ['benthic','mollusk','ostracod','rock','junk image']
            other = ['echinoid spine','radiolarian','spicule','tooth','clipped image','unknown']
            categories = [planktonic, nonplankton, other]
            self.subcat_dict = {'all':['very','somewhat','not']}


        else: # User-provided categories
            # Parse user-provided category file to get main categories and sub-categories
            # Main categories: [ A, B, C ]
            # Sub-categories: [ [a1,a2,a3], [b1,b2], [c1,c2,c3,c4] ]

            with open(self.class_file_path, mode='r', encoding='utf-8') as f:
                csv_reader = csv.reader(f, delimiter=',')
                categories = []

                for row in csv_reader:
                    if 'categories' in row:
                        pass
                    else:
                        categories.append(row[0])
                        if len(row) == 2:
                            subcat_list = row[1].split(';')
                            self.subcat_dict[row[0]] = subcat_list
                            
                # Put the categories in right format for enumeration
                categories = [categories]


        keys = string.ascii_lowercase
        colors = ['green','gray','dark blue']

        # Make main category selection buttons
        button_count = 0
        for m,lst in enumerate(categories):
            for n,name in enumerate(lst):
                self.buttons[name] = mtk.Button(self.cat_frame,
                    text=keys[button_count]+'. '+name,
                    command=make_selection_fn(name),
                    color=colors[m] if self.cv.get() == 0 else colors[n % 3],
                    staydown=True)
                self.buttons[name].pack()
                # attach key to button
                self.cat_frame.bind_all(keys[button_count],make_selection_fn(name))
                button_count += 1


    def next_image(self):
        # Save previous selections
        obj_name = self.image_list[self.image_ind]
        self.data[ obj_name ] = ( self.selection, self.subcategory )

        # Reset buttons
        self.buttons[self.selection].unSet()
        self.subcat_buttons[self.subcategory].unSet()
        self.selection = None
        self.subcategory = None

        # Write selections to file
        if self.image_ind > 0:
            self.append = True
        self.write_data(obj_name)
        self.image_ind += 1

        # Display message and quit if all images complete
        if self.image_ind == len(self.image_list):
            if tkinter.messagebox.askyesno('Classify','All done!' + linesep + ' Exit program?'):
                self.exit()
                return
            else:
                return

        # Close windows for previous object
        self.image_window.destroy()
        self.object_name.destroy()
        self.subcat_frame.destroy()
        try:
            self.undo_frame.destroy()
        except:
            pass

        # Display windows for next object
        self.display_image()
        self.display_object_name()
        self.display_undo_button()


    def exit(self):
        self.update_console(self.console_idx, 'Exiting program.')

        # Save console output to file
        timestamp = datetime.now().strftime('%Y_%m_%d-%H:%M:%S')
        console_file = 'console-' + timestamp + '.txt'
        with open(console_file, 'w') as f:
            for line in self.console.get(0, tk.END):
                f.write(line)
                f.write(linesep)

        # Exit program
        self.root.quit()


    def previous_image(self):
        ### Move image index back by one (unless first image)

        if self.image_ind == 0:
            self.undo_frame.destroy()
            self.update_console(self.console_idx, 'Cannot undo.' + linesep + 'You are at the first image!')
        else:
            self.image_ind -= 1

        # Reset buttons if necessary
        try:
            self.buttons[self.selection].unSet()
        except:
            pass
        self.selection = self.subcategory = None

        # Close windows of current object
        self.image_window.destroy()
        self.object_name.destroy()
        self.subcat_frame.destroy()
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
        self.data[ obj_name ] = ( self.selection, self.subcategory )

        # Rewrite previously saved selections for previous object
        self.rewrite_data()


    def rewrite_data(self):
        ### Rewrite data when undoing

        lines = open(self.filename).readlines()
        f = open(self.filename,'w').writelines(lines[:-1])


    def write_data(self, obj=None):
        ### Write classifications to CSV file

        if self.append: # Write to existing file
            f = open(self.filename,'a')
            writer = csv.writer(f)
            writer.writerow([obj,self.data[obj][0],self.data[obj][1]])

        else: # Initialize and write to new file
            self.filename = self.scan + '_classification.csv'
            f = open(self.filename,'w')
            f.write('object,id,confidence\n')
            writer = csv.writer(f)
            writer.writerow([obj,self.data[obj][0],self.data[obj][1]])

        f.close()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Classify')
    root.update() # Fix for hanging file dialog window and images not appearing

    app = GUI(root)
    root.mainloop()
