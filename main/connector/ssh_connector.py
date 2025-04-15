import json
import pexpect
from main import Region, REGION_DICT


class SshConnector:
    COMMAND_PROMPT = '[#$] '
    TERMINAL_PROMPT = r'(?i)terminal type\?'
    TERMINAL_TYPE = 'vt100'
    SSH_NEW_KEY = '(?i)are you sure you want to continue connecting'
    PASSWORD = '(?i)password'
    def __init__(self, region: Region):
        self.region = region
        self.user = region.user
        self.pw = region.pw
        self.cmd_prefix = f"ssh -p {region.port} {region.user}@{region.ip} "

    def ssh_connect(self):
        child = pexpect.spawn(self.cmd_prefix)

        result = child.expect(pattern=[pexpect.TIMEOUT, self.SSH_NEW_KEY, self.COMMAND_PROMPT, self.PASSWORD],timeout=2)

        if result == 0: # timeout
            print('ERROR! could not login with SSH. Here is what SSH said:')
            print(child.before, child.after)
            print(str(child))
        elif result == 1: #password login
            child.sendline("yes")
            child.expect(self.PASSWORD)
        elif result == 2: # key login pass
            pass
        elif result == 3:
            child.sendline(self.pw)
            i = child.expect([self.COMMAND_PROMPT, self.TERMINAL_PROMPT])
            if i == 1:
                child.sendline(self.TERMINAL_TYPE)
                child.expect(self.COMMAND_PROMPT)

        return child


    def run(self, cmd):
        child = self.ssh_connect()

        try:
            child.sendline(cmd)
            self.send_passwd_if_sudo(child, cmd)

            child.expect(f'{self.user}@', timeout=10)
            output = child.before.decode()
        except Exception as e:
            print(cmd)
            raise e
        finally:
            child.close()

        return self.remove_escape_char(output)

    def run_loop_process(self,cmd):
        child = self.ssh_connect()
        try:
            child.sendline(cmd)
            self.send_passwd_if_sudo(child, cmd)

            while True:
                result = child.expect([pexpect.TIMEOUT,f'{sc.user}@'], timeout=3)
                output = child.before.decode()

                yield self.remove_escape_char(output)

                if result == 1: # timeout
                    break
        except Exception as e:
            print(cmd)
            raise e
        finally:
            child.close()

    def send_passwd_if_sudo(self, child, cmd):
        # [sudo] password for {username} :
        if "sudo" in cmd:
            child.expect(f"password for {self.user}: ")
            child.sendline(self.pw)


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

