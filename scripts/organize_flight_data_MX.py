from exiftool import ExifToolHelper
import os
from os.path import join, splitext, split
from shutil import move
import PySimpleGUI as sg

# Set up the GUI
sg.theme("DarkTeal2")
layout = [[sg.T("")],
          [sg.Text("Choose an input folder:   "), sg.Input(), sg.FolderBrowse(key="-PATH-")],
          [sg.Text("Choose an output folder: "), sg.Input(), sg.FolderBrowse(key="-OUTPATH-")],
          [sg.Text("Flight name: "), sg.InputText(key="-name-", size=50)],
          [sg.Text("Drone minimum flight height [ft]: "), sg.InputText(key="-height-", size=6)],
          [sg.Button("Submit"), sg.Button("Close")],
          [sg.Text("Check metadata progress: "), sg.ProgressBar(100, orientation='h', size=(30, 10), border_width=2, key='progbar',bar_color=['Red','Green'])],
          [sg.Text("Moving files progress:        "), sg.ProgressBar(100, orientation='h', size=(30, 10), border_width=2, key='progbar2',bar_color=['Red','Green'])]]

window = sg.Window('My Flights Browser', layout, size=(600,240))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit" or event == "Close":
        window.close()
        exit()
    if event == "Submit":
        path = values["-PATH-"]
        if not os.path.isdir(path):
            sg.Print("Please input folder with the images!")
            continue
        outpath = values["-OUTPATH-"] or os.path.join(path, values["-name-"] or "organized")
        os.makedirs(outpath, exist_ok=True)
        try:
            height_th = int(values["-height-"])/3.281
        except ValueError:
            height_th = 350/3.281
        sg.Print("Using height threshold: {} ft".format(height_th*3.281))
        break

# Get a list of all TIFF files in the input folder and its subfolders
files = []
for root, dirs, filenames in os.walk(path):
    for filename in filenames:
        if splitext(filename)[-1].lower() == '.tif':
            files.append(join(root, filename))

sg.Print("{} files identified.".format(len(files)))
sg.Print()

# Sort the files by filename
files.sort()

# Extract the multispectral images with all 5 bands and move them to the output folder
new_files = []
sg.Print("Reading metadata...")
sg.Print()
fcount = 1
inflight = False
data_start_end = ["0", "0"]

# Read metadata to find data start and end
with ExifToolHelper() as et:
    for f in files:
        # Update progress bar
        val = int(100*fcount/len(files))
        window['progbar'].update_bar(val)
        
        # Read GPS altitude tags for all 5 images and check if the altitude is above the threshold
        try:
            metadata = et.get_tags(f, 'EXIF:GPSAltitude')
            _ = et.get_tags(f[0:-5]+"2.tif", 'EXIF:GPSAltitude')
            _ = et.get_tags(f[0:-5]+"3.tif", 'EXIF:GPSAltitude')
            _ = et.get_tags(f[0:-5]+"4.tif", 'EXIF:GPSAltitude')
            _ = et.get_tags(f[0:-5]+"5.tif", 'EXIF:GPSAltitude')
        except:
            sg.Print("Corrupted metadata: "+f)
            continue
        if metadata[0]['EXIF:GPSAltitude'] >= height_th:
            new_files.append(f)
            # If the flight has just started, update the data start time
            if inflight == False:
                inflight = True
                data_start_end[0] = metadata[0]['SourceFile'][-10:-6]
        else:
            # If the flight has just ended, update the data end time
            if inflight == True:
                data_start_end[1] = metadata[0]['SourceFile'][-10:-6]
                inflight = False
        fcount+=1
    
    # Update progress bar to 100%
    window['progbar'].update_bar(100)
    
# Print data start and end times
sg.Print("Metadata read!")
sg.Print()
sg.Print("Data starts at "+data_start_end[0])
sg.Print("Data ends at "+data_start_end[1])
sg.Print()

# Ask user to continue or close
sg.Print("Press Submit if you would like to continue")
sg.Print("Otherwise, Close")
sg.Print()
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit" or event=="Close":
        exit()
    if event == "Submit":
        break

# Create output folder
sg.Print("Creating output folder: "+outpath)
if not os.path.exists(outpath):
    os.makedirs(outpath)
    
# Move files to output folder
sg.Print("Moving files to: "+outpath)
sg.Print()
fcount = 0
for f in new_files:
    fcount+=1

    # Move all 5 files to the new folder
    name = f.split("/")
    move(f, outpath+name[-1])
    move(f[0:-5]+"2.tif", outpath+name[-1][:-5]+"2.tif")
    move(f[0:-5]+"3.tif", outpath+name[-1][:-5]+"3.tif")
    move(f[0:-5]+"4.tif", outpath+name[-1][:-5]+"4.tif")
    move(f[0:-5]+"5.tif", outpath+name[-1][:-5]+"5.tif")
    
    # Update progress bar
    val = int(100*fcount/len(new_files))
    window['progbar2'].update_bar(val)

# Print "DONE!" when moving is complete
sg.Print()
sg.Print

