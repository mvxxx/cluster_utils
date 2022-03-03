import argparse
import json
from uuid import uuid4
import shutil
import os
from utils.communication import exec_on_rem_workspace

_USERNAME_REMOTE = 'username@remote'
_TREE_ROOT = 'tree_root'

def sync_clusters(src_cluster, target_cluster, config):
    with open(config, 'r') as cfg_f:
        content = cfg_f.read()
    cfg = json.loads(content)

    src_cluster_host = cfg['clusters'][src_cluster][_USERNAME_REMOTE]
    src_tree_root = cfg['clusters'][src_cluster][_TREE_ROOT]

    target_cluster_host = cfg['clusters'][target_cluster][_USERNAME_REMOTE]
    target_tree_root = cfg['clusters'][target_cluster][_TREE_ROOT]

    sync_paths = cfg['sync_paths']
    workspace = uuid4().hex
    os.makedirs(workspace)

    try:
        for sync_path in sync_paths:
            # rsync from remote to local
            os.makedirs(os.path.join(workspace, sync_path))
            os.system(f'rsync -vuar {src_cluster_host}:{os.path.join(src_tree_root, sync_path)}/* {os.path.join(workspace, sync_path)}')

            # rsync from local to remote
            exec_on_rem_workspace(target_cluster_host, target_tree_root, [f'mkdir -p {sync_path}'])
            os.system(f'rsync -vuar {os.path.join(workspace, sync_path)}/* {target_cluster_host}:{os.path.join(target_tree_root, sync_path)}')

    except Exception as e:
        print('Something failed...', str(e))
        shutil.rmtree(workspace)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Path to clusters config file', required=True, type=str)
    parser.add_argument(
        '-s', '--source-cluster', help='Name of cluster which is synced', required=True, type=str)
    parser.add_argument(
        '-t', '--target-cluster', action='append', help='Names of clusters to be synced', required=True)
    args = parser.parse_args()

    cfg = args.config
    source_cluster = args.source_cluster
    target_clusters = args.target_cluster

    for target in target_clusters:
        sync_clusters(source_cluster, target, cfg)
