import cv2
import imutils
import numpy as np
import pytesseract
import sys

from .settings import check_slash


if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'D:\\Programs\\Tesseract\\tesseract.exe'

def license_plate_recognition(image_name=None):
    """
    Detect license plate and convert license plate number to image.
    :arg1: img path.
    :return: tuple with image name and responsed number or None.
    """

    img = cv2.imread(image_name, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (600, 400))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 13, 15, 15)

    edged = cv2.Canny(gray, 30, 200)
    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screen_cnt = None

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * peri, True)

        if len(approx) == 4:
            screen_cnt = approx
            break

    detected = False if screen_cnt is None else True

    if detected:
        cv2.drawContours(img, [screen_cnt], -1, (255, 0, 0), 4)

    mask = np.zeros(gray.shape, np.uint8)
    try:
        new_image = cv2.drawContours(mask, [screen_cnt], 0, 255, -1)
    except Exception as exc:
        img_name = image_name.split(check_slash())[-1]
        return (img_name, None)

    new_image = cv2.bitwise_and(img, img, mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx+1, topy:bottomy+1]

    license_plate = pytesseract.image_to_string(Cropped, config='--psm 11')

    # This block illustrate image and cropped image
    img = cv2.resize(img,(500,300))
    Cropped = cv2.resize(Cropped,(400,200))
    # cv2.imshow('car', img)
    # cv2.imshow('Cropped', Cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    img_name = image_name.split(check_slash())[-1]
    
    filename_responsed = f'responsed_images{check_slash()}responsed_{img_name}'
    cv2.imwrite(filename_responsed, img)

    filename_cropped = f'cropped_images{check_slash()}cropped_{img_name}'
    cv2.imwrite(filename_cropped, Cropped)

    license_plate = license_plate.strip()
    return (img_name, license_plate)
