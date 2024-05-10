#perspective transform 원근 변환

import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread("kmu_img.jpg")
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

#Pn = []
p1 = [650,750]
p2 = [1450,750]
p3 = [1900,1000]
p4 = [300,1000]

corner_points_arr = np.float32([p1,p2,p3,p4])
height,width = image.shape[:2]

image_p1 = [0, 0]
image_p2 = [width, 0]
image_p3 = [width, height]
image_p4 = [0, height]

image_params = np.float32([image_p1, image_p2, image_p3, image_p4])
mat = cv2.getPerspectiveTransform(corner_points_arr, image_params)
image_transformed = cv2.warpPerspective(image, mat, (width, height))

plt.imshow(cv2.cvtColor(image_transformed, cv2.COLOR_BGR2RGB))

hcon = cv2.hconcat([image, image_transformed])
hcon = cv2.resize(hcon, (0, 0), fx=0.5, fy=0.5)
cv2.imshow('bird-eye-view', hcon)
cv2.waitKey(0)
cv2.destroyAllWindows()


# while True:
#     ret, frame = video.read()
#     if not ret:
#         break

#     height, width = frame.shape[:2]
#     roi = frame[int(height * 0.6):height, :]

#     gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)
#     edges = cv2.Canny(blur, 50, 150)
#     lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50)

    
#     cv2.imshow("video", video)
#     cv2.imshow("edges", edges)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.warpPerspective()
# video.release()
# cv2.destroyAllWindows()