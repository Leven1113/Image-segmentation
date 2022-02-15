import numpy as np
from tkinter import filedialog, PhotoImage
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
# import matplotlib.pyplot as plt
# import seaborn as sns
import cv2


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def select_files_prompt(message, directory):
    files = filedialog.askopenfilenames(title=message, initialdir=directory)
    return files


def select_file_prompt(message, directory):
    file = filedialog.askopenfilename(title=message, initialdir=directory)
    return file


def select_image_file_prompt(message, directory):
    ftypes = [('Digital image files', '*.tiff;*.tif;*.jpeg;*.jpg;*.png;*.gif;*.bmp')]
    file = filedialog.askopenfilename(title=message, initialdir=directory, filetypes=ftypes)
    return file


def draw_figure(canvas, figure, loc=(0, 0)):
    # loc: location of top-left corner of figure on canvas in pixels.
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = PhotoImage(master=canvas, width=figure_w, height=figure_h)
    # Position: convert from top-left anchor to center anchor
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
    # Unfortunately, there's no accessor for the pointer to the native renderer
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    # Return a handle which contains a reference to the photo object (must be kept live or the picture disappears)
    return photo


def detect_blobs(mask):
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 0
    params.maxThreshold = 256
    params.filterByArea = False
    params.minArea = 2
    params.filterByCircularity = False
    params.minCircularity = 0.1
    params.filterByConvexity = False
    params.minConvexity = 0.0
    params.maxConvexity = 1.0
    params.filterByInertia = False
    params.minInertiaRatio = 0.0
    params.maxInertiaRatio = 1.0
    detector = cv2.SimpleBlobDetector_create(params)
    reverse_mask = 255-mask
    keypoints = detector.detect(reverse_mask)
    return keypoints

'''
def kde_plot(x, y, filename, img):
    sns.set_style('white')
    sns.set_context('notebook', font_scale=1, rc={"lines.linewidth": 0.5})
    g = sns.kdeplot(x, y, shade=True, cut=2, cmap='jet', shade_lowest=False, alpha=0.5, zorder=2)
    g.imshow(img,aspect = g.get_aspect(), extent = g.get_xlim()+g.get_ylim(), zorder = 1)
    plt.tick_params(axis='both', which='major')
    sns.despine()
    plt.savefig(filename)
'''