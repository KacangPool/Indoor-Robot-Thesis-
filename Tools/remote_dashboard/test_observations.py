"""Fake ROS camera-only inputs: no process, subscriber or movement."""
import unittest
from unittest.mock import Mock
from test_dashboard import Holder, Clock
import server


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.clock=Clock();self.app=server.Dashboard(ros=True,clock=self.clock)
        self.reader=server.RosReader.__new__(server.RosReader);self.reader.dashboard=self.app
        self.reader.rospy=Mock();self.reader.rospy.Time.now.return_value.to_sec.return_value=10.1
        self.message=Holder(image_header=Holder(seq=1,stamp=Holder(secs=10,nsecs=0),frame_id='rgb'),
            bounding_boxes=[Holder(Class='person',id=0,probability=.9,xmin=1,xmax=20,ymin=1,ymax=30)])
    def test_camera_only_retained_without_scan_or_tf_and_expires(self):
        self.reader.boxes_callback(self.message);value=self.app.status()['observations']
        self.assertTrue(value['available']);self.assertEqual(value['records'][0]['class'],'person')
        self.assertIsNone(value['records'][0]['position']);self.assertFalse(self.app.status()['motor_output'])
        self.clock.value+=2;self.assertFalse(self.app.status()['observations']['available'])
        self.assertEqual(self.app.status()['observations']['records'],[])
    def test_bad_source_invalidates_old_records(self):
        self.reader.boxes_callback(self.message);self.message.image_header.stamp.secs=1
        self.reader.boxes_callback(self.message)
        self.assertEqual(self.app.status()['observations']['records'],[])
        self.assertTrue(self.app.status()['observations']['error'])


if __name__=='__main__':unittest.main()
