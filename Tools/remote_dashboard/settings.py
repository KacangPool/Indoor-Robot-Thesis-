"""Dashboard version, fixed read-only topics and static asset allowlist.

No ROS imports, dynamic topic configuration or robot side effects.
"""
VERSION = '0.18'

ASSETS = {'/': ('index.html', 'text/html; charset=utf-8'),
          '/app.js': ('app.js', 'application/javascript; charset=utf-8'),
          '/sensor_view.js': ('sensor_view.js', 'application/javascript; charset=utf-8'),
          '/scene_geometry.js': ('scene_geometry.js', 'application/javascript; charset=utf-8'),
          '/joystick.js': ('joystick.js', 'application/javascript; charset=utf-8'),
          '/controls.css': ('controls.css', 'text/css; charset=utf-8'),
          '/style.css': ('style.css', 'text/css; charset=utf-8')}
TOPICS = {'rgb': '/camera/rgb/image_raw',
          'yolo': '/darknet_ros/detection_image', 'scan': '/scan', 'boxes': '/darknet_ros/bounding_boxes'}
