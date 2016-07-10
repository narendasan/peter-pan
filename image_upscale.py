import cv2
src = cv2.imread("intro-bgSmall.jpg")
dest_inter_cubic = cv2.resize(src, None, fx=4, fy=4, interpolation = cv2.INTER_CUBIC)
cv2.imwrite("intro-bgSmall-upsized-cubic.jpg", dest_inter_cubic)3