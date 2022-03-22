from typing import List, Optional
import argparse
from utils.communication import exec_on_rem_workspace, send_content_to_server, send_to_server 
import importlib.util
import time
import os
from run_sbatch import create_sbatch_job


def submit_job(execute_command: str,  gin: str, local_workspace: str, rem_host: str, rem_workspace: str,
               jobname: str, partition: str, qos: str,
               gpus: int, max_time: str, mem: str):

    # Gather configs
    spec = importlib.util.spec_from_file_location("module.gin", gin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    date = time.strftime("%Y%m%d_%H%M%S")
    names = [f'{i}.gin' for i in range(len(module.configs))]
    for name, c in zip(names, module.configs):
        with open(name, 'w+') as f:
            f.write(c)
    
    # Create folders
    folder_names = [f'{date}_{i}' for i in range(len(names))]
    exec_on_rem_workspace(rem_host, '~', [f'mkdir -p {rem_workspace}'])
    exec_on_rem_workspace(rem_host, rem_workspace, [f'mkdir -p {fname}' for fname in folder_names])

    # Send gins and folder
    for ginname, fname in zip(names, folder_names):
        send_to_server(local_workspace, rem_host, os.path.join(rem_workspace, fname))
        send_to_server(ginname, rem_host, os.path.join(rem_workspace, fname))
        exec_on_rem_workspace(rem_host, os.path.join(rem_workspace, fname), [f'mv {os.path.basename(local_workspace)}/* ./'])


    # Submit sbatch
    for fname in folder_names:
        create_sbatch_job(['python3 runner.py'], rem_host, rem_workspace, jobname, partition, qos, gpus, max_time, job_folder=fname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--command', 
        help='Execute command', 
        required=True, type=str)

    parser.add_argument(
        '--gin', 
        help='Path to gin config', 
        required=True, type=str)

    parser.add_argument(
        '--local-workspace', 
        help='Path to local workspace which will be send to cluster', 
        required=True, type=str)

    parser.add_argument(
        '--remote-host', 
        help='Remote Host, for instance abc123@cluster.com', 
        required=True, type=str)

    parser.add_argument(
        '--remote-workspace', 
        help='Either in relative or absolute form', 
        required=True, type=str)

    parser.add_argument(
        '--jobname', 
        help='Name of slurm job', 
        required=True, type=str)

    parser.add_argument(
        '--partition', 
        help='Partition name', 
        required=True, type=str)

    parser.add_argument(
        '--qos', 
        help='QOS', 
        required=True, type=str)

    parser.add_argument(
        '--gpus', 
        help='Number of gpus', 
        required=True, type=int)

    parser.add_argument(
        '--max-time', 
        help='max time', 
        required=True, type=str)

    parser.add_argument(
        '--mem',
        help='Memory, for instance 20G', 
        required=False, default='30G', type=str)
  
    args = parser.parse_args()

    submit_job(
        execute_command=args.command,
        gin=args.gin,
        local_workspace=args.local_workspace,
        rem_host=args.remote_host,
        rem_workspace=args.remote_workspace,
        jobname=args.jobname,
        partition=args.partition,
        qos=args.qos,
        gpus=args.gpus,
        max_time=args.max_time,
        mem=args.mem
    )