import cv2
import os


image_path = "images/tea-cup.jpeg"
scale_percent = 50

# Read the image
image = cv2.imread(image_path)


# Function to display an image
def display_image(image):
    # Display the image
    cv2.imshow("Tea cup image", image)
    # Wait Key
    cv2.waitKey(0)


# Function to resize an image
def resize_image(image, scale_percent):
    # Calculate the new dimensions
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    new_dim = (width, height)
    # Resize the image
    resized = cv2.resize(image, new_dim)
    return resized


# Coordinates to crop an image
start_row, start_col = 300, 300
end_row, end_col = 800, 800


# Function to crop an image
def crop_image(image, start_row, start_col, end_row, end_col):
    cropped_image = image[start_row:end_row, start_col:end_col]
    return cropped_image


# Resize the image
resized_image = resize_image(image, scale_percent)
# Crop image
cropped_image = crop_image(image, start_row, start_col, end_row, end_col)
# Call function to display the resized image
# display_image(cropped_image)


# FILTRERING AND ENHANCEMENT


def apply_blur(image, kernel_size):
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return blurred_image


def apply_sharpening(image):
    sharpening_kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
    
    sharpened_image = cv2.filter2D(image, -1, sharpening_kernel)
    return sharpened_image


def main():
    # Reference to the path of our image
    image_path = "images/tea-cup.jpeg"
    image = cv2.imread(image_path)
    # Kernel size is for bluerring / defines the size of the filter
    kernel_size = 5
    blurred_image = apply_blur(image, kernel_size)
    sharpened_image = apply_sharpening(image)
    # Display original image
    display_image(image)
    # Sharpened Image
    display_image(sharpened_image)
    # Blurred Image
    display_image(blurred_image)


# Call our main function
# main()


# FEATURE DETECTION AND MATCHING


def feature_detection_and_matching(image1_path, image2_path):
    # Load the images
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    # Convert to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    # Detect keypoints and descriptors
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)
    # Use BFMatcher to match descriptors
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    # Apply Lowe's ratio test to filter out weak matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            # Wrap into a list
            good_matches.append([m])
    # Draw matches
    matched_image = cv2.drawMatchesKnn(image1, keypoints1, image2, keypoints2, good_matches, None, flags=2)
    return matched_image


image1_path = "images/tea-cup.jpeg"
image2_path = "images/tea-cup-3.jpeg"
matched_image = feature_detection_and_matching(image1_path, image2_path)
# display_image(matched_image)


# IMAGE MATCHER


def feature_detection_and_matching(image1_path):
    # Load the images
    image1 = cv2.imread(image1_path)
    # Select the ROI by drawing a bounding box
    roi = cv2.selectROI("Select ROI Tea-Cup", image1, False, False)
    # Crop the selected ROI from the image
    x, y, w, h = roi
    cropped = image1[y:y+h, x:x+w]
    # Convert to grayscale
    gray1 = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    # Detect keypoints and descriptors
    _, descriptors1 = sift.detectAndCompute(gray1, None)
    return descriptors1


def feature_matching(image):
    # Convert target image to grayscale
    gray_image2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    # Detect keypoints and descriptors
    _, descriptors2 = sift.detectAndCompute(gray_image2, None)
    # Use BFMatcher to match descriptors
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    # Apply Lowe's ratio test to filter out weak matches
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            # Wrap into a list
            good_matches.append([m])
    # Define a minimum number of good matches
    MIN_MATCH_COUNT = 7
    return len(good_matches) >= MIN_MATCH_COUNT


def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filepath.lower().endswith(('.jpg', '.jpeg', 'png')):
            # If true, read the image
            image = cv2.imread(filepath)
            # Check if current image matches the template image
            is_match = feature_matching(image)
            # Write the result on the image
            result_text = "Match found" if is_match else "No match"
            cv2.putText(image, result_text, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            #Show the image
            display_image(image)


image1_path = "images/tea-cup.jpeg"
folder_path = "images"
descriptors1 = feature_detection_and_matching(image1_path)
# process_folder(folder_path)
