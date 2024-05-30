
#=======================================
#  $Revision: #1 $
#  $Change: 22715 $
#=======================================

ENUMS = {
    'supervisor_smart_share_mode': [
        'none',
        'jobs'
    ],

    'supervisor_preempt_policy': [
        'disabled',
        'passive',
        'aggressive',
        'mixed'
    ],
    
    'supervisor_license_model': [
        'subjob',
        'host'
    ],

    'supervisor_license_type': [
        'unlimited',
        'designer'
    ],
}

ENUMS['supervisor_smart_share_preempt_policy'] = ENUMS['supervisor_preempt_policy']
