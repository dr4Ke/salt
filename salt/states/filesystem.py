# -*- coding: utf-8 -*-
'''
Managing filesystems
====================

Create any type of filesystem with the present function. Supports only
ext2, ext3 and ext4, for now.

WARNING: this state WILL erase partition with unsupported filesystem.

.. code-block:: yaml

    /dev/sdb:
      filesystem.present:
        - fstype: ext4
'''

# Import python libs
import os.path

# Import salt libs
from salt._compat import string_types


def present(name,
            fstype):
    '''
    Verify that a filesystem exists

    name
        The device name, typically the device node, such as /dev/sdb1

    fstype
        The filesystem type, this will be ext2/3/4
    '''
    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}

    # remove possible trailing slash
    name = name.rstrip("/")

    # supported filesystems
    supported_fs = ['ext2', 'ext3', 'ext4']
    if fstype not in supported_fs:
        ret['comment'] = 'Filesystem not supported (' + fstype + ')'
        ret['result']  = False
        return ret

    cur_fs = _cur_fs(name)

    if cur_fs == fstype:
        out = 'present'
    elif cur_fs != None:
        out = 'different'
    elif __opts__['test']:
        # No ext filesystem, filesystem would be created
        out = 'mkfs_creation'
    else:
        # No ext filesystem, create one
        create_fs = __salt__['extfs.mkfs'](name, fstype)
        if _cur_fs(name) == fstype:
            out = 'mkfs_ok'
        else:
            out = 'mkfs_error'

    if out == 'present':
        ret['comment'] = "device already using filesystem " + fstype
    elif out == 'different':
        ret['comment'] = "device already using a different filesystem (" + cur_fs + ")"
    elif out == 'mkfs_creation':
        ret['comment'] = "Filesystem " + fstype + " would be created"
        ret['result']  = None
    elif out == 'mkfs_ok':
        ret['changes']['mkfs'] = "Filesystem " + fstype + " successfully created"
    elif out == 'mkfs_error':
        ret['comment'] = "The filesystem " + fstype + " creation error"
        ret['result']  = False
    else:
        ret['comment'] = "An error has occured (unknow result: " + out
        ret['result']  = False

    return ret


def _cur_fs(name):
    # Get the current state
    try:
        cur_fs_attr = __salt__['extfs.attributes'](name, 'h')
    except Exception as inst:
        cur_fs_attr = None
        cur_fs = None

    if cur_fs_attr is not None:
        if 'extent' in cur_fs_attr['Filesystem features']:
            cur_fs = 'ext4'
        elif 'has_journal' in cur_fs_attr['Filesystem features']:
            cur_fs = 'ext3'
        elif 'ext_attr' in cur_fs_attr['Filesystem features']:
            cur_fs = 'ext2'
        else:
            cur_fs = 'Unknown'

    return cur_fs
