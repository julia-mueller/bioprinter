# -*- coding: utf-8 -*-
# 05.03.2019 Julia Müller
# revised by Anna Jäkel

import os
import math
import numpy as np
import routinegenerator as rg
from numpy import inf
from datetime import datetime
from pathlib import Path
import constants

def get_datetime():
    i = datetime.now()
    date = i.strftime('%Y_%m_%d')
    time = i.strftime('%H:%M:%S')
    return date, time

def generate_gcode_file_get_volume(params):
    """
    This function returns the outputfile and the needed volume.

    It calculates some needed values with the parameters from the .yaml file.
    It generates the list for the lines and circles.
    It calls the function which puts the routines together for the outputfile.
    It returns then the outputfile and the volume.

    Args:
        params: the parameters are explained in the .yaml file

    Returns:
        outputfile (.gcode file): outputfile
        volume (double): volume that is needed
    """

    params['nozzle_radius'] = params['nozzle_diam'] / 2
    params['extrusion_ratio'] = (params['nozzle_radius']**2)/(params['syringe_radius']**2)
    params['filename'] = get_filename(params)
    params['size'] = get_size(params['inputfile'])
    params['list_of_lines'], params['list_of_circles'] = generate_lists(params)

    outputfile = put_routines_together(params)

    return outputfile

def get_filename(params):
    """
    This function produces the outputfilename for the gcode file.

    Args:
        inputfilename (string): name of the inputfile (svg) with the pattern
    Returns:
        filename (string): outputfilename (file for the printer)
    """

    filename = os.path.splitext(params['inputfile'])[0]

    if params['nozzle_diam'] == 0.11:
        nozzle_colour = 'y'
    elif params['nozzle_diam'] == 0.15:
        nozzle_colour = 'l'
    elif params['nozzle_diam'] == 0.20:
        nozzle_colour = 'w'
    elif params['nozzle_diam'] == 0.25:
        nozzle_colour = 'r'
    elif params['nozzle_diam'] == 0.33:
        nozzle_colour = 'o'
    elif params['nozzle_diam'] == 0.41:
        nozzle_colour = 'b'
    else:
        print('nozzle diameter does not exist!')

    scale_z_short = 'on' if params['scale_z'] else 'off'
    short_squared = 'on' if params['scale_z_squared'] else 'off'
    short_corner = 'on' if params['corner_adjustment'] else 'off'
    volume_factor = params['increase_volume_factor']

    # filename contains the values for red_delta_z, max_normal_layer, dim_z_later
    # and also the nozzle colour, the volume factor, the filename of the svg
    # and it also shows if the stepfunction, the squared correction and the corner correction are on or off
    filename_new = nozzle_colour + '_' + str(volume_factor) + 'V_'\
        + filename + '_step-' + scale_z_short + '_squ-'\
        + short_squared + '_cor-' + short_corner
    #+str(params['red_delta_z']) + '_'\
    #+str(params['max_normal_layer']) + '_'\
    #+str(params['dim_z_later']) + ';'\


    return filename_new

def get_size(inputfile):
    """
    This function opens the inputfile and reads the size of of the svg file.

    Args:
        inputfile (string): inputfilename (svg file)
    Returns:
        size (list): size of the whole file size[0]=x_achse und size[1]=y_achse
    """

    size=[0.0, 0.0] # Size of the object slice [slice width x, slice length y]
    svgfile = open("svgfiles/" + inputfile,"r")

    # get number of lines in svg file -> number of elements to print
    svg_lines = sum(1 for line in svgfile)

    # jump to beginning of the file
    svgfile.seek(0)

    for l in range(0, svg_lines):
        svg = svgfile.readline()
        svg_parts = svg.split(' ')

        if svg_parts[0] == "<svg":

            size1 = svg_parts[6].split('\"')
            size[0] = float(size1[1])

            size2 = svg_parts[7].split('\"')
            size[1] = float(size2[1])

        elif l == svg_lines and size == [0.0, 0.0]:
            print("No size given in svg file.")
            break

        else:
            pass

    return size

def put_routines_together(params):
    """
    This function puts the routines together.

    It produces the outputfile by combining the start routine, the middle
    routine (main gcode) and the end routine. It also returns the volume that
    is needed.

    Args:
        params: the parameters are explained in the .yaml file

    Returns:
        outputfile (string): outputfile
        volume (double): volume
    """

    date, _ = get_datetime()
    outputfile = params['filename'] + ".gcode"
    folder = 'gcodefiles/' + date
    if os.path.isdir(folder):
        print('--> Folder of todays date exists already.')
    else:
        os.mkdir(folder)

    my_file = Path(folder+"/"+outputfile)
    if my_file.is_file():
        print("--> File exists already, will be overwritten!")
    file = open(folder + '/' + outputfile,"w")

    start_code = generate_start_routine(params)
    file.write(start_code)

    gcode, layers = rg.return_middle_routine_get_layers(params)
    file.write(gcode)

    end_code = generate_end_routine(params, layers)
    file.write(end_code)

    return outputfile

