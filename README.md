'''
Created on June 21, 2016

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

To run SAHISim, you need to install following packages

- JModelica
- CERTI
- PyHLA

== JMocelica ==

To install JMocelica following link is helpfull
http://www.jmodelica.org/api-docs/usersguide/1.13.0/ch02s03.html

== CERTI ==

To install CERTI following link is helpfull
www.nongnu.org/certi/certi_doc/Install/CERTI_Install.pdf

== PyHLA ==

To install PyHLA following link is helpfull
http://www.nongnu.org/certi/PyHLA/


The class named "FixedStepJacobi" implements a basic co-simulation algorithm, in which all federates are simulating
according to a fixed time step, and they share state variables at each time step.

To generate the FMUs go to "Modelicas" directory, there is a script named GenFMU.py change the paths in that script to point to the Modelica file. Also, set the path where you want to store the FMUs. Run the script and you will find the FMUs in the specified directory.

To execute a simple example, go to "run" directory, open the shell scripts and the python scripts, and set the paths. The description of the paths is given in comments. Also change the name of terminal you are using in the shell script. Then execute the shell script passing the names of python script files as arguments and two screens should appear. One of the screens asks you to press enter when ready. Press the enter button when asked to do so, the simulation will start and the data will be dumped on the path specified in the scripts.

For further information, please contact using the email above.

 

