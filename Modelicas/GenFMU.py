'''
Created on Jun 7, 2016

@author: usman
'''
from pymodelica import compile_fmu

import subprocess
import os
import shutil
import glob




def main_JM(modelName,modelFile, outpath):
    os.chdir(outpath)
    fmu = compile_fmu(modelName, modelFile)
    return fmu

def main_OM(modelName,modelFile, outpath):
    genPath = os.path.join(outpath,modelName)
    modelAlone= modelFile.split('/')[-1]
    if os.path.exists(genPath) == False:
        os.mkdir(genPath)
    os.chdir(genPath)
    shutil.copy(modelFile,genPath)
    script = os.path.join(genPath,"genFMU.mos")
    scriptFile = open(script,'w+')
    scriptFile.write("setCommandLineOptions({\"+d=rml,noevalfunc\", \"+g=MetaModelica\"});\r\n")
    scriptFile.write("setEnvironmentVar(\"MODELICAUSERFLAGS\", \"-g\");\r\n")
    scriptFile.write("loadFile(\""+modelAlone+"\");\r\n")
    scriptFile.write("getErrorString();\r\n")
    scriptFile.write("translateModelFMU("+modelName+");\r\n")
    scriptFile.write("getErrorString();")
    scriptFile.flush();
    scriptFile.close()
    o = subprocess.check_output(["omc genFMU.mos"],shell=True)
    print(o)
    files = glob.iglob(os.path.join(genPath, "*.fmu"))
    fmu = None
    for file in files:
        if os.path.isfile(file):
            shutil.copy2(file, outpath)
            fmu = file
    return fmu

if __name__ == "__main__":
    outPath = 'FMUs/'# set this path where you want to export FMUs

    modelPath = 'PredPrey.mo' # set the path of model file

    main_JM('PredPrey.PredPreyX', modelPath, outPath)
    main_JM('PredPrey.PredPreyY', modelPath, outPath)


