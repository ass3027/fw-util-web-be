import os
import pexpect
from main.region import Region, REGION_DICT


class ScpConnector:
    def __init__(self, region: Region):
        self.region = region
        self.pw = region.pw
        self.cmd_prefix = f"scp -P {region.port} {region.user}@{region.ip}:"

    def run(self, source, destination):
        cmd = f"{self.cmd_prefix}{source} {destination}"
        print(cmd)
        child = pexpect.spawn(cmd)

        result = child.expect(pattern=[pexpect.TIMEOUT, "Are you sure you want to continue connecting (yes/no)?"],
                              timeout=0.1)
        if result == 1:
            child.sendline("yes")
        else:
            print("is already registered")

        child.expect("'s password: ")
        child.sendline(self.pw)

        child.expect([pexpect.TIMEOUT,pexpect.EOF])
        child.close()

if __name__ == "__main__":
    _region = REGION_DICT["경남"]
    sc = ScpConnector(_region)
    _source = f"/home/workspace/logs/controller/2025-03-13_0.log"
    log_file_dir = os.path.join(os.path.dirname(__file__), f"log_files/{_region.id}")
    sc.run(_source, log_file_dir)
