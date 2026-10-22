"""Read-only sensor modules stay importable/reusable without ROS or a server."""
import ast
from pathlib import Path
import subprocess
import sys
import unittest
import server
import settings
import sensor_models
import sensor_state
import ros_reader


ROOT=Path(__file__).resolve().parent


class BoundaryTests(unittest.TestCase):
    def test_legacy_imports_resolve_to_the_real_modules(self):
        self.assertIs(server.Dashboard,sensor_state.Dashboard);self.assertIs(server.RosReader,ros_reader.RosReader)
        for name in ('finite','planar_pose','scan_summary','occupancy_summary'):
            self.assertIs(getattr(server,name),getattr(sensor_models,name))
        self.assertIs(server.ASSETS,settings.ASSETS)

    def test_imports_start_no_server_ros_motion_or_thread(self):
        code="import sys,threading;sys.path.insert(0,sys.argv[1]);import sensor_models,sensor_state,ros_reader,server;assert 'rospy' not in sys.modules;assert 'cv2' not in sys.modules;assert 'manual_drive' not in sys.modules;assert len(threading.enumerate())==1;assert sensor_state.Dashboard().status()['motor_output'] is False"
        subprocess.run([sys.executable,'-I','-c',code,str(ROOT)],check=True,capture_output=True)

    def test_read_only_layer_cannot_publish_or_launch_processes(self):
        forbidden={'Publisher','Popen','system','execv','execve','call','check_call'}
        for name in ('sensor_models.py','sensor_state.py','ros_reader.py','server.py'):
            tree=ast.parse((ROOT/name).read_text(encoding='utf8'),feature_version=(3,6))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,forbidden,name)

    def test_new_script_order_is_explicit_and_asset_is_served(self):
        html=(ROOT/'dist/index.html').read_text(encoding='utf8')
        self.assertLess(html.index('src="/sensor_view.js"'),html.index('src="/app.js"'))
        self.assertEqual(settings.ASSETS['/sensor_view.js'][0],'sensor_view.js')


if __name__=='__main__':unittest.main()
