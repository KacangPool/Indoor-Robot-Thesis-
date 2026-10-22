"""Ackermann mapping/lease/feedback/HTTP verification; fake output only."""
import math
import threading
import unittest
from unittest import mock
import manual_drive as drive
import crawl_test as crawl
import test_manual_drive as base


class MappingTests(unittest.TestCase):
    def test_six_direction_signs(self):
        expected={'forward':(.03,0),'forward_left':(.03,.03),'forward_right':(.03,-.03),
                  'reverse':(-.03,0),'reverse_left':(-.03,-.03),'reverse_right':(-.03,.03)}
        for action,value in expected.items(): self.assertEqual(drive.requested_twist(action),value)

    def test_joystick_deadzone_and_horizontal_only_have_no_yaw(self):
        for power in (0,.01,-.1,.12):
            self.assertEqual(drive.requested_twist('joystick',power,1),(0,0))

    def test_all_axes_are_bounded_and_curvature_coupled(self):
        for i in range(-20,21):
            for j in range(-20,21):
                speed,yaw=drive.requested_twist('joystick',i/20.,j/20.)
                self.assertLessEqual(abs(speed),.03);self.assertLessEqual(abs(yaw),abs(speed)*drive.MAX_CURVATURE+1e-12)
                if speed==0:self.assertEqual(yaw,0)

    def test_partial_throttle_is_slower(self):
        v,w=drive.requested_twist('joystick',.5,-.5)
        self.assertGreater(v,0);self.assertLess(v,.03);self.assertGreater(w,0)

    def test_invalid_axes_rejected(self):
        for bad in (None,True,False,'1',{},[],float('nan'),float('inf'),-1.01,1.01):
            for power,steering in ((bad,0),(0,bad)):
                with self.assertRaises(ValueError):drive.requested_twist('joystick',power,steering)

    def test_extra_axes_on_buttons_and_unimplemented_actions_rejected(self):
        with self.assertRaises(ValueError):drive.requested_twist('forward',1,0)
        for action in ('left','right','spin','sideways','cmd_vel',{},None):
            with self.assertRaises(ValueError):drive.requested_twist(action)


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.clock=base.Clock();self.sent=[];self.issue=None
        self.control=drive.ManualAckermann(lambda moving:self.issue,lambda v,w:self.sent.append((self.clock(),v,w)),lambda since:True,self.clock)
        self.owner=base.OWNER;self.token=self.control.arm(self.owner)
    def command(self,sequence,action,**axes):return self.control.command(self.owner,self.token,sequence,action,**axes)

    def test_each_button_requests_matching_vector_and_zero_tail(self):
        for action in drive.ACTIONS:
            self.setUp();self.command(1,action);self.control.tick()
            self.assertEqual(self.sent[0][1:],drive.requested_twist(action));self.control.stop();self.control.tick();self.assertEqual(self.sent[-1][1:],(0,0))

    def test_arbitrary_invalid_axes_do_not_refresh_lease(self):
        self.clock.wait(.2)
        with self.assertRaises(ValueError):self.command(1,'joystick',throttle=100,steering=0)
        self.clock.wait(.16);self.control.tick();self.assertFalse(self.control.snapshot()['armed']);self.assertEqual(self.sent,[])

    def test_steering_changes_do_not_reset_hold_limit(self):
        self.command(1,'joystick',throttle=1,steering=0);self.control.tick()
        for sequence in range(2,41):
            self.clock.wait(.05);self.command(sequence,'joystick',throttle=1,steering=(-1 if sequence%2 else 1));self.control.tick()
        self.clock.wait(.06);self.control.tick();self.assertFalse(self.control.snapshot()['armed']);self.assertTrue(all(t<102 for t,v,w in self.sent if v))

    def test_reverse_change_stops_and_retires_generation(self):
        self.command(1,'forward');self.control.tick();self.command(2,'reverse');self.control.tick()
        self.assertEqual(self.sent[-1][1:],(0,0));self.assertFalse(self.control.snapshot()['armed'])
        with self.assertRaises(ValueError):self.command(3,'reverse')
        self.assertTrue(all(v>=0 for t,v,w in self.sent))

    def test_joystick_centre_stops_existing_motion(self):
        self.command(1,'joystick',throttle=-1,steering=.5);self.control.tick();self.command(2,'joystick',throttle=0,steering=1);self.control.tick()
        self.assertEqual(self.sent[-1][1:],(0,0));self.assertFalse(self.control.snapshot()['armed'])

    def test_initial_centred_or_horizontal_joystick_never_publishes(self):
        self.command(1,'joystick',throttle=0,steering=1);self.control.tick();self.assertEqual(self.sent,[])

    def test_cancel_before_worker_prevents_delayed_reverse(self):
        self.command(1,'reverse_left');self.control.stop();self.control.tick();self.assertTrue(all(v==0 and w==0 for t,v,w in self.sent))

    def test_expired_lease_rejects_old_joystick(self):
        self.command(1,'joystick',throttle=1,steering=1);self.control.tick();self.clock.wait(.36);self.control.tick()
        with self.assertRaises(ValueError):self.command(2,'joystick',throttle=1,steering=1)
        self.assertEqual(self.sent[-1][1:],(0,0))

    def test_camera_failure_stops_both_components(self):
        self.command(1,'forward_left');self.control.tick();self.issue='Camera stale';self.control.tick();self.assertEqual(self.sent[-1][1:],(0,0))

    def test_status_advertises_capabilities_and_requested_not_measured_values(self):
        self.command(1,'reverse_right');state=self.control.snapshot();self.assertIn('joystick',state['allowed_actions']);self.assertEqual(state['requested_linear_m_s'],-.03);self.assertEqual(state['requested_yaw_rad_s'],.03)

    def test_browser_cleanup_does_not_hide_original_stop_reason(self):
        self.command(1,'forward');self.control.tick();self.control.stop('Camera stale')
        self.control.stop('Stopped by operator');self.assertEqual(self.control.reason,'Camera stale')


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.clock=base.Clock();self.feedback=drive.ManualFeedback(self.clock);self.feedback.graph(None);self.stamp=1000.
    def samples(self,velocity=(0,0,0),caller=crawl.BASE):
        for unused in range(3):
            self.clock.wait(.01);self.stamp+=.01;self.feedback.observe(caller,self.stamp,self.stamp,velocity)
    def test_signed_reverse_allowed_only_while_moving(self):
        self.samples((-.03,0,-.03));self.assertIsNone(self.feedback.problem(True));self.assertIsNotNone(self.feedback.problem(False))
    def test_old_forward_only_cli_guard_unchanged(self):
        old=crawl.Feedback(self.clock);old.graph(None)
        for offset in (1,2,3):old.observe(crawl.BASE,1000.+offset,1000.+offset,(-.03,0,0))
        self.assertIsNotNone(old.problem(True))
    def test_excess_speed_lateral_or_yaw_rejected(self):
        for velocity in ((-.121,0,0),(.121,0,0),(0,.05,0),(0,0,.16)):
            self.setUp();self.samples(velocity);self.assertIsNotNone(self.feedback.problem(True))
    def test_stale_feedback_and_graph_or_wrong_caller_rejected(self):
        self.samples();self.clock.wait(.51);self.feedback.graph(None);self.assertIsNotNone(self.feedback.problem(True))
        self.setUp();self.samples(caller='/fake');self.assertIsNotNone(self.feedback.problem(True))
        self.setUp();self.samples();self.feedback.graph('Other publisher');self.assertEqual(self.feedback.problem(True),'Other publisher')


