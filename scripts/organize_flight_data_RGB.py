import os
from exiftool import ExifToolHelper
import PySimpleGUI as sg

sg.theme("DarkTeal2")

# Define layout of GUI
layout = [
    [sg.T("")],
    [sg.Text("Choose a folder: "), sg.Input(), sg.FolderBrowse(key="-PATH-")],
    [sg.Text("Output folder:     "), sg.InputText(key="-OUTPATH-")],
    [sg.Button("Submit")],
    [sg.Button("Close")]
]

# Create window
window = sg.Window('My Flights Browser', layout, size=(600,150))

# Loop to handle user interactions with the GUI
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Submit":
        path = values["-PATH-"]
        if path == "":
            sg.Print("Please input a folder with the images!")
            continue
        outpath = values["-OUTPATH-"]
        if outpath == '':
            sg.Print("Creating output folder: output_sort")
            outpath = os.path.join(path, "output_sort")
        else:
            sg.Print("Creating output folder: ", outpath)
            outpath = os.path.join(path, outpath)
        break
    elif event == "Close":
        window.close()
        break

# Get list of image files in the input directory
files = []
for root, dirs, filenames in os.walk(path):
    for filename in filenames:
        if filename.endswith((".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG")):
            files.append(os.path.join(root, filename))
files.sort()

# Use ExifTool to get the creation date of each image file
with ExifToolHelper() as et:
    metadata = et.get_tags(files, 'EXIF:CreateDate')

# Loop through the metadata to find the start and end of each flight and move the image files to the appropriate output folder
start_files = []
flight_count = 0
for i, d in enumerate(metadata):
    datetime_object = datetime.strptime(d['EXIF:CreateDate'], '%Y:%m:%d %H:%M:%S')

    # Check if this is the start of a new flight
    if i == 0 or datetime_object - datetime_object_0 > datetime.timedelta(minutes=2):
        flight_count += 1
        sg.Print(f"Flight {flight_count} start file: {d['SourceFile']}")
        start_files.append(d['SourceFile'])
        if not os.path.exists(os.path.join(outpath, f"Flight {flight_count}")):
            os.makedirs(os.path.join(outpath, f"Flight {flight_count}"))

    # Move the file to the appropriate output folder
    name = os.path.basename(files[i])
    output_file = os.path.join(outpath, f"Flight {flight_count}", name)
    os.replace(files[i], output_file)

    datetime_object_0 = datetime_object

sg.Print("DONE!")

window.close()

