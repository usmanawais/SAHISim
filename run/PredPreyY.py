import sys
import os
import subprocess
from subprocess import Popen

jmPath = "/mnt/data/jmBin/" # Install path of JModelica
codePath = "/mnt/data/Dropbox/code/SAHISim_git/" #Root directory of the SAHISim python code
sys.path.append(jmPath+'Python/')#
sys.path.append(codePath)
sys.path.append(codePath+'common/')
sys.path.append(codePath+'conservative/')


from conservative import FixedStepJacobi as simy
startPath = codePath #Root directory, where FMUs , FOMs and other data is located and saved
simy.main(START_PATH=codePath, FEDERATE_NAME='predPreyY',FEDERATION_NAME="sl",FEDERATION_PATH=startPath+"foms/SimpleLoop.opt.xml",FMU_NAME="PredPrey_PredPreyY.fmu",FMU_PATH=startPath+"FMUs",PUB_CLASS="sl",PUBLISH_DICT= {'y':'y'},SUB_CLASS="sl",SUBSCRIBE_DICT={"x":"x"},OP= ["y"])