class HttpTests(base.HttpTests):
    def setUp(self):
        base.HttpTests.setUp(self)
        self.app.mode='ros_manual_ackermann'
        self.app.control=drive.ManualAckermann(lambda moving:None,lambda v,w:self.sent.append((v,w)),lambda since:True)
    def test_live_mode_is_explicit_in_status(self):
        import json
        status=json.loads(self.fetch('/api/status')[1]);self.assertEqual(status['mode'],'ros_manual_ackermann');self.assertIn('reverse',status['control']['allowed_actions'])
    def test_arm_command_stop_keeps_publication_in_worker(self):
        import json
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        body={'owner':base.OWNER,'generation':token,'sequence':1,'action':'joystick','throttle':-.75,'steering':-.5}
        self.assertEqual(self.fetch('/api/drive/command',body)[0],200);self.assertEqual(self.sent,[])
        self.app.control.tick();self.assertEqual(self.sent[-1],drive.requested_twist('joystick',-.75,-.5))
        self.fetch('/api/drive/stop',{});self.app.control.tick();self.assertEqual(self.sent[-1],(0,0))
        body['sequence']=2;self.assertEqual(self.fetch('/api/drive/command',body)[0],400)
    def test_invalid_json_axis_cannot_publish(self):
        import json
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        for bad in (True,'1',[],{},2):
            body={'owner':base.OWNER,'generation':token,'sequence':1,'action':'joystick','throttle':bad,'steering':0}
            self.assertEqual(self.fetch('/api/drive/command',body)[0],400)
        self.assertEqual(self.sent,[])
    def test_new_assets_are_local_and_served(self):
        for path in ('/joystick.js','/controls.css'):
            code,body=self.fetch(path);self.assertEqual(code,200);self.assertNotIn(b'https://',body)


class AdapterTests(base.IntegrationTests):
    def test_new_adapter_emits_yaw_but_never_lateral_or_in_place(self):
        for action in drive.ACTIONS:
            app,ros,pub,adapter,feedback,monitor,thread=self.adapter()
            token=adapter.control.arm(base.OWNER);adapter.control.command(base.OWNER,token,1,action,motion=1);adapter.control.tick()
            message=pub.publish.call_args.args[0];self.assertEqual((message.linear.x,message.angular.z),drive.requested_twist(action))
            self.assertEqual((message.linear.y,message.linear.z,message.angular.x,message.angular.y),(0,0,0,0));adapter.close()
    def test_opposite_reported_direction_stops_before_output(self):
        app,ros,pub,adapter,feedback,monitor,thread=self.adapter()
        feedback.samples=[(app.clock(),(-.03,0,0))]
        token=adapter.control.arm(base.OWNER);adapter.control.command(base.OWNER,token,1,'forward',motion=1);adapter.control.tick()
        self.assertFalse(adapter.control.snapshot()['armed']);self.assertTrue(all(c.args[0].linear.x==0 for c in pub.publish.call_args_list));adapter.close()


if __name__=='__main__':unittest.main()
