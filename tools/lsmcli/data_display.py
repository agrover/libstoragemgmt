# Copyright (C) 2014 Red Hat, Inc.
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
#
# Author: Gris Ge <fge@redhat.com>
import sys

try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict

from datetime import datetime

from lsm import (size_bytes_2_size_human, LsmError, ErrorNumber,
                 System, Pool, Disk, Volume, AccessGroup,
                 FileSystem, FsSnapshot, NfsExport, TargetPort)

BIT_MAP_STRING_SPLITTER = ','


## Users are reporting errors with broken pipe when piping output
# to another program.  This appears to be related to this issue:
# http://bugs.python.org/issue11380
# Unable to reproduce, but hopefully this will address it.
# @param msg    The message to be written to stdout
def out(msg):
    try:
        sys.stdout.write(str(msg))
        sys.stdout.write("\n")
        sys.stdout.flush()
    except IOError:
        sys.exit(1)


def _bit_map_to_str(bit_map, conv_dict):
    rc = []
    bit_map = int(bit_map)
    for cur_enum in conv_dict.keys():
        if cur_enum & bit_map:
            rc.append(conv_dict[cur_enum])
    # If there are no bits set we really don't need a string
    if bit_map != 0 and len(rc) == 0:
        return 'Unknown(%s)' % hex(bit_map)
    return BIT_MAP_STRING_SPLITTER.join(rc)


def _enum_type_to_str(int_type, conv_dict):
    rc = ''
    int_type = int(int_type)

    if int_type in conv_dict.keys():
        return conv_dict[int_type]
    return 'Unknown(%d)' % int_type


def _str_to_enum(type_str, conv_dict):
    keys = [k for k, v in conv_dict.items() if v.lower() == type_str.lower()]
    if len(keys) > 0:
        return keys[0]
    raise LsmError(ErrorNumber.INVALID_ARGUMENT,
                   "Failed to convert %s to lsm type" % type_str)


_SYSTEM_STATUS_CONV = {
    System.STATUS_UNKNOWN: 'Unknown',
    System.STATUS_OK: 'OK',
    System.STATUS_ERROR: 'Error',
    System.STATUS_DEGRADED: 'Degraded',
    System.STATUS_PREDICTIVE_FAILURE: 'Predictive failure',
    System.STATUS_OTHER: 'Other',
}


def system_status_to_str(system_status):
    return _bit_map_to_str(system_status, _SYSTEM_STATUS_CONV)


_POOL_STATUS_CONV = {
    Pool.STATUS_UNKNOWN: 'Unknown',
    Pool.STATUS_OK: 'OK',
    Pool.STATUS_OTHER: 'Other',
    Pool.STATUS_DEGRADED: 'Degraded',
    Pool.STATUS_ERROR: 'Error',
    Pool.STATUS_STOPPED: 'Stopped',
    Pool.STATUS_RECONSTRUCTING: 'Reconstructing',
    Pool.STATUS_VERIFYING: 'Verifying',
    Pool.STATUS_INITIALIZING: 'Initializing',
    Pool.STATUS_GROWING: 'Growing',
}


def pool_status_to_str(pool_status):
    return _bit_map_to_str(pool_status, _POOL_STATUS_CONV)


_POOL_ELEMENT_TYPE_CONV = {
    Pool.ELEMENT_TYPE_POOL: 'POOL',
    Pool.ELEMENT_TYPE_VOLUME: 'VOLUME',
    Pool.ELEMENT_TYPE_VOLUME_THIN: 'VOLUME_THIN',
    Pool.ELEMENT_TYPE_VOLUME_FULL: 'VOLUME_FULL',
    Pool.ELEMENT_TYPE_FS: 'FS',
    Pool.ELEMENT_TYPE_SYS_RESERVED: 'SYSTEM_RESERVED',
    Pool.ELEMENT_TYPE_DELTA: "DELTA",
}

_POOL_UNSUPPORTED_ACTION_CONV = {
    Pool.UNSUPPORTED_VOLUME_GROW: "Volume Grow",
    Pool.UNSUPPORTED_VOLUME_SHRINK: "Volume Shrink"
}


def pool_element_type_to_str(element_type):
    return _bit_map_to_str(element_type, _POOL_ELEMENT_TYPE_CONV)


