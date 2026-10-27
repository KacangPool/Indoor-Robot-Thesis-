"""Hub logic, safety/ownership and deployment tests. No robot access."""
import ast
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

import agent
import connection
from hub import App, DemoConnection, SOURCE
import hub
import queue


def graph(publishers=None, subscribers=None, nodes=None, reachable=True):
    return {'reachable':reachable,'publishers':publishers or {},'subscribers':subscribers or {},'nodes':nodes or []}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(os.path.realpath(self.temp.name))
        self.graph=graph();self.dashboard=None;self.processes=[]
        self.manager=agent.Manager(str(self.root),lambda:self.graph,lambda:self.dashboard,lambda:self.processes)
    def stage(self,identity='a'*32,content=b'first'):
        root=self.root/'robot_hub'/'staging'/identity;files={}
        for name in agent.RUNTIME_FILES:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content+name.encode())
            files[name]=agent.digest(str(path))
        manifest={'version':agent.VERSION,'files':files,'bundle_id':agent.bundle_id(files)}
        (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf8')
        return root,manifest
    def test_empty_status_does_not_start_anything(self):
        with mock.patch.object(agent.subprocess,'Popen') as spawn:
            status=self.manager.status();spawn.assert_not_called()
        self.assertEqual(set(status['services'].values()),{'stopped'});self.assertFalse(status['runtime_ok'])
    def test_camera_registered_partial_does_not_duplicate(self):
        self.graph=graph({'/camera/rgb/image_raw':['/camera/driver']},nodes=['/camera/driver'])
        with mock.patch.object(agent.subprocess,'Popen') as spawn,self.assertRaisesRegex(RuntimeError,'partial'):
            self.manager.start('camera')
        spawn.assert_not_called()
    def test_existing_camera_reused(self):
        self.graph=graph({'/camera/rgb/image_raw':['/camera/driver'],'/darknet_ros/detection_image':['/darknet_ros']})
        self.assertEqual(self.manager.start('camera')['action'],'reused')
    def test_camera_launch_is_fixed_detached_and_identity_recorded(self):
        record={'pid':2345,'argv':['python','/opt/ros/melodic/bin/roslaunch','darknet_ros','yolo_v3.launch'],'start':'987','group':2345}
        with mock.patch.object(agent.subprocess,'Popen',return_value=mock.Mock(pid=2345)) as spawn, mock.patch.object(agent.os,'setsid',create=True), mock.patch.object(agent,'process_info',return_value=record):
            result=self.manager.start('camera')
            args,kwargs=spawn.call_args
            self.assertEqual(args[0],['roslaunch','darknet_ros','yolo_v3.launch'])
            self.assertTrue(kwargs['close_fds']);self.assertIs(kwargs['preexec_fn'],agent.os.setsid)
            self.assertEqual(kwargs['stderr'],agent.subprocess.STDOUT)
        self.assertEqual(result['pid'],2345);self.assertEqual(self.manager.read_state()['camera'],record)
    def test_one_scan_publisher_reused_and_two_refused(self):
        self.graph=graph({'/scan':['/lsn10']});self.assertEqual(self.manager.start('lidar')['action'],'reused')
        self.graph=graph({'/scan':['/lsn10','/other']})
        with self.assertRaisesRegex(RuntimeError,'conflicting'):self.manager.start('lidar')
    def test_unregistered_lidar_process_is_not_duplicated(self):
        self.processes=[{'pid':10,'argv':['/path/lsn10'],'start':'20','group':10}]
        with self.assertRaisesRegex(RuntimeError,'partial'):self.manager.start('lidar')
    def test_missing_master_prevents_base_or_lidar_launch(self):
        self.graph=graph(reachable=False)
        for name in ('lidar','base','dashboard'):
            with self.assertRaisesRegex(RuntimeError,'master'):self.manager.start(name)
    def test_conflicting_base_and_other_command_publishers_not_reused(self):
        self.graph=graph({'/odom':[agent.BASE],'/cmd_vel':['/teleop']},{agent.COMMAND:[agent.BASE]},[agent.BASE])
        with self.assertRaisesRegex(RuntimeError,'conflicting'):self.manager.start('base')
    def test_other_velocity_subscription_or_publisher_not_considered_ready(self):
        for pubs,subs in [({'/odom':[agent.BASE]},{agent.COMMAND:[agent.BASE],'/other/cmd_vel':[agent.BASE]}),
                          ({'/odom':[agent.BASE],agent.COMMAND:['/another_controller']},{agent.COMMAND:[agent.BASE]})]:
            self.graph=graph(pubs,subs,[agent.BASE]);self.assertEqual(self.manager.status()['services']['base'],'conflict')
    def test_known_isolated_base_is_reused_without_driver_restart(self):
        self.graph=graph({'/odom':[agent.BASE],agent.COMMAND:['/fahad_dashboard_reader_123']},{agent.COMMAND:[agent.BASE]},[agent.BASE])
        self.assertEqual(self.manager.start('base')['action'],'reused')
    def test_unknown_service_and_shell_injection_refused(self):
        for name in ('all','camera; reboot','../base','shutdown',None):
            with self.assertRaises(RuntimeError):self.manager.start(name)
    def test_incomplete_runtime_not_started(self):
        with self.assertRaisesRegex(RuntimeError,'Runtime'):self.manager.start('base')
    def test_complete_bundle_installs_checksums_and_preserves_extra_files(self):
        self.stage();runtime=Path(self.manager.runtime);runtime.mkdir();(runtime/'user-notes.txt').write_text('preserve')
        result=self.manager.deploy('a'*32);self.assertTrue(result['verified']);self.assertEqual((runtime/'user-notes.txt').read_text(),'preserve')
        self.assertTrue(self.manager.runtime_matches());self.assertEqual(self.manager.status()['installed_bundle'],json.loads((runtime/'hub_manifest.json').read_text())['bundle_id'])
    def test_existing_runtime_files_are_backed_up(self):
        self.stage();self.manager.deploy('a'*32);before=(Path(self.manager.runtime)/'server.py').read_bytes()
        self.stage('b'*32,b'second');result=self.manager.deploy('b'*32)
        self.assertEqual((Path(result['backup'])/'server.py').read_bytes(),before)
    def test_modified_runtime_manifest_not_claimed_current(self):
        self.stage();self.manager.deploy('a'*32);(Path(self.manager.runtime)/'server.py').write_text('modified')
        self.assertFalse(self.manager.runtime_matches())
    def test_interrupted_update_blocks_managed_runtime_start(self):
        self.stage();self.manager.deploy('a'*32)
        self.stage('b'*32,b'second')
        replace=agent.atomic_replace;counter=[0]
        def interrupted(source,target):
            counter[0]+=1
            if counter[0]==2:raise OSError('simulated interrupted copy')
            return replace(source,target)
        with mock.patch.object(agent,'atomic_replace',side_effect=interrupted),self.assertRaises(OSError):self.manager.deploy('b'*32)
        self.assertFalse(self.manager.runtime_matches())
        with self.assertRaisesRegex(RuntimeError,'Runtime'):self.manager.start('base')
    def test_wrong_hash_missing_files_or_path_traversal_refused(self):
        stage,manifest=self.stage();(stage/'server.py').write_text('bad')
        with self.assertRaisesRegex(RuntimeError,'checksum'):self.manager.deploy('a'*32)
        with self.assertRaisesRegex(RuntimeError,'identity'):self.manager.deploy('../../other')
        with self.assertRaisesRegex(RuntimeError,'outside'):self.manager.safe(str(self.root.parent/'outside'))
    def test_manifest_cannot_choose_extra_target_paths(self):
        stage,manifest=self.stage();manifest['files']['../../outside']='x';manifest['bundle_id']=agent.bundle_id(manifest['files']);(stage/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(RuntimeError,'bundle'):self.manager.deploy('a'*32)
    def test_symlink_target_refused(self):
        try:(self.root/'remote_dashboard_web_trial').symlink_to(self.root,target_is_directory=True)
        except OSError:self.skipTest('Windows symlink privilege unavailable')
        self.stage()
        with self.assertRaisesRegex(RuntimeError,'symlinks'):self.manager.deploy('a'*32)
    def candidate(self):
        return {'pid':2345,'argv':['python','-u',str(Path(self.manager.runtime)/'server.py'),'--ros','--drive'],'start':'42','group':2345}
    def test_running_dashboard_never_overwritten_by_deploy(self):
        self.stage();self.processes=[self.candidate()]
        with self.assertRaisesRegex(RuntimeError,'running'):self.manager.deploy('a'*32)
    def test_active_faulted_or_unready_drive_not_restarted(self):
        self.processes=[self.candidate()]
        for control in ({'armed':True,'stage':'holding','ready':False},{'armed':False,'stage':'disabled','ready':True,'zero_failures':1},{'armed':False,'stage':'disabled','ready':False}):
            self.dashboard={'motor_output':True,'control':control}
            with mock.patch.object(agent.os,'kill') as kill,self.assertRaises(RuntimeError):self.manager.prepare_update()
            kill.assert_not_called()
    def test_normal_update_only_terms_exact_identified_dashboard(self):
        candidate=self.candidate();self.processes=[candidate]
        self.dashboard={'motor_output':True,'control':{'armed':False,'stage':'disabled','ready':True}}
        with mock.patch.object(self.manager,'dashboard_processes',side_effect=[[candidate],[],[]]),mock.patch.object(agent,'process_info',return_value=candidate),mock.patch.object(agent,'stop_drive') as stop,mock.patch.object(agent.os,'kill') as kill,mock.patch.object(agent.socket,'create_connection',side_effect=OSError):
            self.assertTrue(self.manager.prepare_update()['ready'])
        stop.assert_called_once();kill.assert_called_once_with(2345,signal.SIGTERM)
    def test_changed_pid_identity_is_not_killed(self):
        candidate=self.candidate();self.processes=[candidate]
        self.dashboard={'motor_output':False,'control':{}}
        with mock.patch.object(agent,'process_info',return_value=dict(candidate,start='different')),mock.patch.object(agent.os,'kill') as kill,self.assertRaisesRegex(RuntimeError,'identity'):
            self.manager.prepare_update()
        kill.assert_not_called()
    def test_unrelated_listener_never_killed(self):
        with mock.patch.object(agent.socket,'create_connection') as socket,mock.patch.object(agent.os,'kill') as kill,self.assertRaisesRegex(RuntimeError,'occupied'):
            self.manager.prepare_update()
        kill.assert_not_called();socket.return_value.close.assert_called_once()
    def test_only_stop_endpoint_used_no_arm_or_motion(self):
        with mock.patch.object(agent,'http_json',side_effect=[{'key':'test-only-key'},{'armed':False}]) as call:
            self.assertFalse(agent.stop_drive()['armed'])
        self.assertEqual(call.call_args_list,[mock.call('/api/bootstrap'),mock.call('/api/drive/stop',{},'test-only-key')])
    def test_agent_python36_syntax_and_no_motion_publisher(self):
        tree=ast.parse(Path(agent.__file__).read_text(encoding='utf8'),feature_version=(3,6))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='Publisher' for n in ast.walk(tree)))


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.connection=DemoConnection();self.log=[];self.cancel=threading.Event()
        self.controller=connection.HubController(self.connection,SOURCE,self.log.append,self.cancel)
    def test_prepare_starts_fixed_services_without_arming_or_browser(self):
        with mock.patch.object(self.connection,'rpc',wraps=self.connection.rpc) as rpc:
            result=self.controller.prepare()
        self.assertEqual(set(result['services'].values()),{'ready'});self.assertFalse(result['dashboard']['control']['armed'])
        self.assertEqual([c.args[1] for c in rpc.call_args_list if c.args[0]=='start'],['camera','lidar','base','dashboard'])
        self.assertFalse(any(c.args[0] in ('arm','command','drive') for c in rpc.call_args_list))
    def test_second_prepare_reuses_without_reinstall(self):
        self.controller.prepare()
        with mock.patch.object(self.connection,'install_runtime',wraps=self.connection.install_runtime) as install:
            self.controller.prepare()
        install.assert_not_called();self.assertTrue(any('reused' in text for text in self.log))
    def test_check_alone_never_starts_or_installs(self):
        with mock.patch.object(self.connection,'install_runtime') as install:
            status=self.controller.check()
        self.assertEqual(set(status['services'].values()),{'stopped'});install.assert_not_called()
    def test_cancel_before_start_starts_nothing(self):
        self.cancel.set()
        with mock.patch.object(self.connection,'rpc',wraps=self.connection.rpc) as rpc,self.assertRaisesRegex(RuntimeError,'cancelled'):
            self.controller.prepare()
        self.assertFalse(any(c.args[0]=='start' for c in rpc.call_args_list))
    def test_unhealthy_external_registration_refused_without_retry(self):
        self.connection.rpc=mock.Mock(side_effect=lambda action,value=None: {'action':'reused'} if action=='start' else {'services':{'camera':'partial'},'runtime_ok':False,'owned':{}})
        with self.assertRaisesRegex(RuntimeError,'external'):self.controller.prepare()
        self.assertEqual([c.args[0] for c in self.connection.rpc.call_args_list].count('start'),1)
    def test_source_bundle_changes_are_detected_not_just_version(self):
        manifest=connection.local_manifest(SOURCE);self.assertEqual(manifest['version'],'0.16');self.assertEqual(len(manifest['files']),22)
        changed=dict(manifest['files']);changed['server.py']='f'*64
        self.assertNotEqual(manifest['bundle_id'],agent.bundle_id(changed))
    def test_demo_never_creates_real_ssh_or_tunnel(self):
        with mock.patch.object(connection,'RobotConnection') as real:
            self.controller.prepare()
        real.assert_not_called();self.assertEqual(self.controller.url,'DEMO_NO_ROBOT')
    def test_prepare_progress_reports_stages_without_fake_percentage(self):
        phases=[];self.controller.progress=phases.append;self.controller.prepare()
        self.assertIn('Checking / starting camera',phases);self.assertIn('Opening private dashboard tunnel',phases)
        self.assertTrue(all('%' not in phase for phase in phases))


