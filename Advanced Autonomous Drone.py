
# Swarm Sequence Code Group 1

import time
import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
import math
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

# Drone with sticker placed closer to the net
 

URI0='radio://0/80/2M/5C21CF0101'

URI1='radio://0/80/2M/5C21CF0102'

params0 = {'init_x':0,'init_y':-0.5,'init_z':1,'x0': 1.0, 'y0': -0.3, 'z0' :1}

params1 = {'init_x':0,'init_y':0.5,'init_z':1,'x0': 1.0, 'y0': 0.3, 'z0':1}

uris = {

   URI0,

    URI1,

}

 

params = {

    URI0: [params0],

    URI1: [params1],

}

 

def sine_sequence(scf, params):

    with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID) as pc:

        cf = scf.cf

 

        pc.go_to(params['init_x'], params['init_y'], params['init_z'], 1)

        time.sleep(1)

        pc.go_to(params['x0'], params['y0'], params['z0'], 1)

        #pc.left(1.0)

 

        pc.back(1.0)

 

        #pc.right(1.0)

 

        for p in range(-9,9):

            pc.go_to(p/7, params['y0'], 1+(1/2*math.sin(2*p)))

 

        pc.go_to(params['x0'], params['y0'], params['z0'])

        time.sleep(3)

 

        pc.go_to(params['init_x'], params['init_y'], 1.0)

        time.sleep(3)

 

        pc.down(0.2)

 

def sync(scf, params):

 

    print('Syncing...')

 

def complex_usage(scf, params):

 

   with MotionCommander(scf, default_height=0.5) as mc:

 

        mc.circle_left(0.4, 1.5, angle_degrees=360.0)

 

        mc.circle_right(0.4, 0.6, angle_degrees=180)

 

        mc.forward(1)

 

        mc.right(0.5)

 

        mc.up(0.5)

 

if __name__ == '__main__':

    cflib.crtp.init_drivers()

    factory = CachedCfFactory(rw_cache='./cache')

    duration = time.time()

    print("starting")

    with Swarm(uris, factory=factory) as swarm:

        print('Connected to  Crazyflies, Stand Clear, delay: {}'.format(time.time()-duration))

        duration = time.time()

 

        swarm.parallel_safe(sync, args_dict=params)

        print('Ran syc safe, Delay: {}'.format(time.time()-duration))

        duration = time.time()

 

        swarm.parallel_safe(sine_sequence, args_dict=params)

        print('Ran sine_sequence safe, Delay: {}'.format(time.time()-duration))

        duration = time.time()

 

        swarm.parallel_safe(complex_usage, args_dict=params)

        print('Ran complex manuever safe, Delay: {}'.format(time.time()-duration))