from license_plate_recognition import license_plate_recognition, check_slash
import json
import os


def response(img_path):
    """
    Recognize license plate number.
    :arg1: Full path to image.
    :return: image_name, recognized license plate number.
    """
    license_plate = license_plate_recognition(img_path)
    return license_plate


def main():
    """
    Recognize license plate numbers in dataset (images_jpg).
    """
    license_plates = {}
    path = check_slash().join(__file__.split(check_slash())[:-2]) + f'{check_slash()}images_jpg{check_slash()}'
    for dirname, _, filenames in os.walk(path):
        for filename in filenames:
            license_plate_result = license_plate_recognition(dirname + filename)
            license_plates[license_plate_result[0]] = license_plate_result[1]
            print(f'{license_plate_result[0]}: {license_plate_result[1]}]')

    with open('responsed_license_plates.json', 'w') as save_file:
        json.dump(license_plates, save_file, indent=6)


if __name__ == '__main__':
    main()
