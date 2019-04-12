class Tracker:
    def __init__(self, vr, trackerID):
        self.vr = vr
        self.trackerID = trackerID
        self.serial = self.vr.devices[self.trackerID].get_serial()
        pose = self.vr.devices[self.trackerID].get_pose_euler()
        self.x = pose[0]
        self.z = pose[1]
        self.y = pose[2]
        self.yaw = pose[3]
        self.pitch = pose[4]
        self.roll = pose[5]

    def update_position(self):
        pose = self.vr.devices[self.trackerID].get_pose_euler()
        self.x = pose[0]
        self.z = pose[1]
        self.y = pose[2]
        self.yaw = pose[3]
        self.pitch = pose[4]
        self.roll = pose[5]
