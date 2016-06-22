'''
Created on Mar 19, 2013

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

import time as T
import traceback

from common.utils import *
from common.enumerations import *

from conservative.FMUFederate import *

from scipy.optimize import broyden1
nonLinSolve = broyden1

KINSOL_YES = False
try:
    from pysundials import kinsol
except ImportError:
    try:
        import kinsol
        import math
        import ctypes
        KINSOL_YES= True
    except ImportError:
        pass

import hla.rti as rti
import copy

class FixedStepJacobi(rti.FederateAmbassador,FMUFederate):
    def __init__(self, federateName, rtiaref, maxTime = None ):
        super(FixedStepJacobi, self).__init__(federateName,rtiaref)
        self.isFMUEvent = False

#####################################################################################
## This function actually integrates the FMU and advances it in time. ###############
    def proceed(self, theTime):
        if self.model.time < theTime:
            self.integrate(theTime)
            if DEFAULTS.BDF_METHOD > 0:
                Globals.pastStates.enq(Globals.x)


    def integrate(self,time):
        self.integrate_RK4(time)

    def integrate_FE(self,time):
        Globals.deltaT = time  - self.model.time
        self.model.time = time
        Globals.x = Globals.x + Globals.deltaT * self.model.get_derivatives() 
        self.model.continuous_states = Globals.x

    def integrate_RK4(self,time):
        oldTime = self.model.time
        Globals.deltaT = time  - oldTime
        
        dy1 =  Globals.deltaT * self.model.get_derivatives()

        self.model.time = oldTime +  Globals.deltaT/2.0
        self.model.continuous_states = Globals.x + dy1/2.0
        dy2 = Globals.deltaT * self.model.get_derivatives()
        
        self.model.time = oldTime +  Globals.deltaT/2.0
        self.model.continuous_states = Globals.x + dy2/2.0
        dy3 = Globals.deltaT * self.model.get_derivatives()

        self.model.time = oldTime +  Globals.deltaT
        self.model.continuous_states = Globals.x + dy3
        dy4 = Globals.deltaT * self.model.get_derivatives()
        
        Globals.x = Globals.x + (1/6.0 * (dy1 + 2*dy2 + 2*dy3 + dy4) )
        self.model.continuous_states = Globals.x 

    ######################################################################################################
    ## This is where the updates are applied, and to my knowledge this is the only right way of doing this
    def applyUpdates(self):
        while len(self.pendingUpdates) > 0:
            updt = self.pendingUpdates.pop(0)
            self.model.set(self.subscriptions[updt[UPDT_INDEX.NAME]],float(updt[UPDT_INDEX.VALUE]))

    #####################################################################################
    ## Sends updates to the RTI
    def updateAttributes(self):
        updtDict = {}
        for k,n in self.publications.items():
            updtDict[self.opHandles[k]] = repr(self.model.get(n)[0])
        if len(updtDict) > 0:
            try:
                h = self.rtiaReference.updateAttributeValues(self.myObject,updtDict,"update", self.time)
            except  Exception, e:
                print ("Update exception :"+repr(e)+"Federation time :" + repr(self.rtiaReference.queryFederateTime())+ "self.time:"+repr(self.time))
                print ("object:"+repr(self.myObject))
                print ("updtDict:" + repr(updtDict))
                print ("opHandles:" + repr(self.opHandles))

    #####################################################################################
    def clearEvent(self):
        self.isFMUEvent = False
        for k,v in self.quantizers.items():
            v.clearEvent()
    #####################################################################################
    def isEventOccured(self):
        if self.isFMUEvent == True:
            return True
        for k,v in self.quantizers.items():
            if v.isEventOccured() == True:
                return True
        return False
    #####################################################################################
    ## Called only once, create the instances and attributes of the output variables
    ## inside RTI, needed by other FMU-Federates. After creation they will be available
    ## for other dependant FMU-Federates
    def publish(self, className ,attribNames):
        if className is None or attribNames is None:
            return
        if len(attribNames) == 0:
            return
        if type(attribNames) is not dict:
            raise Exception ("attribNames must be a dictionary")

        self.opClassHandle = self.rtiaReference.getObjectClassHandle(className)
        handleSet = []
        self.publications = attribNames
        for k,n in attribNames.items(): 
            if DEFAULTS.RTI_VERSION == 13:
                self.opHandles[k] = self.rtiaReference.getAttributeHandle(k,self.opClassHandle)
            else:
                self.opHandles[k] = self.rtiaReference.getAttributeHandle(self.opClassHandle,k)
            handleSet.append(self.opHandles[k])

        if DEFAULTS.RTI_VERSION == 13:
            self.rtiaReference.publishObjectClass(self.opClassHandle,handleSet)
        else:    
            self.rtiaReference.publishObjectClassAttributes(self.opClassHandle,handleSet)

######################################################################################################
######################################################################################################
######################################################################################################

def main(START_PATH, FEDERATE_NAME, FEDERATION_NAME,FEDERATION_PATH, FMU_NAME,FMU_PATH, PUB_CLASS, PUBLISH_DICT, SUB_CLASS ,SUBSCRIBE_DICT, OP = None,PARAMS=None ):
    p = START_PATH
    setDefaults(p+'defaults')
    reInitGlobals()
        
    logFile = None
    print("Create ambassador")

    rtia = rti.RTIAmbassador()
    print(rtia)               
    fedAmb = FixedStepJacobi(FEDERATE_NAME,rtia)
    
    try:
        rtia.createFederationExecution(FEDERATION_NAME, FEDERATION_PATH)
        fedAmb.creator = True
        print("Federation created.")
    except Exception , e:
        print("Federation exists: %s" % repr(e))
    finally:
        print ('Federation done.')

    try:
    
        rtia.joinFederationExecution(fedAmb.federateName, FEDERATION_NAME, fedAmb)
        fedAmb.enableTimeSwitches(0.0)
        fedAmb.publish(PUB_CLASS,PUBLISH_DICT)
        fedAmb.subscribe(SUB_CLASS,SUBSCRIBE_DICT)
        fedAmb.waitReadyToPopulate()
        fedAmb.registerInstance(fedAmb.fedrateName)# can be different than federate name
        fedAmb.waitReadyToRun()
        fedAmb.initFMU(FMU_NAME, FMU_PATH)
         
        if DEFAULTS.DRAW_RESULTS > 0:
            t_sol = []
            s_sol = {}
            for o in OP:
                s_sol[o] = []

        if DEFAULTS.DUMP_RESULTS > 0:
            p = O.path.join(p,'Jacobi-RK4-%.2f'%DEFAULTS.DEFAULT_INT_STEP)
            if O.path.exists(p) == False:
                O.makedirs(p)
            p = O.path.join(p,FMU_NAME+".log")

            
            logFile = open(p, 'w+')
            logFile.write("Time\t")
            for o in OP:
                logFile.write(o+"\t")
            logFile.write("\r\n")
        

        Globals.master = fedAmb
        Globals.x = fedAmb.model.continuous_states

        #####################################################################################
        ## The "Master Algorithm".  starts here...

        pt = 0.0
        while fedAmb.time < DEFAULTS.SIM_END:
            pt = pt + DEFAULTS.DEFAULT_INT_STEP
            print ("pt:"+repr(pt)+"\r\n")
            fedAmb.granted = False
            rtia.timeAdvanceRequestAvailable(round(pt,4))
            while fedAmb.granted == False:
                if DEFAULTS.RTI_VERSION == 13 : 
                    rtia.tick()
                else:
                    rtia.evokeCallback(1.0)
            print ("fedAmb.time:"+repr(fedAmb.time))
            ###############################
            #fedAmb.applyUpdates()
            ##############################
            if fedAmb.model.time < fedAmb.time:
                fedAmb.proceed(fedAmb.time)

            if round(fedAmb.time,4)==  round(pt,4):
                fedAmb.updateAttributes()

            fedAmb.granted = False
            rtia.timeAdvanceRequest(round(fedAmb.time,4))
            while fedAmb.granted == False:
                if DEFAULTS.RTI_VERSION == 13 : 
                    rtia.tick()
                else:
                    rtia.evokeCallback(0.0)
            print ("fedAmb.time:"+repr(fedAmb.time)+"\r\n")
            fedAmb.applyUpdates()
            # This shows some serious error in integration or handling of FMU
            if fedAmb.model.time < fedAmb.time:
                raise ('Again the time is less than granted time!!! \r\n')
                

            if DEFAULTS.DRAW_RESULTS > 0:
                t_sol.append(fedAmb.model.time)
                for o in OP:
                    s_sol[o].append(fedAmb.model.get(o)[0])
            
            if DEFAULTS.DUMP_RESULTS > 0:
                logFile.write(repr(fedAmb.model.time)+"\t")
                for o in OP:
                    logFile.write(repr(fedAmb.model.get(o)[0])+"\t")
                logFile.write("\r\n")

        #-------------- end main while----
        #####################################################################################
        ## With the end of while the "Master Algorithm" also ends
            
        if DEFAULTS.DRAW_RESULTS > 0:
            count = 1
            for o in OP:
                P.figure(count)
                P.plot(t_sol,N.array(s_sol[o]),marker='.')
                P.title(o)
                P.ylabel(o)
                P.xlabel('Time (s)')
                count = count + 1
            P.grid(True)
            P.show()
    #------------- end simulation logic ---------------
    
    except Exception, e:
        print("Could not do, exception: %s" % repr(e))
        traceback.print_exc()
        if logFile != None:    
            logFile.write("\nException:\n"+repr(e))

    finally:    
        try:
            fedAmb.terminate()
        except Exception, e:
            print("Could not do, exception: %s" % repr(e))
        try:
            rtia.resignFederationExecution(2)
        except Exception, e:
            print("Could not do, exception: %s" % repr(e))

        #if fedAmb.creator==True:
        try:
            rtia.destroyFederationExecution(FEDERATION_NAME)
        except Exception, e:
            print("Could not do, exception: %s" % repr(e))

        if logFile != None:
            while logFile.closed != True:
                logFile.flush()
                logFile.close()

        print("Done.")
        


if __name__ == "__main__":
    startPath = "/mnt/data/Dropbox/code/SAHISim_git/"

    if sys.argv[1] == 'predPreyX':
        main(START_PATH=startPath, FEDERATE_NAME='predPreyX',FEDERATION_NAME="sl",FEDERATION_PATH=startPath+"foms/SimpleLoop.opt.xml",FMU_NAME="PredPrey_PredPreyX.fmu",FMU_PATH=startPath+"FMUs",PUB_CLASS="sl",PUBLISH_DICT= {'x':'x'},SUB_CLASS="sl",SUBSCRIBE_DICT={"y":"y"},OP= ["x"])

    if sys.argv[1] == 'predPreyY':
        main(START_PATH=startPath, FEDERATE_NAME='predPreyY',FEDERATION_NAME="sl",FEDERATION_PATH=startPath+"foms/SimpleLoop.opt.xml",FMU_NAME="PredPrey_PredPreyY.fmu",FMU_PATH=startPath+"FMUs",PUB_CLASS="sl",PUBLISH_DICT= {'y':'y'},SUB_CLASS="sl",SUBSCRIBE_DICT={"x":"x"},OP= ["y"])

