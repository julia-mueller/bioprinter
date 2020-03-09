# Gel printer

## Motivation
This repo contains all the files needed to create gcode files for the gel printer.

## How to use?
Download all the files in this repo.

To create a printer file, open a bash inside the folder where the following programs are: 
- executor.py
- generator.py
- routinegenerator.py
- constants.py
- also some folders should exist:	
    
    - parameterfiles: a folder with all your parameterfiles
    - gcodefiles: a folder where all your gcodefiles will be saved
    - svgfiles: a folder where all your svgfiles are saved

Type in the shell:  python executor.py parameterfiles/'your parameter file name'.yaml

## Write svg files
To write a svg file a program like Inkscape or ___ can be used. It is for the further compilation necessary that the svg file has a specific header:
```  
    <?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 16.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg  version="1.1" id="Ebene_1" xmlns="&ns_svg;" xmlns:xlink="&ns_xlink;" width="15" height="15"
    	 	viewBox="0 0 15 15" enable-background="new 0 0 15 15" xml:space="preserve">
```
In the following of the svg file the lines should look like this:
```
    <line fill="none" stroke="#000000" stroke-width="0.1" x1="1.155" y1="2.089" x2="1.393" y2="2.089"/>
```

## Write Parameterfiles
The parameterfile must be a yaml file. The name should contain the date and the name of the svg file which should be used. 

--> The format should be: yyyy-mm-dd-'name of svg file'.yaml

It should contain the following paramter:
- inputfile: 'name of svg file'
- colourlist: [["colour 1"]["colour 2"]] (The colours need to be in Hexcode, ne number of colours determines the number of layers which should be printed, the colour determines which parts of the svg should be printed)
- liquid: "type of gel"
- liquidparameters: [flowspeed, nozzle temperatur, bed temperatur]
- volume_gel: [0.0, 0.0, 0.0]
- syringe_radius: radius of syringe in mm
- nozzle_diam: nozzle diameter in mm
- height: [height of the object slide, height of the object slide holder]
- conversion_ratio_syringe: 1.5
- pump_length: 0
- offset: offset between the extruder in mm (e.g. 50.0)
- begin_of_print: 0
- increase_volume_factor: 1.0 (if the volume should be doubled: 2.0, e.g.)
- startdis: 30 (home position before print starts, 30mm in x and y direction from the (0.0,0.0) point)
- red_delta_z: This paramter determines how the height per layer is reduced (0.8, e.g.)
- z_safe_dis: This paramter determines the height added to z during movements (3, e.g.)
- scale_z: True or False, This paramter determines if the nozzle-sample distance should be changed
- max_normal_layer: This paramter determines after how many layers the height should be reduced (8, e.g.)
- dim_z_later: This parameter determines how the height sample-nozzle should be changed after a given number of layers (0.8, e.g.)
- scale_z_squared: True or False,  scale the height quadratically
- red_z_square: factor that decreases the quadratic part of the reduce-z-function (0.01, e.g.)
- corner_adjustment: True or False, This parameter determines if the corner adjustment should happen or not
- slippage: value for the slippage of the printer (0.5, e.g.)

### Abbreviations (used in the name of the gcode file):
	squ-option = quadratic function for heightreducement 
	corn-option = corner adjustment, to prevent slippage of the printer after the first and third corner
	step-option = stepfunction for heightreducement (=1 after a set number of layers)
    --> option = on/off  
    
## Team
- Julia Müller
- Anna Jäkel 