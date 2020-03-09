# -*- coding: utf-8 -*-
# 05.03.2019 Julia Müller
# revised by Anna Jäkel

import math
import numpy as np

def return_middle_routine_get_layers(params):
    """
    This function returns the gcode, the volume and the number of layers.

    It calls the function "build_gcode_volume_layers" which generates the
    gcode, calculates the volume and the layers. After this the volume is
    adapted by the conversion rate.

    Agrs:
        params: the parameters are explained in the .yaml file

    Returns:
        gcode (str): the list of volumes and the number of layers
        volume (list): volume that is needed
        layers (int): number of layers
    """

    conversion_ratio_syringe_adapted = (params['conversion_ratio_syringe'] *
                                        params['increase_volume_factor'])
    begin_of_print = 1 # determines if the smallstart needs to be added to the gcode

    gcode, layers = write_middle_routine_get_layers(params, begin_of_print,
                                                    conversion_ratio_syringe_adapted)

    params['volume_gel'] = ([(x*math.pi*(params['syringe_radius'])**2)/
          params['conversion_ratio_syringe'] for x in params['volume_gel']])

    return gcode, layers

def write_middle_routine_get_layers(params, begin_of_print,
                                    conversion_ratio_syringe_adapted):
    """
    This function returns the gcode, the volume and the layer.

    The gcode is generated for different situations and combined.

    Args:
        params: the parameters are explained in the .yaml file
        begin_of_print (int): determines if the smallstart needs to be added to the gcode
        conversion_ratio_syringe_adapted (double): conversion ratio for the volume

    Returns:
        gcode (str): this is the main routine
        layers (int): number of layers
    """

    gcode = "\n"

    extrude_old = [0.0, 0.0, 0.0] # Memory variable for the volume that was extruded in the last step
    layers = len(params['colourlist'][0]) # number of layers
    actual_layer = 0

    for layer in range(0, layers):
        
        #smallstart for modified gel
        if params['fillstatus'] or params['begin_of_print']:
            gcode_append, volume_add, extrude_old = smallstart(params, extruderno,
                                                           extrude_old)
            gcode = gcode + str(gcode_append)
            params['volume_gel'][extruderno] = (params['volume_gel'][extruderno] +
              volume_add)
            params['begin_of_print'] = 0
        else:
            pass
        
        actual_layer = actual_layer + 1
        
        gcode_append = "    M117 layer " + str(layer+1) + "\n\n" + "    ;change to first extruder at the beginning of each layer\n    T1\n\n"
        gcode = gcode + str(gcode_append)
        
        z_height = calculate_z(params, layer)

        gcode, begin_of_print = translator_add(params, gcode, actual_layer, 
                                                       extrude_old, begin_of_print, 
                                                       conversion_ratio_syringe_adapted, 
                                                       z_height)
        
        gcode = gcode + cleaning_routine(params)

    return gcode, layers

def calculate_z(params, layer):
    """
    This function calculates the height that the nozzle should move upwards.

    Args:
        params: the parameters are explained in the .yaml file
        layer (int): number of layer
    Returns:
        cal_z (float): height between bottom of printer and position where the
            nozzle should drop gel
    """

    layer = float(layer)

    if params['scale_z']:
        cal_z = np.piecewise(layer, [layer <= params['max_normal_layer'],
                                     layer > params['max_normal_layer']],
                [lambda layer: params['height'][0] + params['red_delta_z'] *
                 params['nozzle_radius'] * layer,
                 lambda layer: params['height'][0] + params['red_delta_z'] *
                 params['nozzle_radius'] * layer + params['dim_z_later'] *
                 params['red_delta_z'] * params['nozzle_radius'] *
                 (layer - params['max_normal_layer'])])
    elif params['scale_z_squared']:
        cal_z = (params['height'][0] + params['red_delta_z'] *
                 params['nozzle_radius'] * layer - params['red_z_square'] *
                 params['nozzle_radius'] * layer**2)
    else:
        cal_z = (params['height'][0] + params['red_delta_z'] *
                 params['nozzle_radius'] * layer)

    return cal_z

