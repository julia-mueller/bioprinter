# Gel printer

## Motivation
This repository contains the code used for all 3D printing experiments in the paper "Programming diffusion and localization of DNA signals in 3D-printed DNA functionalized
hydrogels" (INSERT LINK TO SMALL).

Machine readable GCODE files for a 3D printer can be created from .svg files with the python code of this project. 
In contrast to other slicers this code project focusses on the design of print files for a 3D printer loaded with liquid filament (e.g. hydrogel samples).

The idea is to use .svg files as input, to gain voxel based extrusion where each voxel can be placed to defined locations. In the svg files linebased designes work best and are highly scaleable as well as easy to design in a graphic tool like illustrator for example.
For further information or application examples you should have a look at the paper mentioned above.

## How to use?
For detailed instructions with screenshots, see the two introduction pdf files "Gel_Printer_Introduction.pdf" and "GitLab_Introduction.pdf". A brief introduction is given below.

Download all the files in this repository or clone them to your local git folder.

To create a printable file, open a shell inside the folder where the following files and subfolders are. Optional, open a command line interface and change to you working directory that contains the following files: 
- executor.py
- generator.py
- routinegenerator.py
- constants.py
- further the following subolders should exist (if not, create empty folders):	
    
    - parameterfiles: a folder with all your input .yaml parameterfiles
    - svgfiles: a folder that contains all input .svg files
    - gcodefiles: a folder where all your output gcodefiles will be saved

Type in the shell:  python executor.py parameterfiles/'your parameter file name'.yaml

## Write svg files
To write a svg file use any vector graphic program, e.g. Inkscape or Illustrator. It is important that the header does not have the word <line it it (should not be the case by default).
In the following the lines the svg file should look like this:
```
    <line fill="none" stroke="#000000" stroke-width="0.1" x1="1.155" y1="2.089" x2="1.393" y2="2.089"/>
```
As for now it is important that exactly those arguments follow the argument <line.

## Write Parameterfiles
The parameterfile must be a .yaml file which can be written with a simple texteditor. We recommend that the name should contain the date and the name of the svg file which should be used. 

It should contain all the following paramters:

Update these material parameters for each print:
- inputfile: 'name_of_svg_file'
- colourlist: [["color_for_extruder1_layer1", "color_for_extruder1_layer1", ...]["color_for_extruder2_layer1", "color_for_extruder2_layer2", ...]] (The colours need to be in Hexcode, the number of colours determines the number of layers which should be printed, the colour determines which parts of the svg should be printed)
- nozzle_temp: 45 (nozzle temperature in °C, for our bioink this was 45°C)
- bed_temp: 0 (bed temperature in °C, we used a bed at room temperature, so we set this to 0)
- height: [height of the object slide, height of the object slide holder]
- red_delta_z: This paramter determines how the height per layer is reduced (0.8, e.g.)
- increase_volume_factor: 1.0 (if the volume should be doubled: 2.0, e.g.)

Update these material parameters to optimize your print results:
- scale_z: True or False, This paramter determines if the nozzle-sample distance should be changed
- max_normal_layer: This paramter determines after how many layers the height should be reduced (8, e.g.)
- dim_z_later: This parameter determines how the height sample-nozzle should be changed after a given number of layers (0.8, e.g.)
- scale_z_squared: True or False,  scale the height quadratically
- red_z_square: factor that decreases the quadratic part of the reduce-z-function (0.01, e.g.)
- corner_adjustment: True or False, This parameter determines if the corner adjustment should happen or not

Update these parameters for your own printer at first usage:
- syringe_radius: radius of syringe in mm
- nozzle_diam: nozzle diameter in mm
- flowspeed: 500 (worked best for our bioink. The flowspeed is translated to the GCODE parameter F = feedrate and sets the print speed)
- conversion_ratio_syringe: 1.5 (Area of the nozzle divided by the area of the syringe)
- offset: offset between the extruder in mm (e.g. 50.0)
- homeheight: in mm (this is the height of the mechanic or electric switch that sets z = 0)
- slippage: value for the slippage of the printer (0.5, e.g.)
- startdis: 30 (home position before print starts, 30mm in x and y direction from the (0.0,0.0) point)

The parameterfile initializes the following global variables, these do not need to be changed manually:
- volume_gel: [0.0, 0.0, 0.0]
- begin_of_print: 0
- z_safe_dis: This paramter determines the height added to z during movements (3, e.g.)


### Guidelinetable
Below are the optimal values given for specific gels:
- Bioink: Flowspeed = 500, Nozzle Temperature = 45, Bed Temperature = 0 (0 is given here as standart, because we disabled this function as our printer can't cool and doesn't use this parameter)
    
## Infos to temperature settings
- printbed temperature: if you use the onboard printbed heating you can set this paramter in the parameterfile
- nozzle temperature: if you use the onboard nozzle heating you can set this parameter in the parameterfile

In our application we used an external temperature controller for the nozzle heating to avoid high currents on the printer board. 
As we don't use the onboard temperature control for nozzle/bed, we deactivate the corresponding machine codes in the generated GCODE per default.

If you want to use the onboard temperature control you have to replace the second line of the start_routine parameter in the file 'constants.py'.
The lines are:
```
start_routine = "M107	; turn fan off" + "\n"\
        + "M302	;allow cold extrudes" + "\n"\
        + "G21 ;metric values\n"\
```
but it should look like this if you prefere heating, but not waiting with the print till the set temeperature is reached: 
```
start_routine = "M107	; turn fan off" + "\n"\
        + "M302	;allow cold extrudes" + "\n"\
        + "M140 S{0} ;heats build plate to to the bed_temp parameter, no waiting + "\n"\
        + "M104 S{1} ;heats nozzle to the nozzle_temp parameter, no waiting
        + "G21 ;metric values\n"\
```
and it ahould look like that if you prefere heating, and want to wait with the print till the temeperature is reached:
```
start_routine = "M107	; turn fan off" + "\n"\
        + "M302	;allow cold extrudes" + "\n"\
        + "M190 S{0} ;heats build plate to the bed_temp parameter incl waiting to reach this temperature" + "\n"\
        + "M109 S{1} ;heats nozzle to the nozzle_temp parameter incl waiting to reach this temperature" + "\n"\
        + "G21 ;metric values\n"\
```
    
## FAQ's
- For questions concerning the code check out the Troubleshooting file. 
- If you have further questions on the usage of a hydrogel printer, you could hava a look at the paper mentioned in the motivation section above.
- In case you find any bugs, we would highly appreciate, if you contact us via an issue report 
- If there is a feature that you are missing just open an issue for additional features
  
## Team
- Julia Müller
- Anna Jäkel 