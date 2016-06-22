'''
Created on Jan 7, 2013

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

from common.enumerations import *

def overrides (interface_class):
    def overrider(method):
        assert (method.__name__ in dir (interface_class))
        return method
    return overrider

def roundFour(value):
    return round(value, 4)

def myRound( val):
    return round(val,DEFAULTS.DEFAULT_PRECISION)

def truncCompare( val):
    power = 10
    i = 0
    while i <  DEFAULTS.DEFAULT_PRECISION:
        power = power * 10
        i = i + 1
    res = val * power
    return int(res)

class Event(object):
    
    def __init__(self):
        self.__handlers=[]
    
    def __iadd__(self, handler):
        self.__handlers.append(object,handler)

    def __isub__(self, handler):
        self.__handlers.remove(object,handler)
    
    def fire(self, *args, **keyargs):
        for h in self.__handlers:
            h(*args,**keyargs)

    def clearHandlers(self, inObject):
        for h in self.__handlers:
            if h.im_self== inObject:
                self -= h