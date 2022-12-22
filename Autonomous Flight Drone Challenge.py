"""
Created on Mon Oct  3 11:13:06 2022
@author: eucar
This script shows the basic use of the PositionHlCommander class
Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system.
"""

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to

uri = uri_helper.uri_from_env(default='radio://0/80/2M/5C21CF0101')

def complex_usage():

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        with PositionHlCommander(

                scf,

                x=0.0, y=0.0, z=0.0,

                default_velocity=0.3,

                default_height=0.5,

                controller=PositionHlCommander.CONTROLLER_PID) as pc:

            # Go to a coordinate

            pc.go_to(1.0, 1.0, 1.0)

            # Move relative to the current position

            pc.right(1.0)

 

            # Go to a coordinate and use default height

            pc.go_to(0.0, 0.0)

 

            # Go slowly to a coordinate

            pc.go_to(1.0, 1.0, velocity=0.2)

 

            # Set new default velocity and height

            pc.set_default_velocity(0.3)

            pc.set_default_height(1.0)

            pc.go_to(0.0, 0.0)
 
def simple_sequence():

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID) as pc:

            pc.forward(1.0)

            pc.left(1.0)

            pc.back(1.0)

            pc.go_to(0.0, 0.0, 1.0)

            pc.go_to(0.0, 0.0, 0.0)

if __name__ == '__main__':

    cflib.crtp.init_drivers()

    simple_sequence()

    # complex_usage()