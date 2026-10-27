"""Ideal laptop-only Ackermann kinematics. No ROS/network or hardware commands."""
import math
import random
from .fusion_geometry import number

TOY = {'wheelbase_m': .30, 'track_m': .28, 'wheel_radius_m': .05,
       'max_speed_m_s': .15, 'max_steering_rad': .45, 'dt_s': .05}


def bicycle_step(pose, speed, steering, dt=.05, wheelbase=.30):
    if not isinstance(pose, (list, tuple)) or len(pose) != 3:
        raise ValueError('Expected x/y/yaw pose')
    x, y, yaw = [number(v) for v in pose]
    v, angle, dt, length = [number(v) for v in (speed, steering, dt, wheelbase)]
    if not 0 < dt <= .1 or not .05 <= length <= 5 or abs(v) > TOY['max_speed_m_s'] or abs(angle) > TOY['max_steering_rad']:
        raise ValueError('Outside toy simulation envelope')
    rate = v*math.tan(angle)/length
    if abs(rate) < 1e-10:
        return [x+v*math.cos(yaw)*dt, y+v*math.sin(yaw)*dt, yaw]
    return [x+v/rate*(math.sin(yaw+rate*dt)-math.sin(yaw)),
            y-v/rate*(math.cos(yaw+rate*dt)-math.cos(yaw)),
            math.atan2(math.sin(yaw+rate*dt), math.cos(yaw+rate*dt))]


def route_exercise(route=None, steps=2400):
    route = [[0, 0], [1, 0], [2, .5], [3, .5]] if route is None else route
    if not isinstance(route, list) or not 2 <= len(route) <= 100 or type(steps) is not int or not 1 <= steps <= 10000:
        raise ValueError('Invalid bounded route')
    dense = []
    for a, b in zip(route, route[1:]):
        if any(not isinstance(p, (list, tuple)) or len(p) != 2 for p in (a, b)):
            raise ValueError('Expected route XY points')
        a, b = [[number(v) for v in p] for p in (a, b)]
        distance = math.hypot(b[0]-a[0], b[1]-a[1])
        if not .01 <= distance <= 10:
            raise ValueError('Invalid route segment length')
        count = max(1, int(math.ceil(distance/.05)))
        dense.extend([[a[j]+(b[j]-a[j])*i/count for j in range(2)] for i in range(count)])
    dense.append(list(b))
    pose = [dense[0][0], dense[0][1], math.atan2(dense[1][1]-dense[0][1], dense[1][0]-dense[0][0])]
    trace, nearest, errors = [], 0, []
    for index in range(steps):
        # Monotonic path progress; target a bounded lookahead along the reference.
        nearest = min(range(nearest, len(dense)), key=lambda i: math.hypot(dense[i][0]-pose[0], dense[i][1]-pose[1]))
        error = math.hypot(dense[nearest][0]-pose[0], dense[nearest][1]-pose[1])
        errors.append(error)
        if math.hypot(dense[-1][0]-pose[0], dense[-1][1]-pose[1]) < .12:
            break
        target = dense[min(len(dense)-1, nearest+8)]
        dx, dy = target[0]-pose[0], target[1]-pose[1]
        alpha = math.atan2(dy, dx)-pose[2]
        steering = math.atan2(2*TOY['wheelbase_m']*math.sin(alpha), max(.1, math.hypot(dx, dy)))
        steering = max(-TOY['max_steering_rad'], min(TOY['max_steering_rad'], steering))
        pose = bicycle_step(pose, TOY['max_speed_m_s'], steering, TOY['dt_s'], TOY['wheelbase_m'])
        trace.append({'t': (index+1)*TOY['dt_s'], 'pose': pose,
                      'sim_speed_m_s': TOY['max_speed_m_s'], 'sim_steering_rad': steering})
    final = math.hypot(dense[-1][0]-pose[0], dense[-1][1]-pose[1])
    return {'mode': 'synthetic_ideal_kinematics', 'parameters': dict(TOY),
            'reference_xy_m': route, 'trace': trace,
            'metrics': {'reached': final < .12, 'final_error_m': final,
                        'sampled_reference_error_max_m': max(errors), 'steps': len(trace)},
            'stop_requested_in_simulation': True, 'hardware_output': False,
            'limits': 'No dynamics, obstacles, braking, Gazebo execution or hardware performance proof.'}


def obstacles(seed=7, count=10):
    if type(seed) is not int or not 0 <= seed < 2**31 or type(count) is not int or not 0 <= count <= 30:
        raise ValueError('Invalid deterministic world parameters')
    rng = random.Random(seed)
    result = []
    for index in range(count):
        result.append({'name': 'obstacle_%d' % index, 'x': rng.uniform(1, 4.3),
                       'y': rng.uniform(-2.4, 2.4), 'sx': rng.uniform(.2, .5),
                       'sy': rng.uniform(.2, .5), 'height': rng.uniform(.3, 1.0)})
    return result
