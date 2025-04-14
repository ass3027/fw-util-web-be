import json
import pexpect
from main import Region, REGION_DICT


class SshConnector:
    def __init__(self, region: Region):
        self.region = region
        self.user = region.user
        self.pw = region.pw
        self.cmd_prefix = f"ssh -p {region.port} {region.user}@{region.ip} "

    def ssh_connect(self):
        child = pexpect.spawn(self.cmd_prefix)

        result = child.expect(pattern=[pexpect.TIMEOUT, "Are you sure you want to continue connecting (yes/no)?"],
                              timeout=2)
        if result == 1:
            child.sendline("yes")
        else:
            print("is already registered")

        child.expect("'s password: ")
        child.sendline(self.pw)
        child.expect(r'\$')

        return child


    def run(self, main_cmd):
        child = self.ssh_connect()

        try:
            child.sendline(main_cmd)
            # [sudo] password for {username} :
            if "sudo" in main_cmd:
                child.expect(f"password for {self.user}: ")
            child.sendline(self.pw)

            # after result printing, return to console
            child.expect(f'{self.user}@', 10)
            output = child.before.decode("utf-8")
        except Exception as e :
            print(main_cmd)
            raise e
        finally:
            child.close()

        return self.remove_escape_char(output)


    @staticmethod
    def remove_escape_char(output):
        if output[-14:] == "\r\n\x1b[?2004h\x1b]0;":
            output = output[:-14]
        elif output[-10:] == '\r\n\x1b[?2004h':
            output = output[:-10]
        elif output[-4:] == ']0;':
            output = output[:-4]
        return output

    def get_db_info(self):
        docker_exec_cmd = "sudo -S docker exec $(sudo -S docker ps -q --filter publish=27017) "
        mongo_cmd = "mongosh \"firewatcher_v2\" --eval 'db.cctvinfos.find().toArray()' --json"
        result = self.run(docker_exec_cmd + mongo_cmd)
        db_info = json.loads(result)

        result = []
        for info in sorted(db_info, key=lambda o: int(o['cctv_ID']['$numberInt'])):
            cctv_id = int(info['cctv_ID']['$numberInt'])
            info['cctv_ID'] = cctv_id
            result.append(info)
        return result


    def run_ffprobe(self, url):
        docker_exec_cmd = "sudo -S docker exec $(sudo -S docker ps -q --filter ancestor=firewatcher:v2.1) "
        ffprobe_cmd = f"ffprobe {url}"
        result = self.run(docker_exec_cmd + ffprobe_cmd)
        return result

    def get_milestone(self):
        docker_exec_cmd = "sudo -S docker logs $(sudo -S docker ps -q --filter ancestor=monowine_mipsdk_v1)"
        return self.run(docker_exec_cmd)


if __name__ == "__main__":
    _region = REGION_DICT["경남"]
    sc = SshConnector(_region)

    # _result = sc.run("sudo -S docker ps -a")
    # for line in _result:
    #     print(line)
    _result = sc.get_db_info()
    print(_result)

