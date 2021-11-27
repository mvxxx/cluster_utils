from typing import List
import subprocess

def exit_if_error(code):
    if code != 0:
        print('Something went wrong...')
        exit(code)

def send_to_server(file: str, rem_host: str, rem_workspace: str):
    exit_if_error(subprocess.run([
        'scp -r', file, f'{rem_host}:~/{rem_workspace}/'
    ]).returncode)

def exec_on_rem_workspace(rem_host: str, rem_workspace: str, cmds: List[str]):
    cmds = [f'cd {rem_workspace}'] + cmds
    exit_if_error(subprocess.run([
        'ssh', rem_host, '; '.join(cmds)
    ]).returncode)

def send_to_server(file, rem_host, rem_workspace):
    exit_if_error(subprocess.run([
        'scp', file, f'{rem_host}:~/{rem_workspace}/'
    ]).returncode)