def pool_unsupported_actions_to_str(unsupported_actions):
    return _bit_map_to_str(unsupported_actions, _POOL_UNSUPPORTED_ACTION_CONV)


_VOL_PROVISION_CONV = {
    Volume.PROVISION_DEFAULT: 'DEFAULT',
    Volume.PROVISION_FULL: 'FULL',
    Volume.PROVISION_THIN: 'THIN',
    Volume.PROVISION_UNKNOWN: 'UNKNOWN',
}


def vol_provision_str_to_type(vol_provision_str):
    return _str_to_enum(vol_provision_str, _VOL_PROVISION_CONV)


_VOL_ADMIN_STATE_CONV = {
    Volume.ADMIN_STATE_DISABLED: 'Yes',
    Volume.ADMIN_STATE_ENABLED: 'No',
}


def vol_admin_state_to_str(vol_admin_state):
    return _enum_type_to_str(vol_admin_state, _VOL_ADMIN_STATE_CONV)


_VOL_REP_TYPE_CONV = {
    Volume.REPLICATE_CLONE: 'CLONE',
    Volume.REPLICATE_COPY: 'COPY',
    Volume.REPLICATE_MIRROR_SYNC: 'MIRROR_SYNC',
    Volume.REPLICATE_MIRROR_ASYNC: 'MIRROR_ASYNC',
    Volume.REPLICATE_UNKNOWN: 'UNKNOWN',
}


def vol_rep_type_str_to_type(vol_rep_type_str):
    return _str_to_enum(vol_rep_type_str, _VOL_REP_TYPE_CONV)


_DISK_TYPE_CONV = {
    Disk.TYPE_UNKNOWN: 'UNKNOWN',
    Disk.TYPE_OTHER: 'Other',
    Disk.TYPE_ATA: 'ATA',
    Disk.TYPE_SATA: 'SATA',
    Disk.TYPE_SAS: 'SAS',
    Disk.TYPE_FC: 'FC',
    Disk.TYPE_SOP: 'SCSI Over PCI-E(SSD)',
    Disk.TYPE_SCSI: 'SCSI',
    Disk.TYPE_NL_SAS: 'NL_SAS',
    Disk.TYPE_HDD: 'HDD',
    Disk.TYPE_SSD: 'SSD',
    Disk.TYPE_HYBRID: 'Hybrid',
    Disk.TYPE_LUN: 'Remote LUN',
}


def disk_type_to_str(disk_type):
    return _enum_type_to_str(disk_type, _DISK_TYPE_CONV)


_DISK_STATUS_CONV = {
    Disk.STATUS_UNKNOWN: 'Unknown',
    Disk.STATUS_OK: 'OK',
    Disk.STATUS_OTHER: 'Other',
    Disk.STATUS_PREDICTIVE_FAILURE: 'Predictive failure',
    Disk.STATUS_ERROR: 'Error',
    Disk.STATUS_REMOVED: 'Removed',
    Disk.STATUS_STARTING: 'Starting',
    Disk.STATUS_STOPPING: 'Stopping',
    Disk.STATUS_STOPPED: 'Stopped',
    Disk.STATUS_INITIALIZING: 'Initializing',
    Disk.STATUS_MAINTENANCE_MODE: 'Maintenance',
    Disk.STATUS_SPARE_DISK: 'Spare',
    Disk.STATUS_RECONSTRUCT: 'Reconstruct',
    Disk.STATUS_FREE: 'Free',
}


def disk_status_to_str(disk_status):
    return _bit_map_to_str(disk_status, _DISK_STATUS_CONV)


_AG_INIT_TYPE_CONV = {
    AccessGroup.INIT_TYPE_UNKNOWN: 'Unknown',
    AccessGroup.INIT_TYPE_OTHER: 'Other',
    AccessGroup.INIT_TYPE_WWPN: 'WWPN',
    AccessGroup.INIT_TYPE_ISCSI_IQN: 'iSCSI',
    AccessGroup.INIT_TYPE_ISCSI_WWPN_MIXED: 'iSCSI/WWPN Mixed',
}


def ag_init_type_to_str(init_type):
    return _enum_type_to_str(init_type, _AG_INIT_TYPE_CONV)


def ag_init_type_str_to_lsm(init_type_str):
    return _str_to_enum(init_type_str, _AG_INIT_TYPE_CONV)


