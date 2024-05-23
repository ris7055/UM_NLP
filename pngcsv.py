import cv2
import numpy as np
import csv

# Load the image
image = cv2.imread("C:/Users/Wei/Downloads/B-GF.jpg")
print(image.shape)
image = cv2.resize(image,(400,300))
# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use a threshold to separate the floor plan from the background
_, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
cv2.imshow("Show",threshold)
cv2.waitKey(0)
# Find the contours in the threshold image
contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Convert the image data to a numpy array
data = np.array(threshold)
# Change 0 to 1
data[data == 0] = 1
# Change 255 to 0
data[data == 255] = 0

# Find the first X columns that only contain 0
first_zero_cols = [i for i in range(data.shape[1]) if np.all(data[:, i] == 0)]
# Delete the first X columns
for col in sorted(first_zero_cols, reverse=True):
    data = np.delete(data, col, axis=1)

# Find the last X columns that only contain 0
last_zero_cols = [i for i in range(data.shape[1]-1, -1, -1) if np.all(data[:, i] == 0)]

# Delete the last X columns
for col in sorted(last_zero_cols, reverse=True):
    data = np.delete(data, col, axis=1)

print(data.shape)

# Open a new CSV file to write the pixel data
with open('pixels.csv', 'w', newline='') as f:
    writer = csv.writer(f)

    # Write each row of pixel data
    for row in data:
        writer.writerow(row)
