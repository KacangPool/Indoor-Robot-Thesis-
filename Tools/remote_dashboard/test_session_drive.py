"""Persistent session tests: fake clock/ROS and laptop loopback only."""
import json
import unittest
import manual_drive as drive
import test_manual_drive as base


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.clock=base.Clock();self.sent=[];self.issue=None;self.stationary=True
        self.control=drive.ManualSession(lambda moving:self.issue,self.emit,lambda since:self.stationary,self.clock)
        self.token=self.control.arm(base.OWNER);self.sequence=0
    def emit(self,v,w):self.sent.append((self.clock(),v,w))
    def command(self,action='neutral',motion=0,**axes):
        self.sequence+=1
        return self.control.command(base.OWNER,self.token,self.sequence,action,motion=motion,**axes)
    def wait(self,seconds,motion=1):
        for unused in range(round(seconds/.02)):
            self.clock.wait(.02)
            if self.control.stage in ('armed','holding','braking'):self.command('neutral',motion)
            self.control.tick()
    def start(self,action='forward',motion=1):
        self.command(action,motion);self.control.tick()

    def test_same_session_after_release_and_fresh_press(self):
        self.start();self.command('neutral',1);self.control.tick()
        self.assertEqual(self.sent[-1][1:],(0,0));self.assertEqual(self.control.stage,'braking')
        self.wait(.2);self.assertEqual(self.control.stage,'armed');self.assertEqual(self.control.generation,self.token)
        self.start('reverse_right',2);self.assertEqual(self.sent[-1][1:],(-.03,.03))

    def test_first_disable_reason_survives_repeated_stop_and_reenable(self):
        self.start();self.issue='Odometry stale';self.control.tick()
        event=dict(self.control.snapshot()['last_disable'])
        self.assertEqual(event['reason'],'Odometry stale');self.assertEqual(event['requested_linear_m_s'],.03)
        self.control.stop();self.control.tick();self.assertEqual(self.control.snapshot()['last_disable'],event)
        self.issue=None;self.wait(2.1);self.token=self.control.arm(base.OWNER)
        self.assertEqual(self.control.snapshot()['last_disable'],event)

    def test_idle_disable_reason_not_erased_by_operator_stop(self):
        self.clock.wait(.36);self.control.tick()
        event=dict(self.control.snapshot()['last_disable']);self.control.stop()
        self.assertEqual(self.control.snapshot()['last_disable'],event)
        self.assertIn('heartbeat',event['reason'])

    def test_disable_event_history_bounded_and_contains_no_owner_tokens(self):
        for index in range(25):
            self.control.stop('test '+str(index));self.token=self.control.arm(base.OWNER)
        state=self.control.snapshot();self.assertEqual(len(state['disable_events']),20)
        self.assertEqual(state['last_disable']['id'],25)
        self.assertNotIn(base.OWNER,json.dumps(state['disable_events']))

    def test_healthy_hold_continues_beyond_two_seconds(self):
        self.start()
        for unused in range(750):
            self.clock.wait(.02);self.command('forward',1);self.control.tick()
        self.assertEqual(self.control.stage,'holding');self.assertTrue(self.control.snapshot()['armed'])
        self.assertIsNone(self.control.snapshot()['max_hold_s']);self.assertGreater(len(self.sent),100)
        self.assertTrue(all(v==.03 and w==0 for t,v,w in self.sent))

    def test_separate_travel_stays_constant_through_steering_and_brake(self):
        throttle=.12+.88*.06/.30
        for steering in (-1,-.5,0,.5,1):
            self.clock.wait(.1);self.command('joystick',1,throttle=throttle,steering=steering);self.control.tick()
            self.assertAlmostEqual(self.sent[-1][1],.06)
            self.assertLessEqual(abs(self.sent[-1][2]),.06+1e-12)
        self.command('neutral',1);self.control.tick();self.assertEqual(self.sent[-1][1:],(0,0));self.wait(.2)
        with self.assertRaises(ValueError):self.command('joystick',1,throttle=-throttle,steering=1)
        self.command('joystick',2,throttle=-throttle,steering=1);self.control.tick();self.assertAlmostEqual(self.sent[-1][1],-.06)

    def test_release_before_first_worker_never_outputs_nonzero(self):
        self.command('forward',1);self.command('neutral',1);self.control.tick()
        self.assertTrue(all(v==w==0 for t,v,w in self.sent))

    def test_delayed_old_sequence_cannot_undo_release(self):
        self.start();self.control.command(base.OWNER,self.token,99,'neutral',motion=1)
        with self.assertRaises(ValueError):self.control.command(base.OWNER,self.token,98,'forward',motion=1)
        self.control.tick();self.assertEqual(self.sent[-1][1:],(0,0))

    def test_released_motion_cannot_resume_with_new_sequence(self):
        self.start();self.command('neutral',1);self.wait(.2)
        with self.assertRaises(ValueError):self.command('forward',1)
        self.control.tick();self.assertEqual(self.control.stage,'armed');self.assertEqual(self.sent[-1][1:],(0,0))

    def test_press_during_braking_is_not_queued(self):
        self.start();self.command('neutral',1);self.command('reverse',2);self.control.tick();self.wait(.2,2)
        with self.assertRaises(ValueError):self.command('reverse',2)
        self.assertEqual(self.control.stage,'armed');self.start('reverse',3);self.assertEqual(self.sent[-1][1:],(-.03,0))

    def test_no_automatic_resume_after_braking(self):
        self.start();self.command('neutral',1);self.wait(.5)
        self.assertEqual(self.control.stage,'armed');self.assertEqual(len([v for t,v,w in self.sent if v]),1)

    def test_reversing_or_crossing_joystick_centre_requires_new_press(self):
        for action,axes in [('reverse',{}),('joystick',{'throttle':0,'steering':1})]:
            self.setUp();self.start();self.command(action,1,**axes);self.control.tick()
            self.assertEqual(self.control.stage,'braking');self.assertEqual(self.sent[-1][1:],(0,0));self.wait(.2)
            with self.assertRaises(ValueError):self.command('reverse',1)

    def test_initial_joystick_centre_does_not_retire_press(self):
        self.command('joystick',1,throttle=0,steering=0);self.control.tick();self.assertEqual(self.sent,[])
        self.command('joystick',1,throttle=1,steering=-1);self.control.tick();self.assertEqual(self.sent[-1][1:],(.30,.30))

    def test_neutral_idle_does_not_publish(self):
        self.wait(3,0);self.assertEqual(self.sent,[])

    def test_axes_and_motion_validation_do_not_renew_lease(self):
        for bad in (None,True,-1,1.5,'1',2147483648):
            with self.assertRaises(ValueError):self.command('forward',bad)
        with self.assertRaises(ValueError):self.command('joystick',1,throttle=2,steering=0)
        self.clock.wait(.36);self.control.tick();self.assertFalse(self.control.snapshot()['armed']);self.assertEqual(self.sent,[])

    def test_stop_or_lease_fault_requires_new_enable(self):
        for fault in ('stop','lease','camera','gap'):
            self.setUp();self.start()
            if fault=='stop':self.control.stop()
            elif fault=='camera':self.issue='Camera stale'
            elif fault=='gap':self.clock.wait(.3);self.command('forward',1)
            else:self.clock.wait(.36)
            self.control.tick();self.assertFalse(self.control.snapshot()['armed']);self.assertEqual(self.sent[-1][1:],(0,0))
            with self.assertRaises(ValueError):self.command('forward',2)

    def test_fault_during_normal_braking_disables_and_sends_zero_tail(self):
        self.start();self.command('neutral',1);self.issue='Odometry lost';self.control.tick()
        self.assertEqual(self.control.stage,'stopping');self.assertIsNone(self.control.generation);self.assertEqual(self.sent[-1][1:],(0,0))

    def test_stop_during_braking_retires_session(self):
        self.start();self.command('neutral',1);self.control.stop();self.control.tick()
        self.assertEqual(self.control.stage,'stopping');self.assertFalse(self.control.snapshot()['armed'])

    def test_stationary_feedback_timeout_disables_session(self):
        self.start();self.stationary=False;self.command('neutral',1);self.wait(2.1)
        self.assertEqual(self.control.stage,'stopping');self.assertIn('Stationary feedback',self.control.reason)

    def test_failed_zero_never_returns_to_idle_ready(self):
        self.start();self.command('neutral',1)
        def fail(v,w):raise RuntimeError('fake zero failure')
        self.control.emit=fail;self.control.tick();self.assertEqual(self.control.stage,'stopping');self.assertGreater(self.control.zero_failures,0)
        for unused in range(110):self.clock.wait(.02);self.control.tick()
        with self.assertRaises(ValueError):self.control.arm(base.OWNER)

    def test_old_or_wrong_owner_generation_cannot_drive(self):
        for owner,token in [('b'*32,self.token),(base.OWNER,'wrong')]:
            with self.assertRaises(ValueError):self.control.command(owner,token,1,'forward',motion=1)
        self.assertEqual(self.sent,[])

    def test_braking_lease_is_required(self):
        self.start();self.command('neutral',1);self.clock.wait(.36);self.control.tick()
        self.assertEqual(self.control.stage,'stopping');self.assertIn('heartbeat',self.control.reason)

    def test_steering_updates_do_not_drop_a_healthy_hold(self):
        self.start()
        for action in ('forward_left','forward_right','forward'):
            self.clock.wait(.1);self.command(action,1);self.control.tick()
            self.assertEqual(self.sent[-1][1:],drive.requested_twist(action))

    def test_schema_reports_session_and_motion_state(self):
        state=self.control.snapshot();self.assertTrue(state['session_persistent']);self.assertTrue(state['motion_ready'])
        self.start();state=self.control.snapshot();self.assertEqual(state['active_motion'],1);self.assertFalse(state['motion_ready'])

    def test_repeated_stop_preserves_fault_reason(self):
        self.start();self.issue='Camera stale';self.control.tick();self.control.stop('Browser cleanup')
        self.assertEqual(self.control.reason,'Camera stale')

    def test_stationary_samples_must_be_after_release(self):
        feedback=drive.ManualFeedback(self.clock);stamp=1000.
        def sample():
            nonlocal stamp
            self.clock.wait(.01);stamp+=.01;feedback.graph(None)
            feedback.observe(drive.crawl.BASE,stamp,stamp,(0,0,0))
        for unused in range(3):sample()
        self.control=drive.ManualSession(feedback.problem,self.emit,feedback.stopped_since,self.clock)
        self.token=self.control.arm(base.OWNER);self.sequence=0;self.start();self.command('neutral',1);self.control.tick()
        self.clock.wait(.16);self.command('neutral',1);self.control.tick()
        self.assertEqual(self.control.stage,'braking')
        for unused in range(2):sample();self.command('neutral',1);self.control.tick()
        self.assertEqual(self.control.stage,'braking')
        sample();self.command('neutral',1);self.control.tick();self.assertEqual(self.control.stage,'armed')

    def test_new_enable_after_full_stop_uses_new_generation(self):
        self.start();self.control.stop()
        for unused in range(110):self.clock.wait(.02);self.control.tick()
        token=self.control.arm(base.OWNER);self.assertNotEqual(token,self.token)
        with self.assertRaises(ValueError):self.command('forward',2)

    def test_slow_health_before_zero_return_does_not_resume(self):
        self.start();self.command('neutral',1)
        def delayed(moving):
            self.clock.wait(.4)
            return None
        self.control.health=delayed;self.control.tick()
        self.assertFalse(self.control.snapshot()['armed']);self.assertTrue(all(v==w==0 for t,v,w in self.sent[1:]))


