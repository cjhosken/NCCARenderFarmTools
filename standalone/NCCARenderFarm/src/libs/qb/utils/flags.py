
#=======================================
#  $Revision: #1 $
#  $Change: 22715 $
#=======================================

import logging

FLAGS = {
    'job_flags': {
        'uninterruptible': 0x1,
        'memory_hard_limit': 0x2,
        'grid': 0x4,
        'auto_mount': 0x8,
        'export_environment': 0x10,
        'expand': 0x20,
        'thrifty': 0x40,
        'export_job_type': 0x80,
        'host_list': 0x100,
        'elite': 0x200,
        'mail': 0x400,
        'disable_job_object': 0x800,
        'disable_windows_job_object': 0x800,
        'disable_cpu_limit': 0x1000,
        'disable_auto_complete': 0x2000,
        'auto_wrangling': 0x4000,
        'p_agenda': 0x8000,
        'migrate_on_frame_retry': 0x10000,
        'convert_path': 0x20000,
        'enable_job_object': 0x40000,
        'enable_windows_job_object': 0x40000,
        'no_defaults': 0x80000,
    },

    'supervisor_flags': {
        'enforce_password': 0x1,
        'host_recontact': 0x2,
        'heartbeat_monitor': 0x4,
        'clone_logs': 0x8,
        'remove_logs': 0x10,
        'master': 0x20,
        'ssl': 0x40,
        'multicast': 0x80,
        'schedule': 0x100,
        'rotate_logs': 0x200,
        'stub_optimize': 0x400,
        'running_monitor': 0x800,
        'retry_busy': 0x1000,
        'ignore_duplicate_peer': 0x2000,
        'enable_max_connections': 0x4000,
        'enable_prediction': 0x8000,
        'disable_submit_check': 0x10000,
        'archive_jobs': 0x20000,
    },

    'supervisor_manifest_flags': {
        'job': 0x1,
        'subjob': 0x2,
        'work': 0x4,
    },

    'supervisor_log_flags': {
        'job': 0x1,
        'subjob': 0x2,
        'work': 0x4,
        'callback': 0x8,
        'user': 0x10,
        'admin': 0x20,
        'mail': 0x40,
    },

    'supervisor_language_flags': {
        'qube': 0x1,
        'perl': 0x2,
        'python': 0x4,
        'post': 0x8,
        'mail': 0x10,
        'dependency': 0x20,
        'auto_wrangling': 0x40,
    },

    'worker_flags': {
        'dedicated': 0x1,
        'dynamic': 0x2,
        'auto_mount': 0x4,
        'remove_logs': 0x8,
        'load_profile': 0x10,
        'ssl': 0x20,
        'rotate_logs': 0x40,
        'enable_winbind': 0x80,
        'disable_quickboot': 0x100,
        'auto_remove': 0x200,
    },

    'permissions': {
        'submit_job': 0x1,
        'submit_callback': 0x2,
        'submit_global_callback': 0x4,
        'bump': 0x8,
        'kill': 0x10,
        'remove': 0x20,
        'modify': 0x40,
        'preempt': 0x80,
        'block': 0x100,
        'interrupt': 0x200,
        'complete': 0x400,
        'unblock': 0x800,
        'suspend': 0x1000,
        'resume': 0x2000,
        'retry': 0x4000,
        'requeue': 0x8000,
        'migrate': 0x10000,
        'shove': 0x20000,
        'fail': 0x40000,
        'retire': 0x80000,
        'reset': 0x100000,
        'all': 0x1fffff,
        'lock_host': 0x8000000,
        'sudo_admin': 0x10000000,
        'impersonate': 0x20000000,
        'admin': 0x40000000,
        'default': 0x81ffff3,
        'group_default': 0x0,
        'undefined': 0x80000000,
        'full_access': 0xffffffff,
    },    

    'supervisor_verbosity': {
        'startup': 0x1,
        'work': 0x2,
        'subjob': 0x4,
        'job': 0x8,
        'host': 0x10,
        'log': 0x20,
        'admin': 0x40,
        'command': 0x80,
        'query': 0x100,
        'sync': 0x200,
        'queue': 0x400,
        'callback': 0x800,
        'debug': 0x1000,
        'error': 0x2000,
        'warning': 0x4000,
        'security': 0x8000,
        'auth': 0x10000,
        'preempt': 0x20000,
        'memory': 0x40000,
        'web': 0x80000,
        'info': 0x100000,
        'license': 0x200000,
        'file': 0x400000,
    }
}

FLAGS['supervisor_job_flags'] = FLAGS['job_flags']
FLAGS['client_job_flags'] = FLAGS['job_flags']
FLAGS['supervisor_default_security'] = FLAGS['permissions']


def isFlagSet(configParam, flag, flagVal):
    '''
    @param configParam: configuration parameter name, e.g. C{'supervisor_job_flags'}
    @type configParam: C{str}

    @param flag: flag to test for
    @type flag: C{str}

    @param flagVal: value to test against to see if the flag is set, can be a decimal number or a string or any base, e.g. C{'0x1245'}
    @type: flagVal: C{int} or C{str}

    '''
    flagIsSet = False
    configParam = configParam.lower()

    # convert to decimal if it's a string, radix=0 allows int() to guess at base
    if isinstance(flagVal, str):
        flagVal = int(flagVal, 0)

    if configParam in FLAGS:
        flagDict = FLAGS[configParam]

        if flag not in flagDict:
            logging.error('qb.utils.flags.flagIsSet: unknown "%s" flag: "%s"' % (configParam, flag))
            
        if flagDict.get(flag, 0) & flagVal > 0:
            flagIsSet = True
    else:
        logging.error('qb.utils.flags.flagIsSet: unknown configuration parameter: "%s"' % configParam)
    
    return flagIsSet

def flagIntValToString(configParam, intVal):
    '''
    '''
    flagString = ''
    setFlags = []
    # ensure we're dealing with a hex value
    if isinstance(intVal, str):
        intVal = int(intVal, 0)
    
    if configParam in FLAGS:
        flagDict = FLAGS[configParam]

        for (name, val) in list(flagDict.items()):
            if val & intVal:
                setFlags.append(name)
    else:
        logging.error('qb.utils.flags.flagIsSet: unknown configuration parameter: "%s"' % configParam)
    
    flagString = ','.join(sorted(setFlags))

    return flagString

