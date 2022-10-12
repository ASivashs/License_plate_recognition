from license_plate_recognition import license_plate_recognition
import json
import os


def main():
    license_plates = {}
    for dirname, _, filenames in os.walk('images_jpg/'):
        for filename in filenames:
            license_plate_result = license_plate_recognition(dirname + filename)
            license_plates = {license_plate_result[0]: license_plate_result[1]}
            print(f'{license_plate_result[0]}: {license_plate_result[1]}]')
    
    print(license_plates)
    with open('responsed_license_plates.json', 'w') as save_file:
        json.dump(license_plates, save_file, indent=6)


if __name__ == '__main__':
    main()
