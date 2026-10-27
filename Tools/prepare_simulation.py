"""Generate isolated generic Gazebo Harmonic examples; never install/run/publish."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from fahad_core.simulation import TOY, obstacles, route_exercise
from fahad_core.recording import write_json


def tag(parent, element, value=None, **attrs):
    node = ET.SubElement(parent, element, attrs)
    if value is not None:
        node.text = str(value)
    return node


def solid(model, name, pose, size, mass=1, cylinder=False):
    link = tag(model, 'link', name=name)
    tag(link, 'pose', pose)
    inertia = tag(link, 'inertial')
    tag(inertia, 'mass', mass)
    tensor = tag(inertia, 'inertia')
    # Positive generic inertias; not a measured physical vehicle model.
    for name_, value in [('ixx', mass*.01), ('iyy', mass*.01), ('izz', mass*.01), ('ixy', 0), ('ixz', 0), ('iyz', 0)]:
        tag(tensor, name_, value)
    for kind in ('collision', 'visual'):
        node = tag(link, kind, name=name+'_'+kind)
        shape = tag(tag(node, 'geometry'), 'cylinder' if cylinder else 'box')
        if cylinder:
            tag(shape, 'radius', TOY['wheel_radius_m'])
            tag(shape, 'length', .04)
        else:
            tag(shape, 'size', size)
        if kind == 'visual':
            material = tag(node, 'material')
            tag(material, 'ambient', '.12 .55 .42 1' if not cylinder else '.05 .05 .05 1')
            tag(material, 'diffuse', '.12 .55 .42 1' if not cylinder else '.05 .05 .05 1')
    return link


def joint(model, name, parent, child, axis, expressed, steering=False):
    node = tag(model, 'joint', name=name, type='revolute')
    tag(node, 'parent', parent)
    tag(node, 'child', child)
    ax = tag(node, 'axis')
    tag(ax, 'xyz', axis, expressed_in=expressed)
    limit = tag(ax, 'limit')
    tag(limit, 'lower', -.5 if steering else -1e16)
    tag(limit, 'upper', .5 if steering else 1e16)
    tag(limit, 'effort', 10)
    tag(limit, 'velocity', 20)


def vehicle(world):
    model = tag(world, 'model', name='home_lab_toy_car')
    base = solid(model, 'base', '0 0 .14 0 0 0', '.42 .23 .12', 2)
    half_length, half_track, radius = TOY['wheelbase_m']/2, TOY['track_m']/2, TOY['wheel_radius_m']
    for side, y in [('left', half_track), ('right', -half_track)]:
        rear = 'rear_'+side
        solid(model, rear, '%s %s %s 1.57079632679 0 0' % (-half_length, y, radius), None, .1, True)
        joint(model, rear+'_joint', 'base', rear, '0 1 0', '__model__')
        knuckle = 'front_'+side+'_knuckle'
        solid(model, knuckle, '%s %s %s 0 0 0' % (half_length, y, radius), '.02 .02 .02', .02)
        joint(model, side+'_steering', 'base', knuckle, '0 0 1', '__model__', True)
        wheel = 'front_'+side
        solid(model, wheel, '%s %s %s 1.57079632679 0 0' % (half_length, y, radius), None, .1, True)
        joint(model, wheel+'_joint', knuckle, wheel, '0 1 0', knuckle)
    driver = tag(model, 'plugin', filename='gz-sim-ackermann-steering-system', name='gz::sim::systems::AckermannSteering')
    for name, value in [('left_joint', 'rear_left_joint'), ('right_joint', 'rear_right_joint'),
                        ('left_steering_joint', 'left_steering'), ('right_steering_joint', 'right_steering'),
                        ('wheel_base', TOY['wheelbase_m']), ('wheel_separation', TOY['track_m']), ('kingpin_width', TOY['track_m']),
                        ('wheel_radius', radius), ('steering_limit', TOY['max_steering_rad']), ('steer_p_gain', 1),
                        ('min_velocity', -.15), ('max_velocity', .15),
                        ('min_acceleration', -.2), ('max_acceleration', .2),
                        ('topic', '/home_lab_sim/cmd_vel'), ('odom_topic', '/home_lab_sim/odom'),
                        ('tf_topic', '/home_lab_sim/tf'), ('frame_id', 'home_lab_sim/odom'), ('child_frame_id', 'home_lab_sim/base')]:
        tag(driver, name, value)
    sensor = tag(base, 'sensor', name='toy_lidar', type='gpu_lidar')
    tag(sensor, 'pose', '0 0 .05 0 0 0')
    tag(sensor, 'topic', '/home_lab_sim/scan')
    tag(sensor, 'update_rate', 10)
    tag(sensor, 'always_on', 'true')
    lidar = tag(sensor, 'lidar')
    horizontal = tag(tag(lidar, 'scan'), 'horizontal')
    for name, value in [('samples', 360), ('resolution', 1), ('min_angle', -3.14159265), ('max_angle', 3.14159265)]:
        tag(horizontal, name, value)
    range_ = tag(lidar, 'range')
    for name, value in [('min', .1), ('max', 8), ('resolution', .01)]:
        tag(range_, name, value)
    camera = tag(base, 'sensor', name='toy_rgbd', type='rgbd_camera')
    tag(camera, 'pose', '.2 0 0 0 0 0')
    tag(camera, 'topic', '/home_lab_sim/rgbd')
    tag(camera, 'update_rate', 10)
    tag(camera, 'always_on', 'true')
    definition = tag(camera, 'camera')
    tag(definition, 'horizontal_fov', 1.05)
    image = tag(definition, 'image')
    for name, value in [('width', 640), ('height', 480), ('format', 'R8G8B8')]:
        tag(image, name, value)
    clip = tag(definition, 'clip')
    tag(clip, 'near', .1)
    tag(clip, 'far', 8)


def world_xml(name, boxes):
    root = ET.Element('sdf', version='1.9')
    world = tag(root, 'world', name=name)
    physics = tag(world, 'physics', name='toy_physics', type='ignored')
    tag(physics, 'max_step_size', .001)
    tag(physics, 'real_time_factor', 1)
    for file, system in [('physics', 'Physics'), ('user-commands', 'UserCommands'), ('scene-broadcaster', 'SceneBroadcaster'), ('sensors', 'Sensors')]:
        p = tag(world, 'plugin', filename='gz-sim-'+file+'-system', name='gz::sim::systems::'+system)
        if system == 'Sensors':
            tag(p, 'render_engine', 'ogre2')
    tag(world, 'gravity', '0 0 -9.8')
    light = tag(world, 'light', name='sun', type='directional')
    tag(light, 'pose', '0 0 10 0 0 0')
    tag(light, 'diffuse', '.8 .8 .8 1')
    tag(light, 'direction', '-.5 .2 -1')
    ground = tag(world, 'model', name='ground')
    tag(ground, 'static', 'true')
    solid(ground, 'ground_link', '2 0 -.1 0 0 0', '8 8 .2')
    boundaries = [dict(name='wall_'+str(i), x=x, y=y, sx=sx, sy=sy, height=1)
                  for i, (x, y, sx, sy) in enumerate([(-1, 0, .1, 6), (5, 0, .1, 6), (2, -3, 6, .1), (2, 3, 6, .1)])]
    for box in boundaries + boxes:
        model = tag(world, 'model', name=box['name'])
        tag(model, 'static', 'true')
        solid(model, 'body', '%s %s %s 0 0 0' % (box['x'], box['y'], box['height']/2),
              '%s %s %s' % (box['sx'], box['sy'], box['height']))
    vehicle(world)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def prepare(output, seed=7):
    boxes = obstacles(seed)
    route = route_exercise()
    target = Path(output)
    target.mkdir(parents=True, exist_ok=False)
    for name, walls in [('known_route', []), ('seeded_unknown', boxes), ('mapping', boxes)]:
        (target/(name+'.sdf')).write_bytes(world_xml(name, walls))
    write_json(str(target/'ideal_route.json'), route)
    write_json(str(target/'evaluator_truth.json'), {'mode': 'synthetic', 'seed': seed, 'obstacles': boxes,
               'policy': 'Evaluator truth only; never give this map to an unknown-world exploration policy.'})
    bridges = []
    for topic, ros_type, gz_type, direction in [
        ('scan', 'sensor_msgs/msg/LaserScan', 'gz.msgs.LaserScan', 'GZ_TO_ROS'),
        ('odom', 'nav_msgs/msg/Odometry', 'gz.msgs.Odometry', 'GZ_TO_ROS'),
        ('tf', 'tf2_msgs/msg/TFMessage', 'gz.msgs.Pose_V', 'GZ_TO_ROS'),
        ('cmd_vel', 'geometry_msgs/msg/Twist', 'gz.msgs.Twist', 'ROS_TO_GZ')]:
        bridges.append({'ros_topic_name': '/home_lab_sim/'+topic, 'gz_topic_name': '/home_lab_sim/'+topic,
                        'ros_type_name': ros_type, 'gz_type_name': gz_type, 'direction': direction})
    write_json(str(target/'bridge_config.json'), bridges)
    write_json(str(target/'simulation_manifest.json'), {'schema_version': 1, 'mode': 'synthetic', 'seed': seed,
               'target': 'Gazebo Harmonic / ROS2 Jazzy / separate Ubuntu laptop environment',
               'dimensions': TOY, 'gazebo_executed': False, 'hardware_adapter': False,
               'camera_bridge': 'Pending confirmation of generated RGBD topic names in Gazebo',
               'limits': 'Generic example, not a calibrated Wheeltec model. Unknown navigation/SLAM not implemented.'})
    return route['metrics']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=7)
    args = parser.parse_args(argv)
    try:
        metrics = prepare(args.output, args.seed)
        print('Prepared synthetic simulation files; ideal route reached=%s. Gazebo NOT executed.' % metrics['reached'])
        return 0
    except (ValueError, OSError):
        print('Preparation refused: check seed and choose a NEW output directory.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
