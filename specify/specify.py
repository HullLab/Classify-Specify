#!/usr/bin/python
'''
Written by Allison Hsiang

myTkObjects.py written by Greg Meyer

tkentrycomplete.py written by Mitja Martini
'''

from __future__ import division

import Tkinter as tk
import myTkObjects as mtk
import tkMessageBox
import csv
import pandas
import numexpr
import sqlite3
import os
from PIL import ImageTk, Image
from string import lowercase
import tkFileDialog
from tkentrycomplete import *
import glob
import ast


class GUI:

    def __init__(self,root):
        
        def start(event=None):
            
            self.frame.destroy() # Remove mode selection screen

            # Checking mode
            if self.mode.get() == 1:
                
                self.image_dir = tkFileDialog.askdirectory() # Get input directory containing images to check
                self.image_ext = ['.jpg','.tif'] # All acceptable image extensions
                self.all_files = glob.glob(os.path.join(self.image_dir,'*')) # All files in selected directory
                self.image_list = [x for x in self.all_files if os.path.splitext(x)[1] in self.image_ext] # All image files in selected directory
                self.num_objects = len(self.image_list)
                self.objects_list = map(os.path.basename,self.image_list)

                # Check if CSV output file already exists
                self.csv_check = glob.glob(os.path.join(self.image_dir,'specify*csv'))
                if self.csv_check:
                    if tkMessageBox.askyesno('Specify','Specify output file exists; overwrite?'):
                        self.overwrite = True
                    else:
                        self.overwrite = False
                else:
                    self.overwrite = False
                        
                # Check if checkpoint file exists
                if 'checkpoint.txt' in [os.path.basename(x) for x in self.all_files]:
                    self.restart = True
                    self.checkpoint_file = os.path.join(self.image_dir,'checkpoint.txt')
                    
                    print 'Restarting from checkpoint file.'
                    
                    with open(self.checkpoint_file,'rb') as f:
                        lines = f.readlines()
                        self.image_ind = int(lines[0].strip())
                        self.checking_data = ast.literal_eval(lines[1].strip())

                # Clean start setup
                else:
                    self.restart = False
                    self.image_ind = 0
                    self.checking_data = dict.fromkeys(self.objects_list)
                
                self.setup_data_entry()


            # Naming mode (standard)
            else:
                            
                # Set species list
                species_data = pandas.read_csv('app_species_list.csv')
                species_data['specName'] = [x.lower() for x in species_data.specName]
                species_list = species_data['specName']

                # Convert dates
                species_data['End'] = species_data['End'].convert_objects(convert_numeric=True)
                species_data['Start'] = species_data['Start'].convert_objects(convert_numeric=True)
                
                # Get directory of images from user
                data_file = tkFileDialog.askopenfilename()
                os.chdir(os.path.dirname(data_file))

                self.data = os.path.basename(data_file)
                
                # Checkpoint restart
                if 'checkpoint' in data_file:
                    self.restart = True
                    
                    self.checkpoint_data_tr = pandas.read_csv(data_file)
                    self.checkpoint_codes = map(list,self.checkpoint_data_tr.tail(1).values)[0]
                    
                    self.output_base = '_'.join(self.data.split('_')[:-1])

                    self.data_todb = data_file
                    
                    self.image_ind = int(self.checkpoint_codes[0])
                    
                    self.initialize_objects()
                    
                    print 'Restarting from checkpoint file.'
                    
                # Normal start
                else:
                    self.restart = False
                    self.output_base = self.data[:-4]

                    self.image_ind = 0
                    
                    self.convert_csv()

        self.root = root

        # Set mode
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.mode_select = mtk.Title(self.frame,text='Select mode:')
        self.mode_select.pack()

        self.mode = tk.IntVar()

        tk.Radiobutton(self.frame,text='Checking mode',variable=self.mode,value=1).pack()
        tk.Radiobutton(self.frame,text='Naming mode',variable=self.mode,value=2).pack()
        
        mtk.Button(self.frame,text='Start',command=start).pack()


    def convert_csv(self):

        def write_converted_csv(event=None):
            if self.v.get() == 1:
                self.temp_csv = pandas.read_csv(data_file)
                self.temp_csv_subset = self.temp_csv.ix[:,1:4]
                
                for i in range(len(self.temp_csv_subset.ix[:,0])):
                    self.old_entry = self.temp_csv_subset.ix[i,0]
                    self.new_entry = 'obj' + '0' * (5 - len(str(self.old_entry))) + str(self.old_entry)
                    self.temp_csv_subset.ix[i,0] = self.new_entry
                    
                self.temp_csv_subset.columns = ['object','id','confidence']
                self.new_filename = self.output_base + '_converted.csv'
                self.temp_csv_subset.to_csv(self.new_filename, mode='w', index=False)
                self.data_todb = self.new_filename
                
            elif self.v.get() == 2:
                self.temp_csv = pandas.read_csv(data_file)
                self.temp_csv.columns = ['object','id','confidence']
                self.new_filename = self.output_base + '_converted.csv'
                self.temp_csv.to_csv(self.new_filename, mode='w', index=False)
                self.data_todb = self.new_filename

            else:
                self.data_todb = data_file

            self.frame.destroy()
            self.initialize_objects()
            
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.convert_csv_text = mtk.Title(self.frame,text='Convert CSV format?')
        self.convert_csv_text.pack()
        
        self.v = tk.IntVar()
        tk.Radiobutton(self.frame,text='Convert old Classify to new Classify format',variable=self.v,value=1).pack()
        tk.Radiobutton(self.frame,text='Convert Classify column names',variable=self.v,value=2).pack()
        tk.Radiobutton(self.frame,text='No conversion',variable=self.v,value=0).pack()

        self.submit_csv = mtk.Button(self.frame,text='Done',command=write_converted_csv)
        self.submit_csv.pack()


    def initialize_objects(self):
        
        def set_init_objects(event=None):
            self.complete_f = self.complete.get()
            self.fragment_f = self.fragment.get()
            self.damaged_f = self.damaged.get()
            self.all_objects_f = self.all_objects.get()

            if not any([self.complete_f, self.fragment_f, self.damaged_f, self.all_objects_f]):
                tkMessageBox.showerror('Specify','Pick objects to load.')
                
            else:
                print 'Objects loaded: ' + self.complete_f * 'Complete' + self.complete_f * ', ' + self.fragment_f * 'Fragment' + self.fragment_f * ', ' + self.damaged_f * 'Damaged' + self.all_objects_f * ', ' + self.all_objects_f * 'All Objects'
                self.frame.destroy()
                del self.submit
                self.read_data()

        if self.restart:
            self.complete_f = int(self.checkpoint_codes[1])
            self.fragment_f = int(self.checkpoint_codes[2])
            self.damaged_f = int(self.checkpoint_codes[3])
            self.all_objects_f = int(self.checkpoint_codes[4])
            
            print 'Objects loaded: ' + self.complete_f * 'Complete' + self.complete_f * ', ' + self.fragment_f * 'Fragment' + self.fragment_f * ', ' + self.damaged_f * 'Damaged' + self.all_objects_f * ', ' + self.all_objects_f * 'All Objects'

            self.read_data()

        else:
            self.frame = tk.Frame(self.root)
            self.frame.pack()
            self.init_obj_text = mtk.Title(self.frame,text='Load which objects?')
            self.init_obj_text.pack()
            
            self.complete = tk.IntVar()
            self.fragment = tk.IntVar()
            self.damaged = tk.IntVar()
            self.all_objects = tk.IntVar()
            
            self.complete_check = tk.Checkbutton(self.frame,text="Complete",variable=self.complete,onvalue=1,offvalue=0)
            self.complete_check.pack()
            
            self.fragment_check = tk.Checkbutton(self.frame,text="Fragment",variable=self.fragment,onvalue=1,offvalue=0)
            self.fragment_check.pack()

            self.damaged_check = tk.Checkbutton(self.frame,text="Damaged",variable=self.damaged,onvalue=1,offvalue=0)
            self.damaged_check.pack()
            
            self.all_check = tk.Checkbutton(self.frame,text="All",variable=self.all_objects,onvalue=1,offvalue=0)
            self.all_check.pack()
        
            self.submit = mtk.Button(self.frame,text='Done',command=set_init_objects)
            self.submit.pack()


    def read_data(self):

        def get_selected_objects():

            if self.all_objects_f or sum(self.options) == 3:
                self.cur.execute('SELECT object FROM foram WHERE (id = ? OR id = ? OR id = ?)', ('complete','fragment','damaged'))
            elif sum(self.options) == 1:
                id_get = self.complete_f * 'complete' + self.fragment_f * 'fragment' + self.damaged_f * 'damaged'
                self.cur.execute('SELECT object FROM foram WHERE id = ?', [id_get])
            else:
                id_get = self.complete_f * 'complete' + self.fragment_f * ', ' + self.fragment_f * 'fragment' + self.damaged_f * ', ' + self.damaged_f * 'damaged'
                self.cur.execute('SELECT object FROM foram WHERE (id = ? OR id = ?)', [id_get.split(',')[0],id_get.split(',')[1]])
        
        self.con = sqlite3.connect(':memory:')
        self.cur = self.con.cursor()
        self.cur.execute('CREATE TABLE foram (object,id,confidence,species,genus,note,species_confidence);')
        with open(self.data_todb,'rb') as d:
            self.data_read = csv.DictReader(d)
            self.options = [self.complete_f,self.fragment_f,self.damaged_f]
            if self.restart:
                self.to_db = [(i['object'],i['id'],i['confidence'],i['species'],i['genus'],i['note'],i['species_confidence']) for i in self.data_read]
                self.cur.executemany('INSERT INTO foram (object,id,confidence,species,genus,note,species_confidence) VALUES (?,?,?,?,?,?,?);', self.to_db)
                self.cur.execute('DELETE FROM foram WHERE note = ?',['checkpoint'])
            else:
                self.to_db = [(i['object'],i['id'],i['confidence']) for i in self.data_read]
                self.cur.executemany('INSERT INTO foram (object,id,confidence) VALUES (?,?,?);', self.to_db)
                
        self.con.commit()
        
        get_selected_objects()

        self.all_rows = self.cur.fetchall()

        self.num_objects = len(self.all_rows)
        
        self.set_ages()
        

    def set_ages(self): 

        def set_species_options_by_age(event=None):

            try:
                self.start_number = float(self.start_date_entry.get())
            except ValueError:
                self.start_number = ''
            try:
                self.end_number = float(self.end_date_entry.get())
            except ValueError:
                self.end_number = ''

            if (self.start_number == '') and (self.end_number == '') and (self.no_fossils.get() == 0):
                print 'No age range set; using full species list for autocomplete.'
                self.final_data = species_data

            else:
                if self.no_fossils.get() == 1:
                    self.final_data = species_data[['specName','End','Start']].query('End >= 0')
                else:
                    self.query = 'End >= ' + str(self.end_date_entry.get()) + ' and Start <= ' + str(self.start_date_entry.get())
                    self.final_data = species_data[['specName','End','Start']].query(self.query)

            self.frame.destroy()
            self.setup_data_entry()
            
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="left")
               
        self.date_label = mtk.Title(self.frame,text='Age Range (Inclusive):')
        self.date_label.pack()
        
        self.end_default = tk.StringVar()
        self.end_date_entry = tk.Entry(self.frame, textvariable = self.end_default, width = 5)
        self.end_default.set('End')
        self.end_date_entry.pack()
        
        self.start_default = tk.StringVar()
        self.start_date_entry = tk.Entry(self.frame, textvariable = self.start_default, width = 5)
        self.start_default.set('Start')
        self.start_date_entry.pack()
        
        self.no_fossils = tk.IntVar()
        self.no_fossils_check = tk.Checkbutton(self.frame,text="No fossils",variable=self.no_fossils,onvalue=1,offvalue=0)
        self.no_fossils_check.pack()
        
        self.set_ages = mtk.Button(self.frame,text='Set Ages',command=set_species_options_by_age)
        self.set_ages.pack()
       

    def display_image(self):
        
        self.image_window = tk.Toplevel()
        self.image_window.geometry('+370+100')
        self.image_window.lower(root)

        self.img = Image.open(self.image_list[self.image_ind])

        # Resize image if too large
        if self.img.size[0] > 1000:
            new_width = 700
            ratio = new_width / float(self.img.size[0])
            new_height = int((float(self.img.size[1] * float(ratio))))
            self.resized = self.img.resize((new_width,new_height),Image.ANTIALIAS)
            self.img = ImageTk.PhotoImage(self.resized)
        else:
            self.img = ImageTk.PhotoImage(self.img)

        self.panel = tk.Label(self.image_window,image=self.img)
        self.panel.pack()


    def display_object_name(self):
        
        self.object_name = tk.Toplevel()
        self.object_name.geometry('+50+250')
        self.object_name.lower(root)

        self.name = mtk.Message(self.object_name,text=str(self.image_ind + 1) + '/' + str(self.num_objects) + ': '+ os.path.basename(self.image_list[self.image_ind]))
        self.name.pack()


    def confirm_species(self,event=None):
        
        print 'Species set as: ' + self.species_entry._hits[self.species_entry._hit_index]
        
        self.entry_name_split = self.species_entry._hits[self.species_entry._hit_index].split('_')
        self.species_only = self.entry_name_split[0]
        
        if len(self.entry_name_split) == 1:
            self.genus_only = ''
            self.note = ''
        elif len(self.entry_name_split) == 2:
            self.genus_only = self.entry_name_split[1]
            self.note = ''
        elif len(self.entry_name_split) == 3:
            self.genus_only = self.entry_name_split[1]
            self.note = self.entry_name_split[2]

        self.conf_window = tk.Toplevel()
        self.conf_window_label = mtk.Title(self.conf_window,text='Confidence Level:')
        self.conf_window_label.pack()
        self.conf_window.wm_attributes("-topmost", 1)
        self.conf_window.focus_force()

        def set_confidence_level(confidence_level):
            
            def _f(event=None):
                
                if self.species_confidence is not None:
                    self.buttons[confidence_level].unSet()
                    
                self.species_confidence = confidence_level
                self.update_database()
                
            return _f

        self.species_confidence = None
        self.buttons = {}
        confidence = ['very','somewhat','not']
        conf_keys = ['1','2','3']
        for i,c in enumerate(confidence):
            self.buttons[c] = mtk.Button(self.conf_window,text=conf_keys[i] + '. ' + c,color='light gray',command=set_confidence_level(c),staydown=True)
            self.conf_window.bind(conf_keys[i],set_confidence_level(c))
            self.buttons[c].pack()


    def update_database(self):
                
        self.cur.execute('UPDATE foram SET species = ?, genus = ?, note = ?, species_confidence = ? WHERE object = ?', (self.species_only,self.genus_only,self.note,self.species_confidence,self.objects_list[self.image_ind]))
        self.con.commit()

        self.cur.execute('SELECT * FROM foram')
        self.test = self.cur.fetchall()
        
        self.conf_window.destroy()

        self.next_image()
        self.species_entry.delete(0,tk.END)
      
        
    def display_windows(self):
        self.display_image()
        self.display_object_name()
        
        root.wm_attributes("-topmost", 1)
        root.focus_force()          


    def setup_data_entry(self):
        
        def make_selection(new_selection):

            def _f(event=None):
                if self.selection is not None:
                    self.buttons[self.selection].unSet()

                self.checking_data[self.objects_list[self.image_ind]] = new_selection
                print '{:s}: {:s}\n'.format(self.objects_list[self.image_ind],new_selection)
                self.next_image()

            return _f

            
        if self.mode.get() == 1:

            self.display_windows()

            self.frame = tk.Frame(self.root)
            self.frame.pack(side="left")

            self.selection = None

            self.buttons = {}

            options = [('correct','1. Correct as marked'),('change','2. Needs change'),('remove','3. Remove from dataset')]

            for i,option in enumerate(options):
                self.buttons[option[0]] = mtk.Button(self.frame,
                                                text=option[1],
                                                command=make_selection(option[0]))
                self.buttons[option[0]].pack()
                self.frame.bind_all(str(i+1),make_selection(option[0]))

            # Checkpoint button
            self.checkpoint_button = mtk.Button(self.frame,text='Checkpoint',color='dark blue',command=self.check_checkpoint)
            self.checkpoint_button.pack()

            # Undo button
            self.undo_button = tk.Button(self.frame,text='Undo',width=20,pady=2,height=1,bd=2,command=self.previous_image)
            self.undo_button.pack()

        else:
            self.objects_list = [x[0] for x in self.all_rows]
            self.image_list = [x for y in self.objects_list for x in os.listdir('.') if y in x]
            
            self.display_windows()
        
            self.species_entry_label = mtk.Title(root,text='Species ID:')
            self.species_entry_label.pack()

            self.species_entry = AutocompleteEntry(root)
            self.species_entry.set_completion_list(self.final_data['specName'])
            self.species_entry.pack()
            self.species_entry.focus()

            self.submit_species = mtk.Button(root,text='Confirm Species',command=self.confirm_species)
            root.bind('<Return>',self.confirm_species)
            self.submit_species.pack()

            # Checkpoint button
            self.checkpoint_button = mtk.Button(root,text='Checkpoint',color='dark blue',command=self.checkpoint)
            self.checkpoint_button.pack()

            # Undo button
            self.undo_button = tk.Button(self.frame,text='Undo',width=20,pady=2,height=1,bd=2,command=self.previous_image)
            self.undo_button.pack()


    def previous_image(self):
        # Move image index back by one (unless first image)
        if self.image_ind == 0:
            print 'You are at the first image; cannot undo!'
        else:
            self.image_ind -= 1

        # Close windows of current object
        self.image_window.destroy()
        self.object_name.destroy()

        # Display windows of previous object
        self.display_image()
        self.display_object_name()


    def check_checkpoint(self,event=None):
        filename = 'checkpoint.txt'
        with open(os.path.join(self.image_dir,filename),'wb') as f:
            f.write('{:s}\n'.format(str(self.image_ind)))
            f.write(str(self.checking_data))

        print 'Checkpoint file created.'
        

    def checkpoint(self,event=None):
        
        self.checkpoint_filename = self.output_base + '_checkpoint.csv'
        
        f = open(self.checkpoint_filename,'w')

        self.cur.execute('SELECT * FROM foram')
        self.all_rows = self.cur.fetchall()
        
        writer = csv.writer(f)
        writer.writerow(['object','id','confidence','species','genus','note','species_confidence'])
        writer.writerows(self.all_rows)
        writer.writerow([self.image_ind,self.complete_f,self.fragment_f,self.damaged_f,self.all_objects_f,'checkpoint'])
        f.close()

        print 'Checkpoint file created.'


    def next_image(self):

        self.image_ind += 1

        if self.image_ind == len(self.image_list):
            tkMessageBox.showinfo('Specify','All done!')
            self.image_window.destroy()
            self.object_name.destroy()
            self.write_data()

        else:
            self.image_window.destroy()
            self.object_name.destroy()

            self.display_image()
            self.display_object_name()

            self.root.wm_attributes("-topmost", 1)
            self.root.focus_force()

            if self.mode.get() == 2:
                self.species_entry.after(1,lambda:self.species_entry.focus_force())


    def write_data(self):
        
        if self.mode.get() == 1:
            # Determine whether to rewrite output file (if it already exists)
            if self.overwrite:
                filename = 'specify_check_test.csv'
            else:
                
                filename = 'specify_check_test_{:d}.csv'.format(len(self.csv_check)+1)
            
            with open(os.path.join(self.image_dir,filename),'wb') as f:
                f.write('obj,action\n')
                for obj in self.checking_data.keys():
                    f.write('{:s},{:s}\n'.format(obj,self.checking_data[obj]))

            print 'Specify (checking mode) file written.'
            
        else:
            filename = self.output_base + '_specify.csv'
                    
            if not os.path.exists(filename):
                f = open(filename,'w')
            else:
                if tkMessageBox.askyesno('Specify',filename + ' exists; overwrite?'):
                    f = open(filename,'w')
                else:
                    f = open(self.output_base + '_specify_2.csv','w')

            self.cur.execute('SELECT * FROM foram')
            self.all_rows = self.cur.fetchall()

            writer = csv.writer(f)
            writer.writerow(['object','id','confidence','species','genus','note','species_confidence'])
            writer.writerows(self.all_rows)

            print 'Specify (naming mode) file written.'

            f.close()

        self.cleanup()


    def cleanup(self):
        try:
            os.remove(self.checkpoint_file)
        except:
            pass
        
        root.destroy()



if __name__ == '__main__':
    
    root = tk.Tk()
    root.title('Specify')

    app = GUI(root)
    root.mainloop()
