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

#import hla.rti as rti

from common.enumerations import *

import sys as S
import numpy as N

global DEFAULT_Q_STEP
global DEFAULT_INT_STEP
global DEFAULT_PRECISION
global DEFAULT_QUANTA
global DEFAULT_WIN_SZ        
global DEFAULT_SPLINE_ORDER


#####################################################################################
class CircularQeue():
    def __init__(self, capacity, copyMethod='numpy'):
        self.maxLen = capacity
        self.data = []
        self.len = 0
        self.currentIndex = 0
        self.copyMethod = copyMethod

    def getCapacity(self):
        return self.maxLen

    def reInit(self):
        del self.data
        self.data = []
        self.len = 0
        self.currentIndex = 0

    def copy(self, p):
        del self.data
        self.data = []
        for e in p.data:
            self.data.append(e)
        self.len = p.len
        self.currentIndex = p.currentIndex
        self.maxLen = p.maxLen

    def enq(self, e, copyMethod=None):
        if copyMethod == None:
            copyMethod = self.copyMethod
        if copyMethod.lower() == 'numpy':
            elem = N.copy(e)
        elif copyMethod.lower() == 'copy':
            elem = e.copy()
        elif copyMethod.lower() == 'scalar':
            elem = e
        else:
            elem = e

        if self.len < self.maxLen:
            self.data.append(elem)
            self.len += 1
            self.currentIndex += 1
        else:
            victum = self.currentIndex
            if self.currentIndex == self.len:
                victum = 0
            popped = self.data.pop(victum)
            self.data.insert(victum, elem)
            self.currentIndex = victum + 1
            del popped

    def __getitem__(self, index):
        if index >= 0 or (index < 0 and fabs(index) <= self.len):
            if index < self.len:
                retIndex = (self.currentIndex + index) % self.len
                if retIndex < 0:
                    retIndex = self.len + retIndex
                return self.data[retIndex]
            else:
                raise (Exception("Index out of bound"))

    def __len__(self):
        return self.len

    def __del__(self):
        del self.data
        self.maxLen = -1
        self.len = -1
        self.currentIndex = -1


#####################################################################################
class Globals():
    dxParts = []
    dxBits = []
    dx = []
    x = []
    master = None
    ####################################################
    timeBits = []
    times = []
    convergeBits = []
    ####################################################
    ## For BDF method
    deltaT = 0.0
    pastStates = CircularQeue(3)
    oldXSum = 0.0
    maxBroydenIter = 100
    derFactor = 1.0
    stepSizeFactor = 3.0
    stepSizeIncr = 0.1
    iterationCount = 0

####################################################
def reInitGlobals():
    del Globals.dxParts
    Globals.dxParts = []
    del Globals.dxBits
    Globals.dxBits = []
    del Globals.dx
    Globals.dx = []
    del Globals.x
    Globals.x = []
    Globals.master = None
    ####################################################
    ## For BDF method
    Globals.deltaT = 0.0
    del Globals.pastStates
    if DEFAULTS.BDF_METHOD < 0:
        Globals.pastStates = CircularQeue(1)
    else:
        Globals.pastStates = CircularQeue(DEFAULTS.BDF_METHOD)
    Globals.oldXSum = 0.0
    Globals.maxBroydenIter = 50
    Globals.derFactor = 1.0
    Globals.stepSizeFactor = 3.0
    Globals.stepSizeIncr = 0.1

    Globals.iterationCount = 0
##################################################################################################################
## This class may considered a pure abstract class for an FMU-Federate, but because 
## there are no pure abstracts in Python so you cannot declare it like that.
## It hides out some very basic functionalities, which are ought to be done in the way they are done here
## It is different from FMUFederate class because in the case of FMUFederate you could change the implementation
## of few thing, which could be less or more efficient, but what is done here must be done as it is. 
class BaseFMUFederate(object):
    '''
    classdocs
    '''


    def __init__(self,federateName,rtiaref):
        '''
        Constructor
        '''
        self.otherObjects = {}
        self.subscriptions = {}
        self.publications = {}
        self.ipHandles = {}
        self.opHandles = {}
        self.quantizers = {}
        
        self.ipClassHandle = None

        self.synchState = SynchState.NotInit 
        self.granted = False
        self.time = 0.0
        self.rtiaReference = rtiaref
        self.timeState = TimeState.NotInit

        ## Currently following three are bound to index, meaning there is one-one relationship between them
        self.regObjects = []
        self.opObjectNames = []
        self.opClassHandles = []
        ##-------------------------------------------------------------

        self.fedrateName = federateName
        self.creator = False
        self.lookAhead = 0       
        self.nameReserved = False
###########################################################################################################################
    
    @property
    def myObject(self):
        if len(self.regObjects) == 0 :
            return None
        return self.regObjects[0]


    @myObject.setter
    def myObject(self,value):
        if len(self.regObjects) == 0 :
            self.regObjects.append(value)
        else:
            self.regObjects[0] = value

    @myObject.getter
    def myObject(self):
        if len(self.regObjects) == 0 :
            return None
        return self.regObjects[0]
###########################################################################################################################

    @property
    def opObjectName(self):
        if len(self.opObjectNames) == 0 :
            return None
        return self.opObjectNames[0]

    @opObjectName.setter
    def opObjectName(self,value):
        if len(self.opObjectNames) == 0 :
            self.opObjectNames.append(value)
        else:
            self.opObjectNames[0] = value

    @opObjectName.getter
    def opObjectName(self):
        if len(self.opObjectNames) == 0 :
            return None
        return self.opObjectNames[0]
