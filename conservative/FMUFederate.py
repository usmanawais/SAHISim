'''
Created on Dec 10, 2012

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

#############################################################

import struct
import sys

import os as O

import pylab as P

import numpy as N


import time as T
from pyfmi import load_fmu

from common.enumerations import *
from conservative.BaseFMUFederate import *

import os
#import fmippim


#####################################################################################
## This class encapsulates all the common functionalities needed for an FMU-Federate to work
## Purpose of this class is to hide away all the things which need not be changed in future    
class FMUFederate(BaseFMUFederate):
    def __init__(self, federateName, rtiaref, maxTime = None ):
        super(FMUFederate, self).__init__(federateName,rtiaref)
        self.fmu_2=None
        self.fmuName = ""
        self.fmuPath = ""
        self.federateName = federateName
        self.pendingUpdates = []
        self.event_ind = None
        self.maxTime = maxTime
        self.TsoMsgReceived = False
#######################################################################################################################
## Every class must implement this function  
    def publish(self, className ,attribNames):
        raise("Publish method is not implemented")
    
#######################################################################################################################
## A common function, in my opinion it could be only right way of doing the subscription to RTI
    def subscribe(self, className ,attribNames):        
        if className is None or attribNames is None:
            return
        if len(attribNames) == 0:
            return
        if type(attribNames) is not dict:
            raise Exception ("attribNames must be a dictionary")
        self.ipClassHandle = self.rtiaReference.getObjectClassHandle(className)
        handleSet = []
        self.subscriptions = attribNames
        for k,v in attribNames.items(): 
            if DEFAULTS.RTI_VERSION == 13:
                self.ipHandles[k] = self.rtiaReference.getAttributeHandle(k,self.ipClassHandle)
            else:
                self.ipHandles[k] = self.rtiaReference.getAttributeHandle(self.ipClassHandle,k)
            
            handleSet.append(self.ipHandles[k])
        
        self.rtiaReference.subscribeObjectClassAttributes(self.ipClassHandle,handleSet)
#######################################################################################################################
## A common function which queue the updates sent for this federate into a list. It only works for timed updates
    #def reflectAttributeValues(self, object, attributes , logicalTime, tag, retractionHandle = None):
    def reflectAttributeValues(self, object, attributes, tag, order, transport,logicalTime=None, receiveOrder=None,regionHandleSet=None, sentRegionHandleSet=None):
        if logicalTime is not None:
            self.TsoMsgReceived = True

        if object in self.otherObjects.keys():
            for ah in attributes.keys():
                self.otherObjects[object][ah] = attributes[ah]
                for n in self.ipHandles.keys():
                    if ah == self.ipHandles[n]:
                        self.pendingUpdates.append([logicalTime,n,attributes[ah]])

                        #----------------------- RTI callbacks---------------------------------
#######################################################################################################################
## A common function to initialize FMU 
    def initFMU(self, name, path, params=None ):
        self.fmuName = name
        self.fmuPath = path
        self.model = load_fmu(name, path)
        self.model.initialize()

#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation.
    def waitReadyToPopulate (self):
        self.synchState = SynchState.NotInit
        self.waitWorker("Init")
#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation.
    def waitReadyToRun (self):
        if DEFAULTS.RTI_VERSION == 13 :
            self.waitReadyToRun_13()
        else:
            self.waitReadyToRun_1516()
#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation. This implementation specific function when we are using HLA_13
    def waitReadyToRun_13 (self):
        t = self.rtiaReference.queryFederateTime()
        count = 0
        while len(self.otherObjects) == 0 and count < 2:
            self.rtiaReference.tick()
            count += 1
        self.synchState = SynchState.NotInit
        self.waitWorker("Run")
#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation. This implementation specific function when we are using HLA_1516
    def waitReadyToRun_1516 (self):
        t = self.rtiaReference.queryLogicalTime()
        count = 0
        # when you are sure there is going to be other objects, then put a more strict check and put the 
        # the exact number of objects instead of == 0, of course remove count < 5
        while len(self.otherObjects) == 0 and count < 2:
            self.rtiaReference.evokeCallback(1.0)
            count += 1
        self.synchState = SynchState.NotInit
        self.waitWorker("Run")
#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation. It hides specific function implementations of HLA_13 or HLA_1516

    def waitWorker (self, label):
        if DEFAULTS.RTI_VERSION == 13 :
            self.waitWorker_13(label)
        else:
            self.waitWorker_1516(label)
#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation. This implementation specific function when we are using HLA_1516
    
    def waitWorker_1516 (self, label):
        self.synchLabel = label
        # clear up anything left
        t = self.rtiaReference.queryLogicalTime()
        self.rtiaReference.evokeCallback( 1.0)

        if self.creator == True:
            self.rtiaReference.registerFederationSynchronizationPoint(self.synchLabel,"Waiting for all players") 
            self.synchState = SynchState.RegisterRequested 
            # necessary to ensure that the registration is succeeded
            t = self.rtiaReference.queryLogicalTime()
            while self.synchState < SynchState.Registered:
                self.rtiaReference.evokeCallback(1.0)      

        t = self.rtiaReference.queryLogicalTime()
        while self.synchState < SynchState.Announced:
            self.rtiaReference.evokeCallback(1.0)

        if self.creator==True:
            print ("Press ENTER to start execution...")
            c = sys.stdin.read(1)
        
        self.rtiaReference.synchronizationPointAchieved(self.synchLabel)
        self.synchState = SynchState.Achieved
        
        while self.synchState < SynchState.Synched:
            self.rtiaReference.evokeCallback(1.0)
        print ("Synchronization achieved for label:%s" % self.synchLabel)
        return True        

#######################################################################################################################
## This is one of group of functions which provide the control over starting all the federates at the same clock time. 
## It is only used in the beginning of the simulation. This implementation specific function when we are using HLA_13
    def waitWorker_13 (self, label):
        self.synchLabel = label
        # clear up anything left
        t = self.rtiaReference.queryFederateTime()
        self.rtiaReference.tick()

        if self.creator == True:
            print ("Press ENTER when sure that other federate has started Synchronization...")
            c = sys.stdin.read(1)

            self.rtiaReference.registerFederationSynchronizationPoint(self.synchLabel,"Waiting for all players") 
            self.synchState = SynchState.RegisterRequested 
            # necessary to ensure that the registration is succeeded
            while self.synchState < SynchState.Registered:
                self.rtiaReference.tick()      

        print ("Waiting for Synchronization point to be announced")
        while self.synchState < SynchState.Announced:
            self.rtiaReference.tick()

        if self.creator==True:
            print ("Press ENTER to start execution...")
            c = sys.stdin.read(1)
        
        self.rtiaReference.synchronizationPointAchieved(self.synchLabel)
        self.synchState = SynchState.Achieved
        
        while self.synchState < SynchState.Synched:
            self.rtiaReference.tick()
            
        print ("Synchronization achieved for label:%s" % self.synchLabel)
        return True        

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