class HttpTests(base.HttpTests):
    def setUp(self):
        base.HttpTests.setUp(self);self.app.mode='ros_manual_ackermann'
        self.clock=base.Clock()
        self.app.control=drive.ManualSession(lambda moving:None,lambda v,w:self.sent.append((v,w)),lambda since:True,self.clock)
    def test_live_mode_is_explicit_in_status(self):
        state=json.loads(self.fetch('/api/status')[1]);self.assertEqual(state['version'],'0.17');self.assertTrue(state['control']['session_persistent'])
    def test_expired_command_response_includes_backend_fault_without_token(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        self.clock.wait(.36)
        code,raw=self.fetch('/api/drive/command',{'owner':base.OWNER,'generation':token,'sequence':1,'action':'forward','motion':1})
        data=json.loads(raw);self.assertEqual(code,400);self.assertIn('heartbeat',data['control']['last_disable']['reason'])
        self.assertNotIn(token,raw.decode());self.assertNotIn(self.app.key,raw.decode());self.assertEqual(self.sent,[])
    def test_arm_command_stop_keeps_publication_in_worker(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        body={'owner':base.OWNER,'generation':token,'sequence':1,'action':'forward','motion':1}
        self.assertEqual(self.fetch('/api/drive/command',body)[0],200);self.assertEqual(self.sent,[])
        self.app.control.tick();self.assertEqual(self.sent,[(.03,0)])
        body.update(sequence=2,action='neutral');self.assertEqual(self.fetch('/api/drive/command',body)[0],200)
        self.app.control.tick();self.assertEqual(self.sent[-1],(0,0));self.assertEqual(self.app.control.generation,token)
        self.fetch('/api/drive/stop',{});self.assertIsNone(self.app.control.generation)
    def test_missing_motion_from_old_page_cannot_drive(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        self.assertEqual(self.fetch('/api/drive/command',{'owner':base.OWNER,'generation':token,'sequence':1,'action':'forward'})[0],400);self.assertEqual(self.sent,[])

    def test_stale_or_other_owner_cleanup_cannot_stop_current_generation(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        self.fetch('/api/drive/stop',{'owner':'b'*32,'generation':token})
        self.assertTrue(self.app.control.snapshot()['armed'])
        self.fetch('/api/drive/stop',{'owner':base.OWNER,'generation':'old-generation'})
        self.assertTrue(self.app.control.snapshot()['armed'])
        self.fetch('/api/drive/stop',{'owner':base.OWNER,'generation':token})
        self.assertFalse(self.app.control.snapshot()['armed'])

    def test_owner_only_pending_arm_cleanup_and_explicit_global_stop(self):
        self.fetch('/api/drive/arm',{'owner':base.OWNER})
        self.fetch('/api/drive/stop',{'owner':base.OWNER,'generation':None})
        self.assertFalse(self.app.control.snapshot()['armed'])
        self.fetch('/api/drive/arm',{'owner':base.OWNER})
        self.fetch('/api/drive/stop',{})
        self.assertFalse(self.app.control.snapshot()['armed'])

    def test_http_cannot_override_joystick_ceiling(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        body={'owner':base.OWNER,'generation':token,'sequence':1,'action':'joystick','motion':1,
              'throttle':1,'steering':1,'joystick_speed':999,'max_speed':999}
        self.assertEqual(self.fetch('/api/drive/command',body)[0],200);self.assertEqual(self.sent,[])
        self.app.control.tick();self.assertEqual(self.sent[-1],(.30,-.30))

    def test_http_long_hold_release_and_reverse_without_reenable(self):
        token=json.loads(self.fetch('/api/drive/arm',{'owner':base.OWNER})[1])['generation']
        body={'owner':base.OWNER,'generation':token,'sequence':0,'action':'forward_left','motion':1}
        for unused in range(61):
            body['sequence']+=1;self.clock.wait(.1)
            self.assertEqual(self.fetch('/api/drive/command',body)[0],200);self.app.control.tick()
        self.assertEqual(self.app.control.stage,'holding');self.assertEqual(self.sent[-1],(.03,.03))
        body.update(sequence=62,action='neutral');self.fetch('/api/drive/command',body);self.app.control.tick()
        self.assertEqual(self.sent[-1],(0,0));self.clock.wait(.2);body['sequence']=63;self.fetch('/api/drive/command',body);self.app.control.tick()
        body.update(sequence=64,action='reverse',motion=2);self.assertEqual(self.fetch('/api/drive/command',body)[0],200);self.app.control.tick()
        self.assertEqual(self.sent[-1],(-.03,0));self.assertEqual(self.app.control.generation,token)


if __name__=='__main__':unittest.main()
