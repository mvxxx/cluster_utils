from typing import Optional, List
from utils.communication import exec_on_rem_workspace, send_to_server, exit_if_error
import subprocess
import names
import os
import time

def prepare_file(cmds: List[str], jobname: str, partition: str, qos: str,
 gpus: int, time: int, logfile: str, node: Optional[str]) -> str:
  jobname_sbatch = f'#SBATCH --job-name={jobname}'
  partition_sbatch = f'#SBATCH --partition={partition}'
  qos_sbatch = f'#SBATCH --qos={qos}'
  gres_sbatch =f'#SBATCH --gres=gpu:{gpus}'
  time_sbatch = f'#SBATCH --time={time}'
  output_sbatch = f'#SBATCH --output={logfile}'
  node_sbatch = f'#SBATCH --nodelist={node}' if node else ''

  cmd = '\n'.join(cmds)

  return R'''#!/bin/bash
#
{jobname_sbatch}
{partition_sbatch}
{qos_sbatch}
{gres_sbatch}
{time_sbatch}
{output_sbatch}
{node_sbatch}
# rm -rf trax venv

{cmd}

echo "Task done"
    '''.format(
      jobname_sbatch=jobname_sbatch,
      partition_sbatch=partition_sbatch,
      qos_sbatch=qos_sbatch,
      gres_sbatch=gres_sbatch,
      time_sbatch=time_sbatch,
      output_sbatch=output_sbatch,
      node_sbatch=node_sbatch,
      cmd=cmd
    )

def prepare_workspace(rem_workspace: str, rem_host: str, job_folder: str, job_content: str, job_file: str):
    # create workspace if not exists
    exit_if_error(subprocess.run([
        'ssh', rem_host, f'mkdir -p {rem_workspace}'
    ]).returncode)

    # make job dir
    exec_on_rem_workspace(rem_host=rem_host, rem_workspace=rem_workspace, cmds=[
        f'mkdir -p {job_folder}'
    ])

    # prepare job
    with open(job_file, 'w') as output:
        output.write(job_content)
    
    # send job to server
    send_to_server(job_file, rem_host, os.path.join(rem_workspace, job_folder))

    print('[INFO] Workspace prepared') 

def submit_job(job_file: str, rem_host: str, rem_workspace: str):
    cmd=f'sbatch {job_file}'
    exec_on_rem_workspace(rem_host=rem_host, rem_workspace=rem_workspace,
                          cmds=[cmd])


def create_sbatch_job( cmds: List[str], rem_host: str, rem_workspace: str,
 jobname: str, partition: str, qos: str,
 gpus: int, max_time: str, node: Optional[str] = None):

  logfile = 'job_output.txt'
  job_content = prepare_file(cmds, jobname, partition, qos, gpus, max_time, logfile, node)
  date = time.strftime("%Y%m%d_%H%M%S")
  job_folder = date+jobname
  job_file = 'job_task.txt'
  prepare_workspace(rem_workspace, rem_host, job_folder, job_content, job_file)
  submit_job(job_file, rem_host, os.path.join(rem_workspace, job_folder))

  print(f'Output will be saved in\n{rem_host}:~/{rem_workspace}/{job_folder}')