class HubProgressTests(unittest.TestCase):
    def app(self):
        app=App.__new__(App);app.busy=False;app.closing=False;app.cancelled=threading.Event()
        app.root=mock.Mock();app.progress=mock.Mock();app.progress_text=mock.Mock();app.events=queue.Queue()
        app.task_generation=0;app.show_progress=False;app._buttons=mock.Mock()
        return app
    def test_user_task_starts_animation_and_queues_completion(self):
        app=self.app();done=threading.Event()
        app.run(lambda:done.set(),'Connecting to robot');self.assertTrue(done.wait(1))
        app.progress.start.assert_called_once();self.assertTrue(app.busy)
        self.assertIn('Connecting to robot',app.progress_text.configure.call_args.kwargs['text'])
        self.assertEqual(app.events.get(timeout=1),('done',None))
    def test_background_check_has_no_spinner_and_busy_does_not_overlap(self):
        app=self.app();gate=threading.Event();app.run(lambda:gate.wait(1),show_progress=False)
        app.progress.start.assert_not_called();app.run(mock.Mock(),'second')
        self.assertEqual(app.task_generation,1);gate.set()
    def test_old_progress_callback_cannot_restart_after_new_task(self):
        app=self.app();app.busy=True;app.show_progress=True;app.task_generation=2;app.task_started=0
        app._progress_tick(1);app.root.after.assert_not_called()


