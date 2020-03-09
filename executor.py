# -*- coding: utf-8 -*-
# 05.03.2019 Julia Müller
# revised by Anna Jäkel

"""
The Program can be started by typing in the shell:
    "python executor.py parameter.yaml".
I made a small change to test!
"""

import numpy as np
import generator as g
import yaml
import sys
import constants


if __name__ == "__main__":

    """
    This function produces the outputfile that can be read by the gel-printer.

    In addition the volume is calculated which is needed for the print.
    """

    if len(sys.argv) < 2:
        print(constants.error_message)
    else:
        filehandle = open(sys.argv[1], "r")
        params = yaml.safe_load(filehandle)
        params['parameterfile'] = sys.argv[1]
        outputfile = g.generate_gcode_file_get_volume(params)
        volume = list(np.around(np.array(params['volume_gel']),2))
        
        print(constants.finish_message.format(outputfile, volume))