_TGT_PORT_TYPE_CONV = {
    TargetPort.TYPE_OTHER: 'Other',
    TargetPort.TYPE_FC: 'FC',
    TargetPort.TYPE_FCOE: 'FCoE',
    TargetPort.TYPE_ISCSI: 'iSCSI',
}


def tgt_port_type_to_str(port_type):
    return _enum_type_to_str(port_type, _TGT_PORT_TYPE_CONV)


class PlugData(object):
    def __init__(self, description, plugin_version):
            self.desc = description
            self.version = plugin_version


class VolumeRAIDInfo(object):
    _RAID_TYPE_MAP = {
        Volume.RAID_TYPE_RAID0: 'RAID0',
        Volume.RAID_TYPE_RAID1: 'RAID1',
        Volume.RAID_TYPE_RAID3: 'RAID3',
        Volume.RAID_TYPE_RAID4: 'RAID4',
        Volume.RAID_TYPE_RAID5: 'RAID5',
        Volume.RAID_TYPE_RAID6: 'RAID6',
        Volume.RAID_TYPE_RAID10: 'RAID10',
        Volume.RAID_TYPE_RAID15: 'RAID15',
        Volume.RAID_TYPE_RAID16: 'RAID16',
        Volume.RAID_TYPE_RAID50: 'RAID50',
        Volume.RAID_TYPE_RAID60: 'RAID60',
        Volume.RAID_TYPE_RAID51: 'RAID51',
        Volume.RAID_TYPE_RAID61: 'RAID61',
        Volume.RAID_TYPE_JBOD: 'JBOD',
        Volume.RAID_TYPE_MIXED: 'MIXED',
        Volume.RAID_TYPE_OTHER: 'OTHER',
        Volume.RAID_TYPE_UNKNOWN: 'UNKNOWN',
    }

    def __init__(self, vol_id, raid_type, strip_size, disk_count,
                 min_io_size, opt_io_size):
        self.vol_id = vol_id
        self.raid_type = raid_type
        self.strip_size = strip_size
        self.disk_count = disk_count
        self.min_io_size = min_io_size
        self.opt_io_size = opt_io_size

    @staticmethod
    def raid_type_to_str(raid_type):
        return _enum_type_to_str(raid_type, VolumeRAIDInfo._RAID_TYPE_MAP)