class TransportGuards(unittest.TestCase):
    def test_only_private_ipv4_and_valid_port(self):
        for host in ('example.com','8.8.8.8','::1','192.168.0.100;reboot'):
            with self.assertRaises(ValueError):connection.RobotConnection(host)
        for port in (True,0,65536,'22'):
            with self.assertRaises(ValueError):connection.RobotConnection(ssh_port=port)
    def test_invalid_actions_rejected_before_ssh(self):
        robot=connection.RobotConnection()
        for action,value in [('shell',None),('start','lidar;reboot'),('logs','../../file'),('deploy','../../folder'),('status','extra')]:
            with self.assertRaises(ValueError):robot.rpc(action,value)
    def test_upload_cannot_leave_hub_folder(self):
        with self.assertRaises(RuntimeError):connection.RobotConnection._upload(mock.Mock(),b'code','/etc/config')
    def test_sftp_symlink_directory_refused(self):
        fake=mock.Mock();fake.lstat.return_value.st_mode=0o120777
        with self.assertRaisesRegex(RuntimeError,'ordinary directory'):connection.RobotConnection._mkdir(fake,'/home/wheeltec/fahad/robot_hub')
        fake.mkdir.assert_not_called()
    def test_sftp_atomic_replace_does_not_unlink_existing_target(self):
        fake=mock.MagicMock();fake.lstat.return_value.st_mode=0o40700
        connection.RobotConnection._upload(fake,b'code','/home/wheeltec/fahad/robot_hub/agent.py')
        fake.posix_rename.assert_called_once();fake.remove.assert_not_called()


class ModularBundleTests(unittest.TestCase):
    def test_controller_and_manifest_are_compatibility_exports(self):
        import hub_controller
        import runtime_bundle
        self.assertIs(connection.HubController,hub_controller.HubController)
        self.assertIs(connection.local_manifest,runtime_bundle.local_manifest)

    def test_full_runtime_imports_in_isolation_and_contains_all_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in agent.RUNTIME_FILES:
                target=Path(folder)/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(connection.source_file(SOURCE,name),target)
            code="import sys;sys.path.insert(0,sys.argv[1]);import server,settings,sensor_state,ros_reader;assert settings.VERSION==sys.argv[2];assert server.Dashboard is sensor_state.Dashboard;assert 'rospy' not in sys.modules;assert 'cv2' not in sys.modules;assert not server.Dashboard().status()['motor_output'];from pathlib import Path;assert all((Path(sys.argv[1])/'dist'/entry[0]).is_file() for entry in settings.ASSETS.values())"
            subprocess.run([sys.executable,'-I','-c',code,folder,agent.VERSION],check=True,capture_output=True)
        self.assertEqual(set(connection.local_manifest(SOURCE)['files']),set(agent.RUNTIME_FILES))


if __name__=='__main__':unittest.main()
