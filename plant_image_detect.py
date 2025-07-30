import seaborn as sns
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

def segment_plant_by_green(image_bgr, lG = 4, uG = 70, green_threshold=5000):
    """
    Segments green plant from background. Returns mask, segmented image,
    and boolean flag whether a plant is present.
    Parameters: lg: lower green hue threshold, default is 4,
                ug: upper green hue threshold, default is 70,
                image_bgr: input image in BGR format,
                green_threshold: minimum number of green pixels to consider a plant present.
    Returns: mask_clean_2: binary mask of the plant,
             result_2: segmented image with plant,
             has_plant: boolean flag indicating if a plant is detected.
    """
    control_bgr = cv2.imread(os.path.join(os.getcwd(), '/LunarAgent/plant_report/test/imaging_lens_position_7.0_cam_0_1730496602.jpg')) #control image
    control_bgr = cv2.GaussianBlur(control_bgr, (3,3), 0)
    image_bgr = cv2.GaussianBlur(image_bgr, (3,3), 0)

    # Convert to HSV
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    control_hsv = cv2.cvtColor(control_bgr, cv2.COLOR_BGR2HSV)

    plant_diff = cv2.absdiff(image_hsv, control_hsv)

    #pick hue and saturation
    hue_diff = plant_diff[:,:,0]
    sat_diff = plant_diff[:,:,1]

    #set thresholds
    _, hue_thresh = cv2.threshold(hue_diff, 35, 70, cv2.THRESH_BINARY)
    _, sat_thresh = cv2.threshold(sat_diff, 60, 255, cv2.THRESH_BINARY)

    # Green color range (tweak if needed)
    lower_green = np.array([lG, 40, 40])
    upper_green = np.array([uG, 255, 255])

    # Create mask
    mask_2 = cv2.inRange(plant_diff, lower_green, upper_green)
    new_mask = cv2.bitwise_and(hue_thresh, sat_thresh)
    mask = cv2.bitwise_and(new_mask, new_mask, mask=new_mask)

    # Morphological cleaning
    kernel = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # Morphological cleaning_2
    mask_clean_2 = cv2.morphologyEx(mask_2, cv2.MORPH_OPEN, kernel, iterations=2)

    # Count green pixels
    green_pixels = cv2.countNonZero(mask_clean)
    has_plant = green_pixels > green_threshold  # auto-skip threshold

    # Apply mask
    #result = cv2.bitwise_and(image_bgr, image_bgr, mask=mask_clean)
    result_2 = cv2.bitwise_and(image_bgr, image_bgr, mask=mask_clean_2)

    return mask_clean_2, result_2, has_plant

def find_plant_vert_height(mask_inp, genPlot = False):
  
  """Finds the vertical height of the plant in the image mask.
  Returns the height in pixels.
  If genPlot is True, generates a plot of the binary mask and centroids.
  """

  gray_nr = cv2.cvtColor(mask_inp, cv2.COLOR_BGR2GRAY)
  _, binary_nr = cv2.threshold(gray_nr, 1, 255, cv2.THRESH_BINARY)
  num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_nr) #inbuilt method for finding centroid of clusters

  #remove random blobs
  min_area = 500
  valid_components = [
      stats[i] for i in range(1, num_labels)
      if stats[i, cv2.CC_STAT_AREA] >= min_area
  ]
  y_top = min(comp[cv2.CC_STAT_TOP] for comp in valid_components)
  y_bottom = max(comp[cv2.CC_STAT_TOP] + comp[cv2.CC_STAT_HEIGHT] for comp in valid_components)

  if genPlot:
    plt.imshow(binary_nr, cmap='gray')
    plt.axis('off')
    sns.scatterplot(x=centroids[:, 0], y=centroids[:, 1], s = 5, color = 'blue')
    sns.scatterplot(x = [0,0], y = [y_top, y_bottom], color = 'red')

  return int(y_bottom - y_top)

