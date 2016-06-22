'''
Created on Dec 24, 2012

SAHISim - Standardized Architecture for Hybrid Interoperability of Simulations

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author: Muhammad Usman Awais, email:usman.awais@hotmail.com
'''

class SynchState():
    NotInit = 0
    RegisterRequested=1
    Registered=2
    Announced=4
    Achieved=8
    Synched=16
    
class UPDT_INDEX():
    TIME = 0
    NAME = 1
    VALUE = 2

class TimeState():
    NotInit = 0
    Regulated=1
    Constrained=2
    
class DEFAULTS():
    #DEFAULT_Q_STEP = 0.01# Not used
    DEFAULT_INT_STEP = 0.1
    DEFAULT_PRECISION = 4
    DEFAULT_QUANTA = 10
    DEFAULT_WIN_SZ = 100        
    DEFAULT_SPLINE_ORDER = 3    
    RTI_VERSION = 1516
    SIM_END = 100
    SKIP_EVENT_ITER = 1
    DRAW_RESULTS = 1
    MAX_EVENT_ITER = 5
    DUMP_RESULTS = 1
    SYNCH_LABEL = "SynchFeds"
    MIN_DER_VAL = 0.1
    RTI_SERVER = "172.16.128.101"
    RTI_SRV_PORT=33444
    EPSILON= 1e-9
    INIT_STEPS = 10
    BDF_METHOD = 1
    BDF_KIN = 0
    DEBUG_LEVEL = 1
    ALGO_TYPE = ""
    MIN_INT_STEP = 0.001
    QT_INCR = 0.5
    DIFF_METHOD="Difference"
    ERR_TOLERANCE=1e-3
    DIVERGE_TOLERANCE=10.0
    EVENT_DETECTION = 0    
    TOLERANCE = ERR_TOLERANCE
    MAX_ITER = 1000
    
def setDefaults(path):
    f = open(path)
    l = f.readline()
    d = eval(l)
    if len(d) == 0 :
        return

    for name , value  in d.items():
        if name == "DEFAULT_INT_STEP":
            DEFAULTS.DEFAULT_INT_STEP = value
        if name == "DEFAULT_Q_STEP":
            DEFAULTS.DEFAULT_Q_STEP = value
        elif name == "DEFAULT_PRECISION":
            DEFAULTS.DEFAULT_PRECISION = value
        elif name == "DEFAULT_QUANTA":
            DEFAULTS.DEFAULT_QUANTA = value
        elif name == "DEFAULT_WIN_SZ":
            DEFAULTS.DEFAULT_WIN_SZ = value
        elif name == "DEFAULT_SPLINE_ORDER":
            DEFAULTS.DEFAULT_SPLINE_ORDER = value
        elif name == "RTI_VERSION":
            DEFAULTS.RTI_VERSION = value
        elif name == "SIM_END":
            DEFAULTS.SIM_END = value
        elif name == "INIT_STEPS":
            DEFAULTS.INIT_STEPS = value
        elif name == "SKIP_EVENT_ITER":
            DEFAULTS.SKIP_EVENT_ITER = value
        elif name == "DRAW_RESULTS":
            DEFAULTS.DRAW_RESULTS = value
        elif name == "MAX_EVENT_ITER":
            DEFAULTS.MAX_EVENT_ITER = value
        elif name == "DUMP_RESULTS":
            DEFAULTS.DUMP_RESULTS = value
        elif name == "SYNCH_LABEL":
            DEFAULTS.SYNCH_LABEL = value
        elif name == "MIN_DER_VAL":
            DEFAULTS.MIN_DER_VAL = value
        elif name == "RTI_SERVER":
            DEFAULTS.RTI_SERVER = value
        elif name == "RTI_SRV_PORT":
            DEFAULTS.RTI_SRV_PORT = value
        elif name == "EPSILON":
            DEFAULTS.EPSILON = value
        elif name == "BDF_METHOD":
            DEFAULTS.BDF_METHOD = value
        elif name == "BDF_KIN":
            DEFAULTS.BDF_KIN = value
        elif name == "ALGO_TYPE":
            DEFAULTS.ALGO_TYPE = value
        elif name == "ERR_TOLERANCE":
            DEFAULTS.ERR_TOLERANCE = value
            DEFAULTS.TOLERANCE = DEFAULTS.ERR_TOLERANCE
        elif name == "DIVERGE_TOLERANCE":
            DEFAULTS.DIVERGE_TOLERANCE = value
        elif name == "MIN_INT_STEP":
            DEFAULTS.MIN_INT_STEP = value
        elif name == "QT_INCR":
            DEFAULTS.QT_INCR = value
        elif name == "DIFF_METHOD":
            DEFAULTS.DIFF_METHOD = value
        elif name == "EVENT_DETECTION":
            DEFAULTS.EVENT_DETECTION = value
        elif name == "DEBUG_LEVEL":
            DEFAULTS.DEBUG_LEVEL = value
        elif name == "MAX_ITER":
            DEFAULTS.MAX_ITER = value

    f.close()    