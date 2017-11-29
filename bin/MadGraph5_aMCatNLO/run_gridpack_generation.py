import os
import glob
import math
from array import array
import sys
import time
import subprocess
import random

from optparse import OptionParser
from subprocess import Popen

############################################                                                                                                                                                           
#            Job steering                  #                                                                                                                                                           
############################################                                                                                                                                                           

parser = OptionParser()
parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--inputProcessDIR', action="store", type="string", dest="inputProcessDIR", default="",    help="Input directory where the template file are stored")
parser.add_option('--nameToGrep',      action="store", type="string", dest="nameToGrep",      default="",    help="Name to grep in the input directory")
parser.add_option('--queque',          action="store", type="string", dest="queque",          default="1nd", help="queque")
parser.add_option('--runOnBatch',      action='store_true', dest='runOnBatch', default=False, help='runOnBatch -> using the official GEN group script')
parser.add_option('--produceProcess',  action='store_true', dest='produceProcess', default=False, help='produceProcess -> make the directory with the process')
parser.add_option('--produceGridPack', action='store_true', dest='produceGridPack', default=False, help='produceProcess -> make the directory with the process')
(options, args) = parser.parse_args()

if __name__ == '__main__':

    cwd = os.getcwd();

    if options.nameToGrep != "":
        os.system("ls "+options.inputProcessDIR+" | grep "+options.nameToGrep+" > file.list\n");
    else:
        os.system("ls "+options.inputProcessDIR+" > file.list\n");
        
    file = open("file.list","r");    
    for lines in file:
        entry = lines.replace("\n","");
        path = entry.split("/")        
        if options.runOnBatch:
            command = "./submit_gridpack_generation.sh 1200 1200 "+options.queque+" "+path[len(path)-1]+" "+options.inputProcessDIR+"/"+entry+" "+options.queque;
            os.system(command);
        else:
            if options.produceProcess:
                os.system("mkdir -p "+entry);
                os.system("scp "+options.inputProcessDIR+"/"+entry+"/*proc_card.dat ./");
                os.system("./bin/mg5_aMC -f "+entry+"_proc_card.dat");
                os.system("rm *proc_card.dat");
                os.system("scp "+options.inputProcessDIR+"/"+entry+"/* "+entry);
            elif options.produceGridPack:

                os.chdir(cwd);
                os.chdir(options.inputProcessDIR+"/"+entry);
                
                
                #### fix the PDF
                isnlo = 0;
                if os.path.isfile("MCatNLO"):
                    isnlo = 1;

                #### copy files
                
                print os.getcwd()
                os.system("scp *_cuts.f SubProcesses/cuts.f");
                os.system("scp *_run_card.dat Cards/run_card.dat");
                os.system("scp *_param_card.dat Cards/param_card.dat");
                os.system("scp *_setscales.f Cards/setscales.f");
                os.system("scp *_setcuts.f Cards/setcuts.f");
                os.system("scp *_reweight_card.dat Cards/reweight_card.dat");

                if isnlo:
                    os.system("scp *_madspin_card.dat Cards/madspin_card.dat");
                    makegrid = open("makegrid.dat","w");
                    makegrid.write("shower=OFF \n");
                    makegrid.write("done \n");                    
                    os.system("cat "+entry+"_customizecards.dat >> makegrid.dat");
                    makegrid.write("\n");
                    makegrid.write("done \n");
                    os.system("cat makegrid.dat | ./bin/generate_events -n pilotrun");
                else:
                    os.system("scp *_madspin_card.dat Cards/madspin_card.dat");
                    makegrid = open("makegrid.dat","w");
                    makegrid.write("done \n");                    
                    makegrid.write("set gridpack True \n");                    
                    os.system("cat "+entry+"_customizecards.dat >> makegrid.dat");
                    makegrid.write("\n");
                    makegrid.write("done \n");
                    os.system("cat makegrid.dat | ./bin/generate_events -n pilotrun");

    os.system("rm file.list");
                    
