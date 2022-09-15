import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from pathlib import Path
import os

LIGHT_BLUE = "#58C5BC"
DEFAULT_STROKE = 3
DEFAULT_IMAGE_SIZE = 512
DEFAULT_DRAWING_MODE = "polygon"
DEFAULT_IMAGE = "images/img1.png"
DEFAULT_MASKS_DIR = Path("masks").resolve() # use absolutes

st.sidebar.subheader("Binary segmentation annotation app")
st.sidebar.text("Click the image to annotate. \nRight mouse click to complete a poly")
# uploaded_image = st.sidebar.file_uploader("Image to annotate:", type=["png"]) # , "jpg", "jpeg", "tiff", "tif"

# why limit to just pngs?
uploaded_image = st.sidebar.file_uploader("Image to annotate:", type=["png", "jpg", "jpeg", "tiff", "tif"]) 

mask_dir = st.sidebar.text_input('Mask directory path:', DEFAULT_MASKS_DIR) # where masks will be saved
if mask_dir != DEFAULT_MASKS_DIR:
    if not os.path.exists(mask_dir):
        st.sidebar.write(f"{mask_dir} is not a valid path!")

if uploaded_image: 
    image_to_annotate = Image.open(uploaded_image)

    image_to_annotate_name = uploaded_image.name
    st.text(f"Annotating {image_to_annotate_name}")
else: # for testing
    image_to_annotate = Image.open(DEFAULT_IMAGE)
    image_to_annotate_name = "test_mask.png"

## compute input image dimensions for later scaling
try:
    nx, ny, nd = np.array(image_to_annotate).shape
except: # 1band greyscale
    nx, ny = np.array(image_to_annotate).shape

save_mask_filename = Path(mask_dir, image_to_annotate_name)

if st.sidebar.button(f"Mark as 100% background and save"): # set every pixel to 0
    mask_arr = np.zeros((nx, ny), dtype=np.uint8)
    mask_img = Image.fromarray(mask_arr).convert('L')
    mask_img.save(save_mask_filename)
    st.sidebar.write(f"Saved {save_mask_filename}")

if st.sidebar.button(f"Mark as 100% target and save"): # set every pixel to 255
    mask_arr = np.ones((nx, ny), dtype=np.uint8) * 255
    mask_img = Image.fromarray(mask_arr).convert('L')
    mask_img.save(save_mask_filename)
    st.sidebar.write(f"Saved {save_mask_filename}")

# Otherwise draw the mask

canvas_result = st_canvas(
    fill_color = LIGHT_BLUE,
    stroke_color = LIGHT_BLUE,
    stroke_width = DEFAULT_STROKE,
    background_image = image_to_annotate,
    height = DEFAULT_IMAGE_SIZE,
    width = DEFAULT_IMAGE_SIZE,
    drawing_mode = DEFAULT_DRAWING_MODE, # drawing_mode
    display_toolbar = True
)

# st.subheader("Mask")
if canvas_result.image_data is not None: # if there is annotation generate the mask
    mask_arr = canvas_result.image_data[:,:,0] # return first channel
    mask_arr = np.where(mask_arr > 0, 1, 0).astype(np.uint8) # binarise based on larger than zero

    target_percentage = int(np.sum(mask_arr) / (DEFAULT_IMAGE_SIZE * DEFAULT_IMAGE_SIZE) * 100)
    st.write(f"Target percentage: {target_percentage:.2f}%")

    mask_arr = mask_arr * 255 # convert to 0-255
    st.image(mask_arr) # display the mask
    st.text("Right click image to save mask interactively or use the button below")

    if st.button(f"Save mask"):
        mask_img = Image.fromarray(mask_arr).convert('L')

        #rescale images back to original size
        size = ny, nx
        mask_img = mask_img.resize(size)

        mask_img.save(save_mask_filename)
        st.write(f"Saved {save_mask_filename}")

