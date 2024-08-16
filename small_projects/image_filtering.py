import numpy as np
import cv2   


image_path = 'image.png'
image = cv2.imread(image_path)

# Defining a sharpening filter using a NumPy array. The sharpening filter (or kernel) is a 3x3 matrix.
# In this kernel:
# - The center value (9) amplifies the current pixel value.
# - The surrounding values (-1) subtracts the average value of the neighboring pixels.
sharpen_kernel = np.array([[-1,-1,-1], 
                           [-1, 9,-1],
                           [-1,-1,-1]])
# The sum of all weights in the kernel must be 1.

# Setting a threshold value for pixel intensity (this could also be made interactive)
threshold_value = 200

# The GUI will allow users to:
# 1. Adjust brightness and contrast.
# 2. Apply a sharpening filter.
# 3. Display the mean color of the image.
# 4. Highlight pixels above a set threshold.
# Define a callback function for trackbar position changes

def update_image(x):

    # Read trackbar positions
    alpha = cv2.getTrackbarPos('Contrast', 'App') / 50.0
    beta = cv2.getTrackbarPos('Brightness', 'App') - 50
    apply_sharpen = cv2.getTrackbarPos('Toggle Sharpening', 'App')
    show_mean_color = cv2.getTrackbarPos('Toggle Mean Color', 'App')
    highlight_threshold = cv2.getTrackbarPos('Toggle Highlighting', 'App')
    output = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    if apply_sharpen:
        output = cv2.filter2D(output, -1, sharpen_kernel)

    if show_mean_color:
        mean_values = np.mean(output, axis=(0, 1)) # Calculate mean color values
        output = np.ones_like(output) * mean_values.astype(np.uint8)

    if highlight_threshold:
        mask = np.any(output > threshold_value, axis=-1)
        output[mask] = [255, 0, 0]

    cv2.imshow('App', output)


cv2.namedWindow('App')
cv2.createTrackbar('Brightness', 'App', 50, 100, update_image)
cv2.createTrackbar('Contrast', 'App', 50, 100, update_image)
cv2.createTrackbar('Toggle Sharpening', 'App', 0, 1, update_image)
cv2.createTrackbar('Toggle Mean Color', 'App', 0, 1, update_image)
cv2.createTrackbar('Toggle Highlighting', 'App', 0, 1, update_image)
cv2.imshow('App', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
