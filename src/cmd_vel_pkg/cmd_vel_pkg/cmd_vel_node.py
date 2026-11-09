import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float64


class CmdVelMultiplier(Node):
    """Subscribe to a Twist topic and publish a scaled copy."""

    def __init__(self):
        super().__init__("cmd_vel_multiplier")

        self.declare_parameter("input_topic", "/cmd_vel_nav")
        
        self.declare_parameter("output_thrust_left", "/wamv/thrusters/left/thrust")
        self.declare_parameter("output_thrust_right", "/wamv/thrusters/right/thrust")

        self.declare_parameter("output_pos_left", "/wamv/thrusters/left/pos")
        self.declare_parameter("output_pos_right", "/wamv/thrusters/right/pos")


        self.declare_parameter("multiplier", 2.0)

        input_topic = self.get_parameter("input_topic").value

        output_thrust_left = self.get_parameter("output_thrust_left").value
        output_thrust_right = self.get_parameter("output_thrust_right").value

        output_pos_left = self.get_parameter("output_pos_left").value
        output_pos_right = self.get_parameter("output_pos_right").value
        

        self.multiplier = float(self.get_parameter("multiplier").value)

        self.publisher_thrust_left = self.create_publisher(Float64, output_thrust_left, 10)
        self.publisher_thrust_right = self.create_publisher(Float64, output_thrust_right, 10)

        self.publisher_pos_left = self.create_publisher(Float64, output_pos_left, 10)
        self.publisher_pos_right = self.create_publisher(Float64, output_pos_right, 10)
        
        self.subscription = self.create_subscription(
            TwistStamped, input_topic, self.cmd_vel_callback, 10
        )

        self.get_logger().info(
            f"Scaling Twist messages from '{input_topic}' to "
            f"'{output_thrust_left}' by {self.multiplier:g}"
        )

    def cmd_vel_callback(self, msg: TwistStamped) -> None:

        left_thrust = Float64()
        right_thrust = Float64()

        left_pos= Float64()
        right_pos = Float64()

        left_thrust.data = 500.0
        right_thrust.data = 500.0

        left_pos.data = 0.5
        right_pos.data = 0.5

        self.publisher_thrust_left.publish(left_thrust)
        self.publisher_thrust_right.publish(right_thrust)

        scaled = TwistStamped()

        # Scale all six components of geometry_msgs/msg/TwistStamped.
        scaled.twist.linear.x = msg.twist.linear.x * self.multiplier
        scaled.twist.linear.y = msg.twist.linear.y * self.multiplier
        scaled.twist.linear.z = msg.twist.linear.z * self.multiplier

        scaled.twist.angular.x = msg.twist.angular.x * self.multiplier
        scaled.twist.angular.y = msg.twist.angular.y * self.multiplier
        scaled.twist.angular.z = msg.twist.angular.z * self.multiplier

        self.publisher_pos_left.publish(left_pos)
        self.publisher_pos_right.publish(right_pos)


def main(args=None):
    print ("Starting cmd_vel conversion!")
    rclpy.init(args=args)
    node = CmdVelMultiplier()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