def smallstart(params, extruderno, extrude_old):
    """
    This function returns the gcode for the smallstart routine.

    It returns as well the volume amount that should be added to the extruded
    volume and it returns the list of the last extruded volume for each extruder

    Args:
        params: the parameters are explained in the .yaml file
        extruderno (int): number of the extrudor
        extrude_old (list): list of the last extruded volume for each extruder

    Returns:
        gcode_append (str): gcode for the smallstart routine
        volume_add (double): volume that shoulb be added to the extruded volume
        extrude_old (list): list of the last extruded volume for each extruder
    """

    gcode_append = constants.smallstart.format(str(params['height'][1]), 
                                               str(6 * params['liquidparameters'][0]), 
                                               str(params['startdis']+5), 
                                               str(params['startdis']+5), 
                                               str(1 * params['liquidparameters'][0]))

    volume_add = 0.0
    extrude_old[extruderno] = 0.0

    return gcode_append, volume_add, extrude_old

def breaking(params):
    """
    This function returns the breaking routine.

    Args:
        params: the parameters are explained in the .yaml file

    Returns:
        gcode_append (str): gcode for the breaking routine
    """

    g1 = "    ;Slow movement to change nozzle:\n"\
    "    G1 Z " + str(params['height'][1]) + "\n"

    if params['fillstatus']:
        g2 = "G1 F" + str(6 * params['liquidparameters'][0]) + " X10 Y10 \n"
        gcode_append = g1 + g2 + "\n"
    else:
        gcode_append = g1 + "\n"

    return gcode_append

def cleaning_routine(params):
    """
    This function returns the cleaning routine.
    Args:
        params: the parameters are explained in the .yaml file

    Returns:
        gcode_cleaning (str): gcode for the cleaning routine
    """

    gcode_cleaning = "    ;cleaning routine follows:\n"\
        + "    G1 F5000 X" + str(params['startdis']+5) + " Y70 ;move to cleaning position\n"\
        + "    G1 Z1.1\n"\
        + "    G1 F1000 Y100\n"\
        + "    G1 Z10.0\n"\
        + "    G1 F5000 X" + str(params['startdis']+10) + " Y" + str(params['startdis']+10)\
        + " ;move to initial position\n\n"

    return gcode_cleaning

def change_of_extruder(params, extruder):
    """
    This function returns the gcode to change the extruder.
    Args:
        params: the parameters are explained in the .yaml file
        extruder: number of next extruder, that should be used
    Returns:
    gcode_change_extruder (str): gcode for the change of the extruder 
    """
    
    gcode_change_extruder = "    ;change of extruder\n    T" + str(extruder+1) + "\n\n"
    offset = params['offset']
    
    return gcode_change_extruder, offset

def translator_add(params, gcode, actual_layer, extrude_old,
                   begin_of_print, conversion_ratio_syringe_adapted, z_height):
    """
    This function puts the routines for the smallstart, the main routine and
        the breaking together.

    Main routine for the gel that should build the object.

    Args:
        params: the parameters are explained in the .yaml file
        gcode (str): gcode part before smallstart
        actual_layer (int): number of layer
        color (int): color of the actual layer
        volume (list): list of volumes that are needed for the print
        extrude_old (list): list of the last extruded volume for each extruder
        begin_of_print (int): determines if the smallstart needs to be added to the gcode
        conversion_ratio_syringe_adapted (double): conversion ratio for the volume
        z_height (float): height between bottom of printer and position where
            the nozzle should drop gel
        
    Returns:
        gcode (str): gcode routine for the actual gel that should be printed
        volume (list): list of volumes that are needed for the print
        begin_of_print (int): determines if the smallstart needs to be added to the gcode
    """

    extruderno = 1
    
    for extruder in range(0, len(params['colourlist'])):
        
        offset = 0
        if extruder>0:
            #hier tausch des extruders einbauen
            gcode_append, offset = change_of_extruder(params, extruder)
            gcode = gcode + gcode_append
        else:
            pass
        
        color = int(params['colourlist'][extruder][actual_layer-1], 16)
    
        #gcode for modified gel = lines
        gcode_append, volume_add, extrude_old = translator(params, actual_layer,
                                                       color, extrude_old,
                                                       extruderno,
                                                       conversion_ratio_syringe_adapted,
                                                       z_height, extruder, offset)
        gcode = gcode + str(gcode_append)
        params['volume_gel'][extruderno] = (params['volume_gel'][extruderno] +
          volume_add[extruderno])
        
        #break
        gcode_append = breaking(params)
        gcode = gcode + str(gcode_append)

    return gcode, begin_of_print