###########################################################################################################################

    @property
    def opClassHandle(self):
        if len(self.opClassHandles) == 0 :
            return None
        return self.opClassHandles[0]

    @opClassHandle.setter
    def opClassHandle(self,value):
        if len(self.opClassHandles) == 0 :
            self.opClassHandles.append(value)
        else:
            self.opClassHandles[0] = value

    @opClassHandle.getter
    def opClassHandle(self):
        if len(self.opClassHandles) == 0 :
            return None
        return self.opClassHandles[0]
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

 
    def getNextEventTime(self):
        pass
    
    def terminate(self):
        if self.regObjects is not None and len(self.regObjects) > 0:
            for i in range(0,len(self.regObjects)):
                self.rtiaReference.deleteObjectInstance(self.regObjects[i], self.opObjectNames[i])


    def publish(self, className ,opNames):
        pass
    def subscribe(self, className ,ipNames):        
        pass

    def enableTimeSwitches(self, lookahead ):
        if DEFAULTS.RTI_VERSION == 13 :
            self.enableTimeSwitches_13(lookahead)
        else:
            self.enableTimeSwitches_1516(lookahead)
            
    def enableTimeSwitches_13(self, lookahead ):
        self.lookAhead = lookahead        
        self.rtiaReference.enableTimeConstrained()
        t = self.rtiaReference.queryFederateTime()
        self.rtiaReference.enableTimeRegulation(t + 1,self.lookAhead)

    def enableTimeSwitches_1516(self, lookahead ):
        self.rtiaReference.setLogicalTimeFactory("certiFedTime1516")
        self.lookAhead = lookahead        
        self.rtiaReference.enableTimeConstrained()
        self.rtiaReference.enableTimeRegulation(self.lookAhead)

    def updateAttributes(self):
        pass

    def registerAllInstances(self, names):   
        for i in range(0,len(names)):
            self.registerInstance(names[i],self.opClassHandles[i])
    def registerInstance(self, name,classHandle=None):   
        if DEFAULTS.RTI_VERSION == 13 :
            self.registerInstance_13(name,classHandle)
        else:
            self.registerInstance_1516(name,classHandle)
            
    def registerInstance_1516(self, name,classHandle=None):   
        
        if classHandle is None:
            classHandle = self.opClassHandles[-1]
            
        t = self.rtiaReference.queryLogicalTime()
        self.rtiaReference.evokeMultipleCallbacks(0,t+1.0)

        self.opObjectNames.append(name)
        self.rtiaReference.reserveObjectInstanceName(name)
        
        while self.nameReserved == False:
            self.rtiaReference.evokeCallback(1.0)
        
        self.regObjects.append(self.rtiaReference.registerObjectInstance(classHandle, name))

    def registerInstance_13(self, name,classHandle=None):   
        if classHandle is None:
            classHandle = self.opClassHandles[-1]
        self.opObjectNames.append(name)
        self.regObjects.append(self.rtiaReference.registerObjectInstance(classHandle, name))
             
        
    #+++++++++++++++++++++ RTI callbacks ++++++++++++++++++++++++++++++++++++
    
    def synchronizationPointRegistrationFailed(self, label, reason):
        #if label == self.synchLabel and self.creator == False:
            self.synchState = SynchState.Registered
            print("synchronizationPointRegistrationFailed  %s" % repr(reason))

    def objectInstanceNameReservationSucceeded(self, name):
        if name in self.opObjectNames:
            self.nameReserved = True
            return
        raise Exception('objectInstanceNameReservationSucceeded: Name is not same as reserved')
    
    def timeRegulationEnabled(self, time):
        self.timeState |= TimeState.Regulated

    def timeConstrainedEnabled(self, time):
        self.timeState |= TimeState.Constrained

        
    def startRegistrationForObjectClass(self,params):
        pass
    
    def provideAttributeValueUpdate(self,*params):
        pass
    
    def discoverObjectInstance(self, object, objectclass, name):
        if object not in self.otherObjects and object not in self.regObjects:
            self.otherObjects[object] = {}          
    
    def announceSynchronizationPoint(self, label, tag):
        #if label == self.synchLabel:
            self.synchState=SynchState.Announced
            print("announceSynchronizationPoint  %s" % repr(label))

    def synchronizationPointRegistrationSucceeded(self,label):
        #if label == self.synchLabel:
            self.synchState=SynchState.Registered
            print("synchronizationPointRegistrationSucceeded  %s" % repr(label))
    
    def removeObjectInstance(self,object,  userSuppliedTag, theTime=None, retractionHandle=None):
         if object in self.otherObjects:
             self.otherObjects.pop(object)

        
    def federationSynchronized(self,label)  :
        #if label == self.synchLabel:
            self.synchState=SynchState.Synched
            print("federationSynchronized  %s" % repr(label))
         
       
    def reflectAttributeValues(self, object, attributes, tag, order, transport,logicalTime=None, receiveOrder=None,regionHandleSet=None, sentRegionHandleSet=None):
        pass

    #TODO: May be there is a chance to improve the precision by converting from binary instead of string
    def timeAdvanceGrant(self, time):
        self.granted = True
        self.time = round (time,DEFAULTS.DEFAULT_PRECISION)

    #---------------------RTI callbacks --------------------------
    
    #+++++++++++++++++++++++++ FMI ++++++++++++++++++++++++++++
    def initFMU(self, name, path, params=None ):
        raise("initFMU is not implemented")
        
    def setFMUTime (self, time):
        raise("Do not setFMUTime in this way it is devastating")

    def getFMUTime (self):
        return self.model.time
        
    def getFMUVariable(self, name):
        return self.model.get(name)[0]
        
    def setFMUVariable(self, name,value):
        self.model.set(name, value)
        
    #---------------------------- FMI --------------------------
        