class DisplayData(object):

    def __init__(self):
        pass

    DISPLAY_WAY_COLUMN = 0
    DISPLAY_WAY_SCRIPT = 1

    DISPLAY_WAY_DEFAULT = DISPLAY_WAY_COLUMN

    DEFAULT_SPLITTER = ' | '

    VALUE_CONVERT = {}

    # lsm.System
    SYSTEM_HEADER = OrderedDict()
    SYSTEM_HEADER['id'] = 'ID'
    SYSTEM_HEADER['name'] = 'Name'
    SYSTEM_HEADER['status'] = 'Status'
    SYSTEM_HEADER['status_info'] = 'Info'

    SYSTEM_COLUMN_SKIP_KEYS = []
    # XXX_COLUMN_SKIP_KEYS contain a list of property should be skipped when
    # displaying in column way.

    SYSTEM_VALUE_CONV_ENUM = {
        'status': system_status_to_str,
    }

    SYSTEM_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[System] = {
        'headers': SYSTEM_HEADER,
        'column_skip_keys': SYSTEM_COLUMN_SKIP_KEYS,
        'value_conv_enum': SYSTEM_VALUE_CONV_ENUM,
        'value_conv_human': SYSTEM_VALUE_CONV_HUMAN,
    }

    PLUG_DATA_HEADER = OrderedDict()
    PLUG_DATA_HEADER['desc'] = 'Description'
    PLUG_DATA_HEADER['version'] = 'Version'

    PLUG_DATA_COLUMN_SKIP_KEYS = []

    PLUG_DATA_VALUE_CONV_ENUM = {}
    PLUG_DATA_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[PlugData] = {
        'headers': PLUG_DATA_HEADER,
        'column_skip_keys': PLUG_DATA_COLUMN_SKIP_KEYS,
        'value_conv_enum': PLUG_DATA_VALUE_CONV_ENUM,
        'value_conv_human': PLUG_DATA_VALUE_CONV_HUMAN,
    }

    # lsm.Pool
    POOL_HEADER = OrderedDict()
    POOL_HEADER['id'] = 'ID'
    POOL_HEADER['name'] = 'Name'
    POOL_HEADER['element_type'] = 'Element Type'
    POOL_HEADER['unsupported_actions'] = 'Does not support'
    POOL_HEADER['total_space'] = 'Total Space'
    POOL_HEADER['free_space'] = 'Free Space'
    POOL_HEADER['status'] = 'Status'
    POOL_HEADER['status_info'] = 'Info'
    POOL_HEADER['system_id'] = 'System ID'

    POOL_COLUMN_SKIP_KEYS = ['unsupported_actions']

    POOL_VALUE_CONV_ENUM = {
        'status': pool_status_to_str,
        'element_type': pool_element_type_to_str,
        'unsupported_actions': pool_unsupported_actions_to_str
    }

    POOL_VALUE_CONV_HUMAN = ['total_space', 'free_space']

    VALUE_CONVERT[Pool] = {
        'headers': POOL_HEADER,
        'column_skip_keys': POOL_COLUMN_SKIP_KEYS,
        'value_conv_enum': POOL_VALUE_CONV_ENUM,
        'value_conv_human': POOL_VALUE_CONV_HUMAN,
    }

    # lsm.Volume
    VOL_HEADER = OrderedDict()
    VOL_HEADER['id'] = 'ID'
    VOL_HEADER['name'] = 'Name'
    VOL_HEADER['vpd83'] = 'SCSI VPD 0x83'
    VOL_HEADER['block_size'] = 'Block Size'
    VOL_HEADER['num_of_blocks'] = 'Block Count'
    VOL_HEADER['size_bytes'] = 'Size'
    VOL_HEADER['admin_state'] = 'Disabled'
    VOL_HEADER['pool_id'] = 'Pool ID'
    VOL_HEADER['system_id'] = 'System ID'

    VOL_COLUMN_SKIP_KEYS = ['block_size', 'num_of_blocks']

    VOL_VALUE_CONV_ENUM = {
        'admin_state': vol_admin_state_to_str
    }

    VOL_VALUE_CONV_HUMAN = ['size_bytes', 'block_size']

    VALUE_CONVERT[Volume] = {
        'headers': VOL_HEADER,
        'column_skip_keys': VOL_COLUMN_SKIP_KEYS,
        'value_conv_enum': VOL_VALUE_CONV_ENUM,
        'value_conv_human': VOL_VALUE_CONV_HUMAN,
    }

    # lsm.Disk
    DISK_HEADER = OrderedDict()
    DISK_HEADER['id'] = 'ID'
    DISK_HEADER['name'] = 'Name'
    DISK_HEADER['disk_type'] = 'Type'
    DISK_HEADER['block_size'] = 'Block Size'
    DISK_HEADER['num_of_blocks'] = 'Block Count'
    DISK_HEADER['size_bytes'] = 'Size'
    DISK_HEADER['status'] = 'Status'
    DISK_HEADER['system_id'] = 'System ID'

    DISK_COLUMN_SKIP_KEYS = ['block_size', 'num_of_blocks']

    DISK_VALUE_CONV_ENUM = {
        'status': disk_status_to_str,
        'disk_type': disk_type_to_str,
    }

    DISK_VALUE_CONV_HUMAN = ['size_bytes', 'block_size']

    VALUE_CONVERT[Disk] = {
        'headers': DISK_HEADER,
        'column_skip_keys': DISK_COLUMN_SKIP_KEYS,
        'value_conv_enum': DISK_VALUE_CONV_ENUM,
        'value_conv_human': DISK_VALUE_CONV_HUMAN,
    }

    # lsm.AccessGroup
    AG_HEADER = OrderedDict()
    AG_HEADER['id'] = 'ID'
    AG_HEADER['name'] = 'Name'
    AG_HEADER['init_ids'] = 'Initiator IDs'
    AG_HEADER['init_type'] = 'Type'
    AG_HEADER['system_id'] = 'System ID'

    AG_COLUMN_SKIP_KEYS = ['init_type']

    AG_VALUE_CONV_ENUM = {
        'init_type': ag_init_type_to_str,
    }

    AG_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[AccessGroup] = {
        'headers': AG_HEADER,
        'column_skip_keys': AG_COLUMN_SKIP_KEYS,
        'value_conv_enum': AG_VALUE_CONV_ENUM,
        'value_conv_human': AG_VALUE_CONV_HUMAN,
    }

    # lsm.FileSystem
    FS_HEADER = OrderedDict()
    FS_HEADER['id'] = 'ID'
    FS_HEADER['name'] = 'Name'
    FS_HEADER['total_space'] = 'Total Space'
    FS_HEADER['free_space'] = 'Free Space'
    FS_HEADER['pool_id'] = 'Pool ID'
    FS_HEADER['system_id'] = 'System ID'

    FS_COLUMN_SKIP_KEYS = []

    FS_VALUE_CONV_ENUM = {
    }

    FS_VALUE_CONV_HUMAN = ['total_space', 'free_space']

    VALUE_CONVERT[FileSystem] = {
        'headers': FS_HEADER,
        'column_skip_keys': FS_COLUMN_SKIP_KEYS,
        'value_conv_enum': FS_VALUE_CONV_ENUM,
        'value_conv_human': FS_VALUE_CONV_HUMAN,
    }

    # lsm.FsSnapshot
    FS_SNAP_HEADER = OrderedDict()
    FS_SNAP_HEADER['id'] = 'ID'
    FS_SNAP_HEADER['name'] = 'Name'
    FS_SNAP_HEADER['ts'] = 'Time Stamp'

    FS_SNAP_COLUMN_SKIP_KEYS = []

    FS_SNAP_VALUE_CONV_ENUM = {
        'ts': datetime.fromtimestamp
    }

    FS_SNAP_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[FsSnapshot] = {
        'headers': FS_SNAP_HEADER,
        'column_skip_keys': FS_SNAP_COLUMN_SKIP_KEYS,
        'value_conv_enum': FS_SNAP_VALUE_CONV_ENUM,
        'value_conv_human': FS_SNAP_VALUE_CONV_HUMAN,
    }

    # lsm.NfsExport
    NFS_EXPORT_HEADER = OrderedDict()
    NFS_EXPORT_HEADER['id'] = 'ID'
    NFS_EXPORT_HEADER['fs_id'] = 'FileSystem ID'
    NFS_EXPORT_HEADER['export_path'] = 'Export Path'
    NFS_EXPORT_HEADER['auth'] = 'Auth Type'
    NFS_EXPORT_HEADER['root'] = 'Root Hosts'
    NFS_EXPORT_HEADER['rw'] = 'RW Hosts'
    NFS_EXPORT_HEADER['ro'] = 'RO Hosts'
    NFS_EXPORT_HEADER['anonuid'] = 'Anonymous UID'
    NFS_EXPORT_HEADER['anongid'] = 'Anonymous GID'
    NFS_EXPORT_HEADER['options'] = 'Options'

    NFS_EXPORT_COLUMN_SKIP_KEYS = ['anonuid', 'anongid', 'auth']

    NFS_EXPORT_VALUE_CONV_ENUM = {}

    NFS_EXPORT_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[NfsExport] = {
        'headers': NFS_EXPORT_HEADER,
        'column_skip_keys': NFS_EXPORT_COLUMN_SKIP_KEYS,
        'value_conv_enum': NFS_EXPORT_VALUE_CONV_ENUM,
        'value_conv_human': NFS_EXPORT_VALUE_CONV_HUMAN,
    }

    # lsm.TargetPort
    TGT_PORT_HEADER = OrderedDict()
    TGT_PORT_HEADER['id'] = 'ID'
    TGT_PORT_HEADER['port_type'] = 'Type'
    TGT_PORT_HEADER['physical_name'] = 'Physical Name'
    TGT_PORT_HEADER['service_address'] = 'Address'
    TGT_PORT_HEADER['network_address'] = 'Network Address'
    TGT_PORT_HEADER['physical_address'] = 'Physical Address'
    TGT_PORT_HEADER['system_id'] = 'System ID'

    TGT_PORT_COLUMN_SKIP_KEYS = ['physical_address', 'physical_name']

    TGT_PORT_VALUE_CONV_ENUM = {
        'port_type': tgt_port_type_to_str,
    }

    TGT_PORT_VALUE_CONV_HUMAN = []

    VALUE_CONVERT[TargetPort] = {
        'headers': TGT_PORT_HEADER,
        'column_skip_keys': TGT_PORT_COLUMN_SKIP_KEYS,
        'value_conv_enum': TGT_PORT_VALUE_CONV_ENUM,
        'value_conv_human': TGT_PORT_VALUE_CONV_HUMAN,
    }

    VOL_RAID_INFO_HEADER = OrderedDict()
    VOL_RAID_INFO_HEADER['vol_id'] = 'Volume ID'
    VOL_RAID_INFO_HEADER['raid_type'] = 'RAID Type'
    VOL_RAID_INFO_HEADER['strip_size'] = 'Strip Size'
    VOL_RAID_INFO_HEADER['disk_count'] = 'Disk Count'
    VOL_RAID_INFO_HEADER['min_io_size'] = 'Minimum I/O Size'
    VOL_RAID_INFO_HEADER['opt_io_size'] = 'Optimal I/O Size'

    VOL_RAID_INFO_COLUMN_SKIP_KEYS = []

    VOL_RAID_INFO_VALUE_CONV_ENUM = {
        'raid_type': VolumeRAIDInfo.raid_type_to_str,
        }
    VOL_RAID_INFO_VALUE_CONV_HUMAN = [
        'strip_size', 'min_io_size', 'opt_io_size']

    VALUE_CONVERT[VolumeRAIDInfo] = {
        'headers': VOL_RAID_INFO_HEADER,
        'column_skip_keys': VOL_RAID_INFO_COLUMN_SKIP_KEYS,
        'value_conv_enum': VOL_RAID_INFO_VALUE_CONV_ENUM,
        'value_conv_human': VOL_RAID_INFO_VALUE_CONV_HUMAN,
    }

    @staticmethod
    def _get_man_pro_value(obj, key, value_conv_enum, value_conv_human,
                           flag_human, flag_enum):
        value = getattr(obj, key)
        if not flag_enum:
            if key in value_conv_enum.keys():
                value = value_conv_enum[key](value)
        if flag_human:
            if key in value_conv_human:
                value = size_bytes_2_size_human(value)
        return value

    @staticmethod
    def _find_max_width(two_d_list, column_index):
        max_width = 1
        for row_index in range(0, len(two_d_list)):
            row_data = two_d_list[row_index]
            if len(row_data[column_index]) > max_width:
                max_width = len(row_data[column_index])
        return max_width

    @staticmethod
    def _data_dict_gen(obj, flag_human, flag_enum, display_way,
                       extra_properties=None, flag_dsp_all_data=False):
        data_dict = OrderedDict()
        value_convert = DisplayData.VALUE_CONVERT[type(obj)]
        headers = value_convert['headers']
        value_conv_enum = value_convert['value_conv_enum']
        value_conv_human = value_convert['value_conv_human']

        if flag_dsp_all_data:
            display_way = DisplayData.DISPLAY_WAY_SCRIPT

        display_keys = []

        if display_way == DisplayData.DISPLAY_WAY_COLUMN:
            for key_name in headers.keys():
                if key_name not in value_convert['column_skip_keys']:
                    display_keys.append(key_name)
        elif display_way == DisplayData.DISPLAY_WAY_SCRIPT:
            display_keys = headers.keys()

        if extra_properties:
            for extra_key_name in extra_properties:
                if extra_key_name not in display_keys:
                    display_keys.append(extra_key_name)

        for key in display_keys:
            key_str = headers[key]
            value = DisplayData._get_man_pro_value(
                obj, key, value_conv_enum, value_conv_human, flag_human,
                flag_enum)
            data_dict[key_str] = value

        return data_dict

    @staticmethod
    def display_data(objs, display_way=None,
                     flag_human=True, flag_enum=False,
                     extra_properties=None,
                     splitter=None,
                     flag_with_header=True,
                     flag_dsp_all_data=False):
        if len(objs) == 0:
            return None

        if display_way is None:
            display_way = DisplayData.DISPLAY_WAY_DEFAULT

        if splitter is None:
            splitter = DisplayData.DEFAULT_SPLITTER

        data_dict_list = []
        if type(objs[0]) in DisplayData.VALUE_CONVERT.keys():
            for obj in objs:
                data_dict = DisplayData._data_dict_gen(
                    obj, flag_human, flag_enum, display_way,
                    extra_properties, flag_dsp_all_data)
                data_dict_list.extend([data_dict])
        else:
            return None
        if display_way == DisplayData.DISPLAY_WAY_SCRIPT:
            DisplayData.display_data_script_way(data_dict_list, splitter)
        elif display_way == DisplayData.DISPLAY_WAY_COLUMN:
            DisplayData._display_data_column_way(
                data_dict_list, splitter, flag_with_header)
        return True

    @staticmethod
    def display_data_script_way(data_dict_list, splitter):
        key_column_width = 1
        value_column_width = 1

        for data_dict in data_dict_list:
            for key_name in data_dict.keys():
                # find the max column width of key
                cur_key_width = len(key_name)
                if cur_key_width > key_column_width:
                    key_column_width = cur_key_width
                # find the max column width of value
                cur_value = data_dict[key_name]
                cur_value_width = 0
                if isinstance(cur_value, list):
                    if len(cur_value) == 0:
                        continue
                    cur_value_width = len(str(cur_value[0]))
                else:
                    cur_value_width = len(str(cur_value))
                if cur_value_width > value_column_width:
                    value_column_width = cur_value_width

        row_format = '%%-%ds%s%%-%ds' % (key_column_width,
                                         splitter,
                                         value_column_width)
        sub_row_format = '%s%s%%-%ds' % (' ' * key_column_width,
                                         splitter,
                                         value_column_width)
        obj_splitter = '%s%s%s' % ('-' * key_column_width,
                                   '-' * len(splitter),
                                   '-' * value_column_width)

        for data_dict in data_dict_list:
            out(obj_splitter)
            for key_name in data_dict:
                value = data_dict[key_name]
                if isinstance(value, list):
                    flag_first_data = True
                    for sub_value in value:
                        if flag_first_data:
                            out(row_format % (key_name, str(sub_value)))
                            flag_first_data = False
                        else:
                            out(sub_row_format % str(sub_value))
                else:
                    out(row_format % (key_name, str(value)))
        out(obj_splitter)

    @staticmethod
    def _display_data_column_way(data_dict_list, splitter, flag_with_header):
        if len(data_dict_list) == 0:
            return
        two_d_list = []

        item_count = len(data_dict_list[0].keys())

        # determine how many lines we will print
        row_width = 0
        for data_dict in data_dict_list:
            cur_max_wd = 0
            for key_name in data_dict.keys():
                if isinstance(data_dict[key_name], list):
                    cur_row_width = len(data_dict[key_name])
                    if cur_row_width > cur_max_wd:
                        cur_max_wd = cur_row_width
                else:
                    pass
            if cur_max_wd == 0:
                cur_max_wd = 1
            row_width += cur_max_wd

        if flag_with_header:
            # first line for header
            row_width += 1

        # init 2D list
        for raw in range(0, row_width):
            new = []
            for column in range(0, item_count):
                new.append('')
            two_d_list.append(new)

        # header
        current_row_num = -1
        if flag_with_header:
            two_d_list[0] = data_dict_list[0].keys()
            current_row_num = 0

        # Fill the 2D list with data_dict_list
        for data_dict in data_dict_list:
            current_row_num += 1
            save_row_num = current_row_num
            values = data_dict.values()
            for index in range(0, len(values)):
                value = values[index]
                if isinstance(value, list):
                    for sub_index in range(0, len(value)):
                        tmp_row_num = save_row_num + sub_index
                        two_d_list[tmp_row_num][index] = str(value[sub_index])

                    if save_row_num + len(value) > current_row_num:
                        current_row_num = save_row_num + len(value) - 1
                else:
                    two_d_list[save_row_num][index] = str(value)

        # display two_list
        row_formats = []
        header_splitter = ''
        for column_index in range(0, len(two_d_list[0])):
            max_width = DisplayData._find_max_width(two_d_list, column_index)
            row_formats.extend(['%%-%ds' % max_width])
            header_splitter += '-' * max_width
            if column_index != (len(two_d_list[0]) - 1):
                header_splitter += '-' * len(splitter)

        row_format = splitter.join(row_formats)
        for row_index in range(0, len(two_d_list)):
            out(row_format % tuple(two_d_list[row_index]))
            if row_index == 0 and flag_with_header:
                out(header_splitter)