def generate_start_routine(params):
    """
    This function returns the starting routine script for the gcode file.

    Args:
        params: the parameters are explained in the .yaml file
    Returns:
        start_code (string): start-code that printer needs in the beginning
    """

    _, time = get_datetime()

    start_code = constants.info_message.format(str(time),
                                               str(params['liquid']),
                                               str(params['nozzle_diam']),
                                               str(params['nozzle_diam']),
                                               str(params['parameterfile']))\
        + constants.start_routine.format(str(params['liquidparameters'][1]),
                                         str(params['liquidparameters'][2]),
                                         str(params['height'][1]),
                                         str(params['startdis']+10),
                                         str(params['startdis']+10),
                                         str(params['homeheight']),
                                         str(params['homeheight']+5))

    return start_code

def generate_end_routine(params, layers):
    """
    This function returns the end_routine for the gcode.

    Args:
        params: the parameters are explained in the .yaml file
        layers (int): number of layer
        volume (list): volume that is needed

    Returns:
        end_code (string): end-code that printer needs at the end of the printer-file
    """

    end_code = constants.end_routine.format(str(params['height'][0] + layers * 1.6 * params['nozzle_radius'] + 3),
                                            str(params['volume_gel'][1]),
                                            str(params['volume_gel'][2]))

    return end_code

def generate_lists(params):
    """
    This function generates the lists for the lines and cyrcles.

    Agrs:
        params: the parameters are explained in the .yaml file

    Returns:
        list_of_line (list): list of all the lines that printer should print
        list_of_circles (list): list of all circles that printer should print
    """

    svgfile = open("svgfiles/" + params['inputfile'],"r")

    # get number of lines in svg file -> number of elements to print
    svg_lines = sum(1 for line in svgfile)

    # create the lists:
    list_of_lines = np.zeros((1, 8))
    list_of_circles = np.zeros((1, 5))

    # start at the beginning to read file:
    svgfile.seek(0)

    # filter svg file for lines and write in list_of_lines
    n = 0
    m = 0
    for l in range(0, svg_lines):
        svg = svgfile.readline()
        ################################################
        # Example:
        # svg = [<line fill="none" stroke="#000000" x1="0" y1="1" x2="1" y2="2"/>]
        # svg_parts is list of elements in svg
        # svg = ['<line', 'fill="none"','stroke="#000000"', 'x1="0"', 'y1="1"', 'x2="1"', 'y2="2"/']
        # get start and end points and write in list with colour and extrusion
        #################################################
        # split svg line into parts seperated by the space character:
        svg_parts = svg.split(' ')

        # translation if path is a line
        if svg_parts[0] == "<line":
            # split by " to get numbers
            x1 = svg_parts[4].split('\"')
            x1 = float(x1[1])
            y1 = svg_parts[5].split('\"')
            y1 = float(y1[1])
            x2 = svg_parts[6].split('\"')
            x2 = float(x2[1])
            y2 = svg_parts[7].split('\"')
            y2 = float(y2[1])

            color = svg_parts[2].split('#')
            color = str(color[1])
            color = color.split('\"')
            color = color[0]
            color = int(color, 16)

            # calculate extrude = printed length
            delta_x = abs(x2 - x1)
            delta_y = abs(y2 - y1)
            extrude = math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2))
            extrude = extrude * params['extrusion_ratio']

            # Was tut das hier?:
            if x2 != x1:
                slope = (y2 - y1) / (x2 - x1)
                intercept = y1 - (slope * x1)
            else:
                slope = inf
                intercept = 0
            if n == 0:
                list_of_lines = np.array([x1, y1, x2, y2, color, extrude, slope, intercept])
            else:
                list_of_lines = np.vstack([list_of_lines,[x1, y1, x2, y2, color, extrude, slope, intercept]])
            n = n + 1

        # translation if path is a circle
        # <circle fill="#FFFFFF" stroke="#000000" cx="4.532" cy="25.097" r="4.032"/>
        # get centre point and radius as well as colour and write with extrusion in list of circles
        elif svg_parts[0] == "<circle":
            cx = svg_parts[4].split('\"')
            cx = float(cx[1])
            cx = cx + 0
            cy = svg_parts[5].split('\"')
            cy = float(cy[1])
            cy = cy + 0
            r = svg_parts[6].split('\"')
            r = float(r[1])

            color = svg_parts[2].split('#')
            color = str(color[1])
            color = color.split('\"')
            #color = int(color[1])
            color = int(color[0])

            extrude = 2 * math.pi * r
            extrude = extrude * params['extrusion_ratio']

            if m == 0:
                list_of_circles = np.array( [cx, cy, r, color, extrude])
            else:
                list_of_circles = np.vstack([list_of_circles, [cx, cy, r, color, extrude]])
            m = m + 1

        else:
            pass

    return list_of_lines, list_of_circles
