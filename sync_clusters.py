import argparse
import json
from uuid import uuid4
import shutil
import os
from utils.communication import exec_on_rem_workspace

_USERNAME_REMOTE = 'username@remote'
_TREE_ROOT = 'tree_root'

def sync_clusters(target_cluster, config):
    target_cluster_host = cfg['clusters'][target_cluster][_USERNAME_REMOTE]
    target_tree_root = cfg['clusters'][target_cluster][_TREE_ROOT]

    sync_paths = cfg['sync_paths']
    for sync_path in sync_paths:
        # rsync from local to remote
        exec_on_rem_workspace(target_cluster_host, target_tree_root, [f'mkdir -p {sync_path}'])
        os.system(f'rsync -vuar {os.path.join(workspace, sync_path)}/* {target_cluster_host}:{os.path.join(target_tree_root, sync_path)}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config', help='Path to clusters config file', required=True, type=str)
    parser.add_argument(
        '-s', '--source-cluster', help='Name of cluster which is synced', required=True, type=str)
    parser.add_argument(
        '-t', '--target-cluster', action='append', help='Names of clusters to be synced', required=True)
    args = parser.parse_args()

    config_path = args.config
    source_cluster = args.source_cluster
    target_clusters = args.target_cluster

    workspace = uuid4().hex
    os.makedirs(workspace)
    
    with open(config_path, 'r') as cfg_f:
        content = cfg_f.read()
    cfg = json.loads(content)

    src_cluster_host = cfg['clusters'][source_cluster][_USERNAME_REMOTE]
    src_tree_root = cfg['clusters'][source_cluster][_TREE_ROOT]

    # rsync from remote to local
    for sync_path in cfg['sync_paths']:
        os.makedirs(os.path.join(workspace, sync_path))
        os.system(f'rsync -vuar {src_cluster_host}:{os.path.join(src_tree_root, sync_path)}/* {os.path.join(workspace, sync_path)}')
    
    for target in target_clusters:
        try:
            sync_clusters(target, cfg)
        except Exception as e:
            print(f'Failed syncing to {target} due to exception: {str(e)}')

    print(f'Removing workspace {workspace}')
    shutil.rmtree(workspace)