def translator(params, actual_layer, color, extrude_old, extruderno,
               conversion_ratio_syringe_adapted, z_height, extruder, offset):
    """
    This function returns the main routine for the actual gelprint.

    Args:
        params: the parameters are explained in the .yaml file
        actual_layer (int): number of actual layer
        color (int): color of actual layer
        volume (list): list of volumes that are needed for the print
        extrude_old (list): list of the last extruded volume for each extruder
        extruderno (int): number of extruder
        conversion_ratio_syringe_adapted (double): conversion ratio for the volume
        z_height (float): height between bottom of printer and position where
            the nozzle should drop gel
        extruder: extruder which is used at the moment 0=first extruder,...
        offset: offset that needs to be substracted from x values

    Returns:
        gcode (str): gcode for the object that should be printed
        volume_intern (list): list of volumes that are needed for the print
        extrude_old (list): list of the last extruded volume for each extruder 
    """

    volume_intern = [0,0,0,0]

    gcode = "    ;GCODE of lines\n    ;M117 Print lines...\n\n"

    delta_x_values = [0] * len(params['list_of_lines'])
    delta_y_values = [0] * len(params['list_of_lines'])
    slippage = 0

    # go through lines and check for same colour
    for l in range(0, len(params['list_of_lines'])): 
        line = l
        #list_of_lines = [x1, y1, x2, y2, color, extrude]
        if color == params['list_of_lines'][line, 4]:
            x1 = params['list_of_lines'][line, 0]
            y1 = params['list_of_lines'][line, 1]
            x2 = params['list_of_lines'][line, 2]
            y2 = params['list_of_lines'][line, 3]
            delta_x_values[line] = x2 - x1
            delta_y_values[line] = y2 - y1

            # if corner adjustment is True: adjust positions by slippage
            if params['corner_adjustment']:
                if delta_y_values[line]>0:
                    slippage = params['slippage'] # calculate slip from printer, 0.5 chosen randomly
                elif delta_y_values[line]<0:
                    slippage = -params['slippage']
                else:
                    pass
            else:
                slippage = 0

            #Länge die Spritze runter gedrückt wird
            extrude = params['list_of_lines'][line, 5] * conversion_ratio_syringe_adapted
            volume_intern[extruderno] = volume_intern[extruderno] + extrude

            gcode_append = "        G1 F" + str(6 * params['liquidparameters'][0])\
                + " X" + str(x1 + params['startdis'] - offset)\
                + " Y" + str(y1 + slippage + params['startdis']) + " E0\n"\
                + "        G1 Z" + str(z_height)\
                + " E" + str(extrude_old[extruderno] * 0.1) + "\n"\
                + "        G1 F" + str(params['liquidparameters'][0])\
                + " X" + str(x2 + params['startdis'] - offset)\
                + " Y" + str(y2 + slippage + params['startdis'])\
                + " E" + str(extrude) + "\n"\
                + "        G1 Z" + str(z_height + params['z_safe_dis'])\
                + " E" + str(-(extrude * 0.1)) + "\n\n"

            gcode = gcode + str(gcode_append)
            extrude_old[extruderno] = extrude

        else:
            pass

    for l in range(1, len(params['list_of_circles'])):
        #list_of_circles = [cx, cy, r, color, extrude]
        if color == params['list_of_circles'][l, 3]:
            cx = params['list_of_circles'][l, 0]
            cy = params['list_of_circles'][l, 1]
            r = params['list_of_circles'][l, 2]
            extrude = (params['list_of_circles'][l, 4] *
                       conversion_ratio_syringe_adapted)
            volume_intern[extruderno] = volume_intern[extruderno] + extrude

            gcode_append = "G1 F" + str(6 * params['liquidparameters'][0])\
                + " X" + str(cx + params['startdis'])\
                + " Y" + str(cy + params['startdis'] - r) + " E0\n"\
                + "G1 Z" + str(z_height) + " E" + str(extrude_old[extruderno] *
                              0.1) + "\n"\
                + "G2 F" + str(params['liquidparameters'][0])\
                + " J" + str(r) + " E" + str(extrude) + "\n"\
                + "G1 Z" + str(z_height +  params['z_safe_dis'])\
                + " E" + str(-(extrude * 0.1)) + "\n"

            gcode = gcode + str(gcode_append)
            extrude_old[extruderno] = extrude

        else:
            pass

    gcode_append = "    G1 Z" + str(z_height +  params['z_safe_dis']) + "\n\n" #??? Julia do we need this?
    gcode = gcode + str(gcode_append)

    return gcode, volume_intern, extrude_old