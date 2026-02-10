import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class ArucoToTF(Node):
    def __init__(self):
        super().__init__('aruco_tf_publisher')
        self.br = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            PoseArray, '/aruco_poses', self.listener_callback, 10)

    def listener_callback(self, msg):
        if len(msg.poses) > 0:
            t = TransformStamped()
            t.header.stamp = t.header.stamp = msg.header.stamp
            t.header.frame_id = 'camera_color_optical_frame' 
            t.child_frame_id = 'marker_26'
            
            t.transform.translation.x = msg.poses[0].position.x
            t.transform.translation.y = msg.poses[0].position.y
            t.transform.translation.z = msg.poses[0].position.z
            t.transform.rotation = msg.poses[0].orientation
            
            self.br.sendTransform(t)

def main():
    rclpy.init()
    node = ArucoToTF()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()