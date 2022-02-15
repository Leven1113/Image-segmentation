import os
import time
import tkinter as tk
from tkinter import simpledialog
from tkinter.colorchooser import *
from os import getcwd, path
from PIL import ImageTk, Image

from aux_functions import *
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# import matplotlib.gridspec as gridspec
from skimage.filters import gaussian
from skimage.filters.rank import entropy
from skimage.morphology import disk
import copy
import subprocess


class Gui:
    def __init__(self, master):
        self.master = master
        self.gui_width = 1500
        self.gui_height = 780
        self.space_for_text = 100
        self.pad_size = 7
        self.scale = 1.0
        self.factor = 1.0
        self.image_size_limit = 5e6
        master.title('PyPAIS')
        icon = ImageTk.PhotoImage(file='_aux/icon.png')
        master.tk.call('wm', 'iconphoto', root._w, icon)
        screen_width, screen_height = master.winfo_screenwidth(), master.winfo_screenheight()
        x_position, y_position = self.gui_width/2-screen_width/2, self.gui_height/2-screen_height/2
        master.geometry('%dx%d+%d+%d' % (self.gui_width, self.gui_height, x_position, y_position))

        # initialized default GUI values
        self.phases, self.original_image, self.gray_image_asarray, self.gray_image_asrgb, self.masked_img, \
        self.smooth_image, self.smooth_image_asarray, self.percentage, self.entropy, self.smooth_entropy, \
        self.smooth_entropy_image, self.masked_entropy, self.mask, self.roi_mask = [], [], [], [], [], [], [], [], [], \
            [], [], [], [], []
        self.cur_phase, self.selected_color, self.selected_entropy, self.mask_size = 0, 0, 0, 0
        self.just_initiated = True
        self.low_val, self.high_val, self.low_val_entropy, self.high_val_entropy, self.phases_color, \
        self.phases_color_normed, self.phases_color_tk = [], [], [], [], [], [], []
        self.project_name = ' '
        self.x1 = np.linspace(0, 255, num=256)

        # load initial image
        self.gray_image = Image.open('_aux/dummy.png')
        self.my_image_name = '   File name : --- none ---'
        self.thumb_factor, self.thumb_size = self.rescale_image()
        self.thumb_image = ImageTk.PhotoImage(self.gray_image.resize(self.thumb_size, Image.ANTIALIAS))

        # first pull-down menu
        self.menu_bar = tk.Menu(master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Load image", command=self.upload_image)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=master.destroy)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        # second pull-down menu
        self.scale_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.scale_menu.add_command(label="Scale the image", command=self.scale_image)
        self.scale_menu.add_command(label="Draw ROI", command=self.add_roi)
        self.scale_menu.add_command(label="Load ROI", command=self.load_roi)
        self.menu_bar.add_cascade(label="ROI and Scaling", menu=self.scale_menu)
        # third pull-down menu
        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="Export all data", command=self.export_all)
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)
        # show the menu
        master.config(menu=self.menu_bar)  # show the menu!!

        # Canvas frame
        canvas_frame = tk.Frame(master)
        # canvas
        self.canvas_1 = tk.Canvas(canvas_frame, width=int(self.gui_width/2),
                                  height=int(self.gui_height-1.25*self.space_for_text))
        self.canvas_1.grid(column=0, row=0, columnspan=4)
        self.canvas_1.create_image(0, 0, image=self.thumb_image, anchor=tk.NW)
        # radiobutton image/entropy + show mask
        radio_frame = tk.Frame(canvas_frame)
        self.radio_choice = tk.IntVar()
        self.radio_choice.set(0)  # initializing the choice
        self.radio_image = tk.Radiobutton(radio_frame, text='Image in grayscale', variable=self.radio_choice,
                                          value=0, command=self.image_changed, anchor=tk.NE)
        self.radio_image.pack(side=tk.LEFT)
        self.radio_entropy = tk.Radiobutton(radio_frame, text='Texture roughness (entropy)',
                                            variable=self.radio_choice, value=1, command=self.image_changed,
                                            anchor=tk.NE)
        self.radio_entropy.pack(side=tk.LEFT)
        self.display_mode = tk.IntVar()
        self.display_mode.set(1)  # initializing the choice
        self.checkbox_mode = tk.Checkbutton(radio_frame, text='Show masked image', variable=self.display_mode,
                                            command=self.image_changed)
        self.checkbox_mode.pack(side=tk.LEFT)
        radio_frame.grid(column=0, row=1, sticky='W', pady=2)
        # label with filename
        self.label_filename = tk.Label(canvas_frame, text=self.my_image_name, anchor=tk.NE)
        self.label_filename.grid(column=0, row=2, sticky='W', pady=2)
        # smoothing
        self.label_smoothing = tk.Label(canvas_frame, text='Smoothing: ', anchor=tk.NE)
        self.label_smoothing.grid(column=1, row=2, sticky='E', pady=2)
        self.slider_smooth = tk.Scale(canvas_frame, from_=0.0, to=10.0, tickinterval=2.0, resolution=0.1,
                                      length=self.gui_width/10, orient=tk.HORIZONTAL, font=("Helvetica", 8),
                                      command=self.image_smoothing)
        self.slider_smooth.grid(column=2, row=2, sticky='E', pady=2)
        self.entry_smooth_var = tk.StringVar()
        self.entry_smooth_var.set('%.2f' % 0.0)
        self.entry_smooth = tk.Entry(canvas_frame, width=5, font=("Helvetica", 8), textvariable=self.entry_smooth_var)
        self.entry_smooth.bind('<Return>', (lambda _: self.callback_entry_smooth_var()))
        self.entry_smooth.grid(column=3, row=2, sticky='W', pady=2)
        # place the frame
        canvas_frame.grid(column=0, row=0, rowspan=2, padx=self.pad_size, pady=self.pad_size, sticky='NW')

        # separator
        separator = tk.Frame(width=2, bd=3, bg='white', height=self.gui_height-3*self.pad_size, relief=tk.SUNKEN)
        separator.grid(column=1, row=0, rowspan=2, pady=self.pad_size, padx=self.pad_size, sticky='N')

        # Phases list frame
        phases_frame = tk.Frame(master, width=int(self.gui_width/9), height=int(3*self.gui_height/5))
        phases_frame.grid_propagate(0)
        # label phases
        self.label_phases = tk.Label(phases_frame, text='Phases', anchor=tk.NW)
        self.label_phases.grid(column=0, row=0, columnspan=2, sticky='W', pady=2)
        # listbox with phases
        listbox_frame_1 = tk.Frame(phases_frame)
        self.scrollbar_phases = tk.Scrollbar(listbox_frame_1)
        self.phases_listbox = tk.Listbox(listbox_frame_1, yscrollcommand=self.scrollbar_phases.set)
        self.scrollbar_phases.config(command=self.phases_listbox.yview)
        self.scrollbar_phases.pack(side=tk.RIGHT, fill=tk.Y)
        self.phases_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.phases_listbox.bind('<<ListboxSelect>>', self.change_phase)
        listbox_frame_1.grid(column=0, row=1, columnspan=2)
        # add button
        self.add_button = tk.Button(phases_frame, text='Add', command=self.add_phase)
        self.add_button.grid(column=0, row=2, sticky='W', padx=2)
        # delete button
        self.delete_button = tk.Button(phases_frame, text='Delete', command=self.delete_phase)
        self.delete_button.grid(column=1, row=2, sticky='W', padx=2)
        # color picker
        self.color_button = tk.Button(phases_frame, text='Phase color', command=self.get_color)
        self.color_button.grid(column=0, row=3, columnspan=2, pady=5, sticky='W')
        # percentage label
        self.label_area = tk.Label(phases_frame, text=' ', anchor=tk.NW)
        self.label_area.grid(column=0, row=4, columnspan=2, pady=5, sticky='W')
        # place the frame
        phases_frame.grid(column=2, row=0, padx=self.pad_size, pady=self.pad_size, sticky='NW')

        # Gray-level distribution
        distribution_frame = tk.Frame(master, width=int(7*self.gui_width/18), height=int(3*self.gui_height/5))
        distribution_frame.pack_propagate(0)
        # label distribution
        self.label_distribution = tk.Label(distribution_frame, text='Gray-level distribution', anchor=tk.NW)
        self.label_distribution.grid(column=0, row=0, columnspan=2, sticky='W', pady=2)
        # canvas for plotting
        self.canvas_2 = tk.Canvas(distribution_frame, bg='white', width=int(self.gui_width/4-1.5*self.space_for_text),
                                  height=int(3*self.gui_height/4-4*self.space_for_text))
        self.canvas_2.grid(column=0, row=1, columnspan=2)
        # label Laplace
        self.label_distribution_entropy = tk.Label(distribution_frame, text='Entropy distribution', anchor=tk.NW)
        self.label_distribution_entropy.grid(column=2, row=0, columnspan=2, padx=8, pady=2, sticky='W')
        # canvas for plotting
        self.canvas_3 = tk.Canvas(distribution_frame, bg='white', width=int(self.gui_width/4-1.5*self.space_for_text),
                                  height=int(3*self.gui_height/4-4*self.space_for_text))
        self.canvas_3.grid(column=2, row=1, columnspan=2, padx=8, sticky='W')
        # settings and statistics widgets
        # 0) Entropy setting
        self.label_entropy = tk.Label(distribution_frame, text='Entropy calculation radius:', anchor=tk.NW)
        self.label_entropy.grid(column=0, row=2, columnspan=1, sticky='E', pady=2)
        self.slider_entropy = tk.Scale(distribution_frame, from_=0, to=10, tickinterval=2, length=self.gui_width/6,
                                       orient=tk.HORIZONTAL, font=("Helvetica", 8), command=self.slide_entropy)
        self.slider_entropy.grid(column=1, row=2, columnspan=2, sticky='W', pady=2)
        self.entry_entropy_var = tk.StringVar()
        self.entry_entropy_var.set('%d' % 5)
        self.slider_entropy.set(int(self.entry_entropy_var.get()))
        self.entry_entropy = tk.Entry(distribution_frame, width=5, font=("Helvetica", 8),
                                      textvariable=self.entry_entropy_var)
        self.entry_entropy.bind('<Return>', (lambda _: self.callback_entry_entropy_var()))
        self.entry_entropy.grid(column=3, row=2, sticky='W', pady=2)
        # 1) gray-scale
        self.label_low = tk.Label(distribution_frame, text='Gray-level minimum (blacks):', anchor=tk.NW)
        self.label_low.grid(column=0, row=3, columnspan=1, sticky='E', pady=2)
        self.label_high = tk.Label(distribution_frame, text='Gray-level maximum (whites):', anchor=tk.NW)
        self.label_high.grid(column=0, row=4, columnspan=1, sticky='E', pady=2)
        # self.label_mean = tk.Label(distribution_frame, text=' ', anchor=tk.NW)
        # self.label_mean.grid(column=0, row=5, columnspan=1, sticky='W', pady=2)
        self.slider_low = tk.Scale(distribution_frame, from_=0, to=255, tickinterval=50, length=self.gui_width/6,
                                   orient=tk.HORIZONTAL, font=("Helvetica", 8), command=self.slide_low)
        self.slider_low.grid(column=1, row=3, columnspan=2, sticky='W', pady=2)
        self.entry_low_var = tk.StringVar()
        self.entry_low_var.set('%d' % 0)
        self.entry_low = tk.Entry(distribution_frame, width=5, font=("Helvetica", 8), textvariable=self.entry_low_var)
        self.entry_low.bind('<Return>', (lambda _: self.callback_entry_low_var()))
        self.entry_low.grid(column=3, row=3, sticky='W', pady=2)
        self.slider_high = tk.Scale(distribution_frame, from_=0, to=255, tickinterval=50, length=self.gui_width/6,
                                    orient=tk.HORIZONTAL, font=("Helvetica", 8), command=self.slide_high)
        self.slider_high.grid(column=1, row=4, columnspan=2, sticky='W', pady=2)
        self.entry_high_var = tk.StringVar()
        self.entry_high_var.set('%d' % 0)
        self.entry_high = tk.Entry(distribution_frame, width=5, font=("Helvetica", 8), textvariable=self.entry_high_var)
        self.entry_high.bind('<Return>', (lambda _: self.callback_entry_high_var()))
        self.entry_high.grid(column=3, row=4, sticky='W', pady=2)
        # 2) entropy
        self.label_low_entropy = tk.Label(distribution_frame, text='Entropy minimum (smooth textures):', anchor=tk.NW)
        self.label_low_entropy.grid(column=0, row=6, columnspan=1, sticky='E', pady=2)
        self.label_high_entropy = tk.Label(distribution_frame, text='Entropy maximum (rough textures):', anchor=tk.NW)
        self.label_high_entropy.grid(column=0, row=7, columnspan=1, sticky='E', pady=2)
        # self.label_mean_entropy = tk.Label(distribution_frame, text=' ', anchor=tk.NW)
        # self.label_mean_entropy.grid(column=0, row=8, columnspan=1, sticky='W', pady=2)
        self.slider_low_entropy = tk.Scale(distribution_frame, from_=0, to=255, tickinterval=50, length=self.gui_width/6,
                                           orient=tk.HORIZONTAL, font=("Helvetica", 8), command=self.slide_low_entropy)
        self.slider_low_entropy.grid(column=1, row=6, columnspan=2, sticky='W', pady=2)
        self.entry_low_entropy_var = tk.StringVar()
        self.entry_low_entropy_var.set('%d' % 0)
        self.entry_low_entropy = tk.Entry(distribution_frame, width=5, font=("Helvetica", 8),
                                          textvariable=self.entry_low_entropy_var)
        self.entry_low_entropy.bind('<Return>', (lambda _: self.callback_entry_low_entropy_var()))
        self.entry_low_entropy.grid(column=3, row=6, sticky='W', pady=2)
        self.slider_high_entropy = tk.Scale(distribution_frame, from_=0, to=255, tickinterval=50, length=self.gui_width/6,
                                            orient=tk.HORIZONTAL, font=("Helvetica", 8), command=self.slide_high_entropy)
        self.slider_high_entropy.grid(column=1, row=7, columnspan=2, sticky='W', pady=2)
        self.entry_high_entropy_var = tk.StringVar()
        self.entry_high_entropy_var.set('%d' % 0)
        self.entry_high_entropy = tk.Entry(distribution_frame, width=5, font=("Helvetica", 8),
                                           textvariable=self.entry_high_entropy_var)
        self.entry_high_entropy.bind('<Return>', (lambda _: self.callback_entry_high_entropy_var()))
        self.entry_high_entropy.grid(column=3, row=7, sticky='W', pady=2)
        # place the frame
        distribution_frame.grid(column=3, row=0, padx=self.pad_size, pady=self.pad_size, sticky='NW')

        # Output frame
        output_frame = tk.Frame(master)
        # label distribution
        self.label_status = tk.Label(output_frame, text='Messages', anchor=tk.NW)
        self.label_status.grid(column=0, row=0, sticky='W', pady=2)
        # textbox
        textbox_frame_1 = tk.Frame(output_frame)
        self.scrollbar_output = tk.Scrollbar(textbox_frame_1)
        self.text_status = tk.Text(textbox_frame_1, height=9, font=("Helvetica", 9),
                                   yscrollcommand=self.scrollbar_output.set)
        self.scrollbar_output.config(command=self.text_status.yview)
        self.scrollbar_output.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_status.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        textbox_frame_1.grid(column=0, row=1, columnspan=2)
        # place the frame
        output_frame.grid(column=2, row=1, columnspan=2, padx=self.pad_size, sticky='NW')

        # Finish initialization
        self.switch_state_widgets(False)
        self.write_output('>> Program launched successfully, please upload an image for the phase analysis.\n')

    def rescale_image(self):
        my_image_width, my_image_height = self.gray_image.size
        factor = (self.gui_width/2)/my_image_width
        width = int(my_image_width*factor)
        height = int(my_image_height*factor)
        max_height = self.gui_height-self.space_for_text
        if height > max_height:
            factor = max_height/my_image_height
            width = int(my_image_width*factor)
            height = int(my_image_height*factor)
        return factor, (width, height)

    def switch_state_widgets(self, enable_widgets):
        if enable_widgets:
            self.phases_listbox.config(state='normal')
            self.add_button.config(state='normal')
            self.canvas_2.config(state='normal')
            self.label_low.config(state='normal')
            self.label_high.config(state='normal')
            # self.label_mean.config(state='normal')
            self.label_area.config(state='normal')
            self.label_distribution.config(state='normal')
            self.canvas_3.config(state='normal')
            self.label_low_entropy.config(state='normal')
            self.label_high_entropy.config(state='normal')
            # self.label_mean_entropy.config(state='normal')
            self.label_distribution_entropy.config(state='normal')
            self.label_phases.config(state='normal')
            self.label_smoothing.config(state='normal')
            self.radio_image.config(state='normal')
            self.radio_entropy.config(state='normal')
            self.checkbox_mode.config(state='normal')
        else:
            self.phases_listbox.config(state='disable')
            self.add_button.config(state='disable')
            self.color_button.config(state='disable')
            self.delete_button.config(state='disable')
            self.canvas_2.config(state='disable')
            self.label_low.config(state='disable')
            self.label_high.config(state='disable')
            # self.label_mean.config(state='disable')
            self.label_area.config(state='disable')
            self.label_distribution.config(state='disable')
            self.canvas_3.config(state='disable')
            self.label_low_entropy.config(state='disable')
            self.label_high_entropy.config(state='disable')
            # self.label_mean_entropy.config(state='disable')
            self.label_distribution_entropy.config(state='disable')
            self.label_phases.config(state='disable')
            self.label_smoothing.config(state='disable')
            self.radio_image.config(state='disable')
            self.radio_entropy.config(state='disable')
            self.checkbox_mode.config(state='disable')

    def write_output(self, string_to_display):
        self.text_status.insert(tk.INSERT, string_to_display)
        self.text_status.mark_set('insert', tk.END)
        self.text_status.see('insert')

    def upload_image(self):
        img_file = select_image_file_prompt('Choose an image file', getcwd())
        self.project_name = simpledialog.askstring('Project name', 'Fill in the project name')
        self.master.title('PyPAIS [%s]' % self.project_name)
        self.write_output('>> Project name: %s.\n' % self.project_name)
        for self.cur_phase in range(len(self.phases)):
            self.delete_phase()
        try:
            self.original_image = mpimg.imread(img_file)
            self.write_output('>> Image %s loaded for the phase analysis.\n' % (path.basename(img_file)))
            img_size = self.original_image.shape[0]*self.original_image.shape[1]
            max_size = self.image_size_limit
            if img_size > max_size:
                self.factor = np.sqrt(max_size/img_size)
                img_image = Image.fromarray(self.original_image)
                img_image = img_image.resize((int(self.original_image.shape[1]*self.factor),
                                              int(self.original_image.shape[0]*self.factor)), Image.ANTIALIAS)
                self.original_image = np.array(img_image)
                self.write_output('>> Image scaled by a factor of %.3f.\n' % self.factor)
            self.gray_image_asarray = np.asarray(rgb2gray(self.original_image))
            self.roi_mask = np.ones_like(self.gray_image_asarray)
            self.roi_mask = self.roi_mask.astype(bool)
            self.gray_image_asrgb = np.dstack((self.gray_image_asarray, self.gray_image_asarray, self.gray_image_asarray))
            self.calculate_entropy()
            self.entropy_asrgb = np.dstack((self.entropy, self.entropy, self.entropy))
            self.mask_size = np.sum(self.roi_mask)
            rgb_image = Image.fromarray(self.original_image)
            self.gray_image = rgb_image.convert('L')  # convert image to monochrome
            self.entropy_image = Image.fromarray(self.entropy)
            self.slider_smooth.set(0.0)
            self.initiate_smoothed_images()
            self.my_image_name = '   File name : %s' % (path.basename(img_file))
            self.label_filename.config(text=self.my_image_name)
            self.thumb_factor, self.thumb_size = self.rescale_image()
            self.thumb_image = ImageTk.PhotoImage(self.gray_image.resize(self.thumb_size, Image.ANTIALIAS))
            self.canvas_1.delete('all')
            self.canvas_1.create_image(0, 0, image=self.thumb_image, anchor=tk.NW)
            self.gray_histogram = self.smooth_image.histogram()
            self.entropy_histogram = self.smooth_entropy_image.histogram()
            self.show_histogram()
            self.show_histogram_entropy()
            self.switch_state_widgets(True)
            self.just_initiated = False
        except:
            self.write_output('>> Cannot read %s!\n' % (path.basename(img_file)))

    def show_histogram(self):
        canvas_width = self.canvas_2.winfo_width()
        canvas_height = self.canvas_2.winfo_height()
        self.canvas_2.delete('all')
        fig = mpl.figure.Figure(figsize=(canvas_width/100, canvas_height/100))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.bar(self.x1, self.gray_histogram, facecolor=[0, 0, 0.25], align='edge', width=1.0)
        if len(self.low_val) > 0:
            x2, sub_histogram = self.get_subhist(self.x1, self.gray_histogram)
            ax.bar(x2, sub_histogram, facecolor=self.phases_color_normed[self.cur_phase], align='edge', width=1.0)
        # Keep this handle alive, or else figure will disappear
        self.fig_photo = draw_figure(self.canvas_2, fig)

    def show_histogram_entropy(self):
        canvas_width = self.canvas_3.winfo_width()
        canvas_height = self.canvas_3.winfo_height()
        self.canvas_3.delete('all')
        fig_2 = mpl.figure.Figure(figsize=(canvas_width/100, canvas_height/100))
        ax_2 = fig_2.add_axes([0, 0, 1, 1])
        ax_2.bar(self.x1, self.entropy_histogram, facecolor=[0, 0, 0.25], align='edge', width=1.0)
        if len(self.low_val) > 0:
            x2, sub_histogram = self.get_subhist_entropy(self.x1, self.entropy_histogram)
            ax_2.bar(x2, sub_histogram, facecolor=self.phases_color_normed[self.cur_phase], align='edge', width=1.0)
        # Keep this handle alive, or else figure will disappear
        self.fig_photo_2 = draw_figure(self.canvas_3, fig_2)

    def get_subhist(self, x1, y1):
        x2 = x1[self.low_val[self.cur_phase]:self.high_val[self.cur_phase]]
        y2 = y1[self.low_val[self.cur_phase]:self.high_val[self.cur_phase]]
        return x2, y2

    def get_subhist_entropy(self, x1, y1):
        x2 = x1[self.low_val_entropy[self.cur_phase]:self.high_val_entropy[self.cur_phase]]
        y2 = y1[self.low_val_entropy[self.cur_phase]:self.high_val_entropy[self.cur_phase]]
        return x2, y2

    def add_phase(self):
        self.pick_color()
        phase = simpledialog.askstring('Phase name', 'Fill in the phase name')
        self.write_output('>> New phase: %s.\n' % phase)
        if len(self.phases) == 0:
            self.delete_button.config(state='normal')
            self.color_button.config(state='normal')
        self.phases.append(phase)
        self.phases_color.append((255, 0, 0))
        self.phases_color_normed.append((1, 0, 0))
        self.phases_color_tk.append('#%02x%02x%02x' % (255, 0, 0))
        self.masked_img.append([])
        self.masked_entropy.append([])
        self.mask.append([])
        self.percentage.append([])
        self.cur_phase = len(self.phases)-1
        low, high = max(0, self.selected_color-30.0), min(255, self.selected_color+30.0)
        self.low_val.append(int(low))
        self.high_val.append(int(high))
        gray_mean = (self.low_val[self.cur_phase]+self.high_val[self.cur_phase])/2
        gray_range = self.high_val[self.cur_phase]-self.low_val[self.cur_phase]
        low_entropy, high_entropy = max(0, self.selected_entropy-30.0), min(255, self.selected_entropy+30.0)
        self.low_val_entropy.append(int(low_entropy))
        self.high_val_entropy.append(int(high_entropy))
        entropy_mean = (self.low_val_entropy[self.cur_phase]+self.high_val_entropy[self.cur_phase])/2
        entropy_range = self.high_val_entropy[self.cur_phase]-self.low_val_entropy[self.cur_phase]
        # update listbox
        self.phases_listbox.select_clear(0, tk.END)
        self.phases_listbox.delete(0, tk.END)
        for idx, phase in enumerate(self.phases):
            self.phases_listbox.insert(tk.END, phase)
            # self.phases_listbox.itemconfig(idx, fg=self.phases_color_tk[self.cur_phase])
        self.phases_listbox.selection_set(int(self.cur_phase))
        # update sliders and labels
        self.slider_low.set(self.low_val[self.cur_phase])
        self.slider_high.set(self.high_val[self.cur_phase])
        # self.label_mean.config(text='Mean gray: %.1f, range: %d' % (gray_mean, gray_range))
        self.slider_low_entropy.set(self.low_val_entropy[self.cur_phase])
        self.slider_high_entropy.set(self.high_val_entropy[self.cur_phase])
        # self.label_mean_entropy.config(text='Mean entropy: %.1f, range: %d' % (entropy_mean, entropy_range))
        self.show_histogram()
        self.show_histogram_entropy()
        self.create_mask()
        self.show_masked_img()

    def pick_color(self):
        self.write_output('>> Pick a phase in the image.\n')
        fig = plt.figure()
        plt.imshow(self.smooth_image_asarray, cmap='gray')
        p1 = plt.ginput(1)
        plt.close(fig)
        x, y = int(p1[0][0]), int(p1[0][1])
        self.selected_color = self.smooth_image_asarray[y, x]
        self.selected_entropy = self.smooth_entropy[y, x]

    def slide_entropy(self, val):
        self.entry_entropy_var.set('%d' % self.slider_entropy.get())
        # self.write_output('>> Entropy calculation window set to %d.' % int(self.entry_entropy_var.get()))
        if len(self.phases) > 0:
            self.calculate_entropy()
            self.entropy_asrgb = np.dstack((self.entropy, self.entropy, self.entropy))
            self.entropy_image = Image.fromarray(self.entropy)
            self.entropy_histogram = self.smooth_entropy_image.histogram()
            self.show_histogram_entropy()
            self.create_mask()
            self.show_masked_img()

    def slide_low(self, val):
        self.entry_low_var.set('%d' % self.slider_low.get())
        if len(self.phases) > 0:
            self.low_val[self.cur_phase] = int(self.slider_low.get())
            if self.low_val[self.cur_phase] >= self.high_val[self.cur_phase]:
                self.slider_high.set(self.low_val[self.cur_phase])
                self.high_val[self.cur_phase] = int(self.slider_high.get())
            # gray_mean = (self.low_val[self.cur_phase]+self.high_val[self.cur_phase])/2
            # gray_range = self.high_val[self.cur_phase]-self.low_val[self.cur_phase]
            # self.label_mean.config(text='Mean gray: %.1f, range: %d' % (gray_mean, gray_range))
            self.show_histogram()
            self.create_mask()
            self.show_masked_img()

    def slide_high(self, val):
        self.entry_high_var.set('%d' % self.slider_high.get())
        if len(self.phases) > 0:
            self.high_val[self.cur_phase] = int(self.slider_high.get())
            if self.high_val[self.cur_phase] <= self.low_val[self.cur_phase]:
                self.slider_low.set(self.high_val[self.cur_phase])
                self.low_val[self.cur_phase] = self.slider_low.get()
            # gray_mean = (self.low_val[self.cur_phase]+self.high_val[self.cur_phase])/2
            # gray_range = self.high_val[self.cur_phase]-self.low_val[self.cur_phase]
            # self.label_mean.config(text='Mean gray: %.1f, range: %d' % (gray_mean, gray_range))
            self.show_histogram()
            self.create_mask()
            self.show_masked_img()

    def slide_low_entropy(self, val):
        self.entry_low_entropy_var.set('%d' % self.slider_low_entropy.get())
        if len(self.phases) > 0:
            self.low_val_entropy[self.cur_phase] = int(self.slider_low_entropy.get())
            if self.low_val_entropy[self.cur_phase] >= self.high_val_entropy[self.cur_phase]:
                self.slider_high_entropy.set(self.low_val_entropy[self.cur_phase])
                self.high_val_entropy[self.cur_phase] = int(self.slider_high_entropy.get())
            # entropy_mean = (self.low_val_entropy[self.cur_phase]+self.high_val_entropy[self.cur_phase])/2
            # entropy_range = self.high_val_entropy[self.cur_phase]-self.low_val_entropy[self.cur_phase]
            # self.label_mean_entropy.config(text='Mean entropy: %.1f, range: %d' % (entropy_mean, entropy_range))
            self.show_histogram_entropy()
            self.create_mask()
            self.show_masked_img()

    def slide_high_entropy(self, val):
        self.entry_high_entropy_var.set('%d' % self.slider_high_entropy.get())
        if len(self.phases) > 0:
            self.high_val_entropy[self.cur_phase] = int(self.slider_high_entropy.get())
            if self.high_val_entropy[self.cur_phase] <= self.low_val_entropy[self.cur_phase]:
                self.slider_low_entropy.set(self.high_val_entropy[self.cur_phase])
                self.low_val_entropy[self.cur_phase] = self.slider_low_entropy.get()
            # entropy_mean = (self.low_val_entropy[self.cur_phase]+self.high_val_entropy[self.cur_phase])/2
            # entropy_range = self.high_val_entropy[self.cur_phase]-self.low_val_entropy[self.cur_phase]
            # self.label_mean_entropy.config(text='Mean entropy: %.1f, range: %d' % (entropy_mean, entropy_range))
            self.show_histogram_entropy()
            self.create_mask()
            self.show_masked_img()

    def create_mask(self):
        self.mask[self.cur_phase] = (self.smooth_image_asarray >= self.low_val[self.cur_phase]) & \
               (self.smooth_image_asarray <= self.high_val[self.cur_phase]) & \
               (self.smooth_entropy >= self.low_val_entropy[self.cur_phase]) & \
               (self.smooth_entropy <= self.high_val_entropy[self.cur_phase])
        self.masked_img[self.cur_phase] = self.smooth_image_asrgb*1
        self.masked_img[self.cur_phase][self.mask[self.cur_phase]] = self.phases_color[self.cur_phase]
        self.masked_entropy[self.cur_phase] = self.smooth_entropy_asrgb*1
        self.masked_entropy[self.cur_phase][self.mask[self.cur_phase]] = self.phases_color[self.cur_phase]

    def show_masked_img(self):
        image_masked_gamma = 255.*(self.gray_image_asarray/255.)**0.05
        self.entropy[~self.roi_mask] = image_masked_gamma[~self.roi_mask]
        for i in range(len(self.phases)):
            self.masked_img[i][~self.roi_mask, 0] = image_masked_gamma[~self.roi_mask]
            self.masked_img[i][~self.roi_mask, 1] = image_masked_gamma[~self.roi_mask]
            self.masked_img[i][~self.roi_mask, 2] = image_masked_gamma[~self.roi_mask]
            self.mask[i][~self.roi_mask] = False
        try:
            self.percentage[self.cur_phase] = (np.sum(self.mask[self.cur_phase])/self.mask_size)*100
            self.label_area.config(text='Phase area: %.1f %%' % self.percentage[self.cur_phase])
            self.label_area.config(foreground=self.phases_color_tk[self.cur_phase])
        except IndexError:
            pass

        if self.radio_choice.get() == 0:
            if len(self.masked_img) > 0:
                if self.display_mode.get() == 1:
                    rgb_image = Image.fromarray(np.uint8(self.masked_img[self.cur_phase]))
                else:
                    rgb_image = copy.deepcopy(self.gray_image)
            else:
                rgb_image = copy.deepcopy(self.gray_image)

            # apply ROI mask
            rgb_image_asarray = np.array(rgb_image)
            rgb_image_shape = rgb_image_asarray.shape
            if len(rgb_image_shape) < 3:
                rgb_image_asarray[~self.roi_mask] = image_masked_gamma[~self.roi_mask]
            else:
                try:
                    rgb_image_asarray[~self.roi_mask, 0] = image_masked_gamma[~self.roi_mask]
                    rgb_image_asarray[~self.roi_mask, 1] = image_masked_gamma[~self.roi_mask]
                    rgb_image_asarray[~self.roi_mask, 2] = image_masked_gamma[~self.roi_mask]
                except IndexError:
                    rgb_image_asarray[~self.roi_mask] = image_masked_gamma[~self.roi_mask]
            rgb_image = Image.fromarray(np.uint8(rgb_image_asarray))

            self.thumb_image = ImageTk.PhotoImage(rgb_image.resize(self.thumb_size, Image.ANTIALIAS))
            self.canvas_1.delete('all')
            self.canvas_1.create_image(0, 0, image=self.thumb_image, anchor=tk.NW)
        else:
            if len(self.masked_entropy) > 0:
                if self.display_mode.get() == 1:
                    rgb_image = Image.fromarray(np.uint8(self.masked_entropy[self.cur_phase]))
                else:
                    rgb_image = copy.deepcopy(self.entropy_image)
            else:
                rgb_image = copy.deepcopy(self.entropy_image)

            # apply ROI mask
            rgb_image_asarray = np.array(rgb_image)
            rgb_image_shape = rgb_image_asarray.shape
            if len(rgb_image_shape) < 3:
                rgb_image_asarray[~self.roi_mask] = image_masked_gamma[~self.roi_mask]
            else:
                try:
                    rgb_image_asarray[~self.roi_mask, 0] = image_masked_gamma[~self.roi_mask]
                    rgb_image_asarray[~self.roi_mask, 1] = image_masked_gamma[~self.roi_mask]
                    rgb_image_asarray[~self.roi_mask, 2] = image_masked_gamma[~self.roi_mask]
                except IndexError:
                    rgb_image_asarray[~self.roi_mask] = image_masked_gamma[~self.roi_mask]
            rgb_image = Image.fromarray(np.uint8(rgb_image_asarray))

            self.thumb_image = ImageTk.PhotoImage(rgb_image.resize(self.thumb_size, Image.ANTIALIAS))
            self.canvas_1.delete('all')
            self.canvas_1.create_image(0, 0, image=self.thumb_image, anchor=tk.NW)

    def change_phase(self, event):
        widget = event.widget
        selection = widget.curselection()
        self.cur_phase = selection[0]
        self.slider_low.set(self.low_val[self.cur_phase])
        self.slider_high.set(self.high_val[self.cur_phase])
        self.slider_low_entropy.set(self.low_val_entropy[self.cur_phase])
        self.slider_high_entropy.set(self.high_val_entropy[self.cur_phase])
        # gray_mean = (self.low_val[self.cur_phase]+self.high_val[self.cur_phase])/2
        # gray_range = self.high_val[self.cur_phase]-self.low_val[self.cur_phase]
        # entropy_mean = (self.low_val_entropy[self.cur_phase]+self.high_val_entropy[self.cur_phase])/2
        # entropy_range = self.high_val_entropy[self.cur_phase]-self.low_val_entropy[self.cur_phase]
        # self.label_mean.config(text='Mean gray: %.1f, range: %d' % (gray_mean, gray_range))
        # self.label_mean_entropy.config(text='Mean entropy: %.1f, range: %d' % (entropy_mean, entropy_range))
        self.label_area.config(foreground=self.phases_color_tk[self.cur_phase])
        self.show_histogram()
        self.show_histogram_entropy()
        self.create_mask()
        self.show_masked_img()

    def initiate_smoothed_images(self):
        self.smooth_image = copy.deepcopy(self.gray_image)
        self.smooth_image_asarray = copy.deepcopy(self.gray_image_asarray)
        self.smooth_image_asrgb = copy.deepcopy(self.gray_image_asrgb)
        self.smooth_entropy = copy.deepcopy(self.entropy)
        self.smooth_entropy_asrgb = copy.deepcopy(self.entropy_asrgb)
        self.smooth_entropy_image = copy.deepcopy(self.entropy_image)

    def callback_entry_smooth_var(self):
        limit_check = max(0.0, min(float(self.entry_smooth_var.get()), 10.0))
        self.slider_smooth.set(limit_check)
        self.image_smoothing(limit_check)

    def callback_entry_entropy_var(self):
        limit_check = max(0, min(int(self.entry_entropy_var.get()), 10))
        self.slider_entropy.set(limit_check)
        self.slide_entropy(limit_check)

    def callback_entry_low_var(self):
        limit_check = max(0, min(int(self.entry_low_var.get()), 255))
        self.slider_low.set(limit_check)
        self.slide_low(limit_check)

    def callback_entry_high_var(self):
        limit_check = max(0, min(int(self.entry_high_var.get()), 255))
        self.slider_high.set(limit_check)
        self.slide_high(limit_check)

    def callback_entry_low_entropy_var(self):
        limit_check = max(0, min(int(self.entry_low_entropy_var.get()), 255))
        self.slider_low_entropy.set(limit_check)
        self.slide_low_entropy(limit_check)

    def callback_entry_high_entropy_var(self):
        limit_check = max(0, min(int(self.entry_high_entropy_var.get()), 255))
        self.slider_high_entropy.set(limit_check)
        self.slide_high_entropy(limit_check)

    def image_smoothing(self, val):
        if not self.just_initiated:
            smoothing_radius = self.slider_smooth.get()
            self.entry_smooth_var.set('%.2f' % self.slider_smooth.get())
            if smoothing_radius > 0:
                self.smooth_image_asarray = gaussian(self.gray_image_asarray, (smoothing_radius, smoothing_radius))
                self.smooth_image_asrgb = np.dstack((self.smooth_image_asarray, self.smooth_image_asarray,
                                                     self.smooth_image_asarray))
                self.smooth_image = Image.fromarray(self.smooth_image_asarray)
                self.smooth_entropy = gaussian(self.entropy, (smoothing_radius, smoothing_radius))
                self.smooth_entropy_asrgb = np.dstack((self.smooth_entropy, self.smooth_entropy, self.smooth_entropy))
                self.smooth_entropy_image = Image.fromarray(self.smooth_entropy)
                # self.write_output('>> Gauss smoothing applied to gray intensities and map of entropy, kernel std = %.1f.\n' %
                #                   smoothing_radius)
            else:
                self.initiate_smoothed_images()
                self.write_output('>> Gauss smoothing switched off.\n')
            self.gray_histogram = self.smooth_image.histogram()
            self.entropy_histogram = self.smooth_entropy_image.histogram()
            self.show_histogram()
            self.show_histogram_entropy()
            if len(self.phases) > 0:
                self.create_mask()
                self.show_masked_img()
            else:
                if self.radio_choice.get() == 0:
                    self.thumb_image = ImageTk.PhotoImage(self.smooth_image.resize(self.thumb_size, Image.ANTIALIAS))
                else:
                    self.thumb_image = ImageTk.PhotoImage(self.smooth_entropy_image.resize(self.thumb_size,
                                                                                           Image.ANTIALIAS))
                self.canvas_1.delete('all')
                self.canvas_1.create_image(0, 0, image=self.thumb_image, anchor=tk.NW)

    def delete_phase(self):
        del self.phases[self.cur_phase]
        del self.low_val[self.cur_phase]
        del self.high_val[self.cur_phase]
        del self.masked_img[self.cur_phase]
        del self.mask[self.cur_phase]
        del self.low_val_entropy[self.cur_phase]
        del self.high_val_entropy[self.cur_phase]
        del self.masked_entropy[self.cur_phase]
        del self.phases_color[self.cur_phase]
        del self.phases_color_normed[self.cur_phase]
        del self.phases_color_tk[self.cur_phase]
        self.cur_phase = 0
        if len(self.phases) == 0:
            self.delete_button.config(state='disable')
            self.color_button.config(state='disable')
            gray_mean, gray_range, entropy_mean, entropy_range = 0, 0, 0, 0
            self.slider_low.set(0)
            self.slider_high.set(0)
            self.slider_low_entropy.set(0)
            self.slider_low_entropy.set(0)
            self.phases_listbox.select_clear(0, tk.END)
            self.phases_listbox.delete(0, tk.END)
        else:
            gray_mean = (self.low_val[self.cur_phase]+self.high_val[self.cur_phase])/2
            gray_range = self.high_val[self.cur_phase]-self.low_val[self.cur_phase]
            entropy_mean = (self.low_val_entropy[self.cur_phase]+self.high_val_entropy[self.cur_phase])/2
            entropy_range = self.high_val_entropy[self.cur_phase]-self.low_val_entropy[self.cur_phase]
            # update listbox
            self.phases_listbox.select_clear(0, tk.END)
            self.phases_listbox.delete(0, tk.END)
            for idx, phase in enumerate(self.phases):
                self.phases_listbox.insert(tk.END, phase)
            self.phases_listbox.selection_set(int(self.cur_phase))
            self.slider_low.set(self.low_val[self.cur_phase])
            self.slider_high.set(self.high_val[self.cur_phase])
            self.slider_low_entropy.set(self.low_val_entropy[self.cur_phase])
            self.slider_high_entropy.set(self.high_val_entropy[self.cur_phase])
            self.show_histogram()
            self.show_histogram_entropy()
            self.show_masked_img()
        # self.label_mean.config(text='Mean gray: %.1f, range: %d' % (gray_mean, gray_range))
        # self.label_mean_entropy.config(text='Mean entropy: %.1f, range: %d' % (entropy_mean, entropy_range))

    def get_color(self):
        color = askcolor()
        self.phases_color[self.cur_phase] = color[0]
        self.phases_color_tk[self.cur_phase] = color[1]
        color_normed = [i/256 for i in self.phases_color[self.cur_phase]]
        self.phases_color_normed[self.cur_phase] = color_normed
        # update listbox
        self.phases_listbox.select_clear(0, tk.END)
        self.phases_listbox.delete(0, tk.END)
        for idx, phase in enumerate(self.phases):
            self.phases_listbox.insert(tk.END, phase)
        self.phases_listbox.selection_set(int(self.cur_phase))
        self.show_histogram()
        self.show_histogram_entropy()
        self.create_mask()
        self.show_masked_img()

    def calculate_entropy(self):
        self.entropy = entropy(self.gray_image_asarray/255, disk(int(self.entry_entropy_var.get())))
        entropy_temp = np.array(self.entropy)
        self.entropy = entropy_temp/np.max(entropy_temp)*255

    def image_changed(self):
        self.show_masked_img()

    def scale_image(self):
        img_file = select_image_file_prompt('Choose an image file', getcwd())
        original_image = mpimg.imread(img_file)
        self.write_output('>> Image %s loaded for the scaling.\n' % (path.basename(img_file)))
        img_image = Image.fromarray(original_image)
        img_image = img_image.resize((int(original_image.shape[1]*self.factor),
                                      int(original_image.shape[0]*self.factor)), Image.ANTIALIAS)
        original_image = np.array(img_image)
        gray_image_asarray = np.asarray(rgb2gray(original_image))
        fig = plt.figure()
        plt.imshow(gray_image_asarray, cmap='gray')
        [p1, p2] = plt.ginput(2)
        x = np.round(np.array([p1[0], p2[0]]))
        y = np.round(np.array([p1[1], p2[1]]))
        length = np.sqrt((x[0]-x[1])**2+(y[0]-y[1])**2)
        def_length = simpledialog.askfloat('Scaling', 'Define reference length:')
        self.scale = length/def_length
        self.write_output('>> Scale: %.2f px/unit_of_length.\n' % self.scale)
        plt.close(fig)

    def load_roi(self):
        try:
            img_file = select_image_file_prompt('Choose an image file', getcwd())
            original_image = mpimg.imread(img_file)
            self.write_output('>> ROI from image %s loaded.\n' % (path.basename(img_file)))
            factor = self.original_image.shape[0]/original_image.shape[0]
            self.write_output('>> ROI image scaled by a factor of %.3f.\n' % factor)
            img_image = Image.fromarray(original_image)
            img_image = img_image.resize((int(original_image.shape[1]*factor), int(original_image.shape[0]*factor)),
                                         Image.NEAREST)
            original_image = np.array(img_image)
            self.roi_mask = np.asarray(rgb2gray(original_image), dtype=bool)
            self.mask_size = np.sum(self.roi_mask)
            self.show_masked_img()
        except IndexError:
            self.write_output('>> ROI could not be loaded, the height/width ratio does not match the analyzed image.')

    def add_roi(self):
        plt.imsave(arr=self.original_image/255, fname='temp.jpg')  # save the reference image to a file
        try:
            subprocess.call(["python3", "aux_roi.py"])
        except FileNotFoundError:
            subprocess.call(["python", "aux_roi.py"])
        self.roi_mask = np.asarray(rgb2gray(mpimg.imread('mask.jpg')), dtype=bool)  # read the mask file
        os.remove('temp.jpg')  # delete the reference image
        os.remove('mask.jpg')  # delete the mask image
        self.mask_size = np.sum(self.roi_mask)
        self.show_masked_img()
        self.write_output('>> ROI selected by hand.\n')

    def export_all(self):
        temp_dir = os.getcwd()
        os.chdir('output')
        time_str = time.strftime('-%Y_%m_%d-%H_%M_%S')
        new_folder_name = self.project_name+time_str
        os.makedirs(new_folder_name, 0o777)
        os.chdir(temp_dir)
        project_path = 'output/'+new_folder_name+'/'
        plt.imsave(arr=self.original_image/255, fname=project_path+'original_image.png')
        plt.imsave(arr=self.entropy/255, fname=project_path+'entropy.png', cmap='gray')
        f_out = open(project_path+'phases_summary.txt', 'w')
        try:
            merged_mask = self.mask[0]
            for i in range(1, len(self.phases)):
                merged_mask += self.mask[i]
            plt.imsave(arr=merged_mask/255, fname=project_path+'merged_mask_all_phases.jpg', cmap=cm.gray)
        except:
            pass
        for i in range(len(self.phases)):
            plt.imsave(arr=self.masked_img[i]/255, fname=project_path+self.phases[i]+'.png')
            plt.imsave(arr=self.mask[i], fname=project_path+'mask_'+self.phases[i]+'.jpg', cmap=cm.gray)
            f_out.write('Phase: %s\tPercentage: %.2f%%\tGray min: %d\tGray max: %d\tEntropy min: %d'
                        '\tEntropy max: %d\n' % (self.phases[i], self.percentage[i], self.low_val[i], self.high_val[i],
                                                 self.low_val_entropy[i], self.high_val_entropy[i]))
            key_points = detect_blobs(np.array(self.mask[i], dtype=np.uint8)*255)
            try:
                f_out_area = open(project_path+'phase_'+self.phases[i]+'_areas.txt', 'w')
                f_out_diameter = open(project_path+'phase_'+self.phases[i]+'_diameters.txt', 'w')
                x, y = [], []
                for key_point in key_points:
                    x.append(key_point.pt[0]/self.scale)
                    y.append(key_point.pt[1]/self.scale)
                    diameter = key_point.size/self.scale
                    area = (diameter**2)*np.pi/4
                    f_out_area.write('%.12f\n' % area)
                    f_out_diameter.write('%.6f\n' % diameter)
                f_out_area.close()
                # kde_plot(x, y, project_path+'phase_'+self.phases[i]+'_kde_density.jpg', self.original_image)
            except:
                self.write_output('>> The density of the phase could not be plotted.\n')
            '''
            # PLOTTING FOR THE ARTICLE
            #
            fig = plt.figure(figsize=(18.5, 10.5))
            gs = gridspec.GridSpec(1, 2, height_ratios=[1])
            fig.add_subplot(gs[0])
            ax = plt.gca()
            im = plt.imshow(self.original_image, cmap='gray')
            divider = make_axes_locatable(ax)
            plt.axis('off')
            cax = divider.append_axes("right", size="8%", pad=0.08)
            plt.colorbar(im, cax=cax)
            fig.add_subplot(gs[1])
            plt.imshow(self.masked_img[i]/255)
            plt.axis('off')
            plt.subplots_adjust(wspace=0.1)
            plt.savefig(project_path+'_original_image_scale.png', bbox_inches='tight')
            #
            #
            fig = plt.figure(figsize=(18.5, 10.5))
            gs = gridspec.GridSpec(1, 2, height_ratios=[1])
            fig.add_subplot(gs[0])
            ax = plt.gca()
            im = plt.imshow(self.entropy, cmap='jet')
            divider = make_axes_locatable(ax)
            plt.axis('off')
            cax = divider.append_axes("right", size="8%", pad=0.08)
            plt.colorbar(im, cax=cax)
            fig.add_subplot(gs[1])
            plt.imshow(self.masked_img[i]/255)
            plt.axis('off')
            plt.subplots_adjust(wspace=0.1)
            plt.savefig(project_path+'_entropy_scale.png', bbox_inches='tight')
            #
            #
            fig = plt.figure(figsize=(18.5, 10.5))
            gs = gridspec.GridSpec(1, 2, height_ratios=[1])
            fig.add_subplot(gs[0])
            ax = plt.gca()
            im = plt.imshow(self.smooth_entropy, cmap='jet')
            divider = make_axes_locatable(ax)
            plt.axis('off')
            cax = divider.append_axes("right", size="8%", pad=0.08)
            plt.colorbar(im, cax=cax)
            fig.add_subplot(gs[1])
            plt.imshow(self.masked_img[i]/255)
            plt.axis('off')
            plt.subplots_adjust(wspace=0.1)
            plt.savefig(project_path+'_smoothing_scale.png', bbox_inches='tight')
            #  
            
            # Draw detected blobs as red circles.
            import cv2
            # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
            im_with_keypoints = cv2.drawKeypoints(np.array(self.masked_img[i], dtype=np.uint8)*255, key_points, np.array([]),
                                                  (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            cv2.imshow("Keypoints", im_with_keypoints)
            cv2.waitKey(0)
            '''

        f_out.close()
        self.write_output('>> Masked images, mask, and statistics exported to %s.\n' % project_path)


root = tk.Tk()
my_gui = Gui(root)
root.mainloop()

