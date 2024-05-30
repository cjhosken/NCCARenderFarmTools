"""
Qube Python API Module -- Provide hooks to access Qube's API through python

:Note: This documentation is formatted for use with `epydoc <http://epydoc.sourceforge.net>`__
       using reStructuredText as the format.
       See `epydoc alternate markup languages <http://epydoc.sourceforge.net/manual-othermarkup.html#restructuredtext>`__
       and `Quick reStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`__ for more information on the structure and format.

:Copyright: PipelineFX.  All rights reserved.  

:newfield example: Example, Examples
:newfield Compatibility: Compatibility, Compatibilities

:group Jobtype_Backend: _init_assign, _assignment, _setjob, jobid, subid, jobobj, requestwork, reportwork, reportjob
"""
__docformat__ = "restructuredtext en"

import sys
import warnings
import os.path
import re
from datetime import datetime, date
from time import mktime

#
# Import _qb## binary module
#
qbPythonVer = '_qb%i%i' % (sys.version_info[0], sys.version_info[1])
exec('from . import '+qbPythonVer+' as _qb')

# Load a few constants into the module namespace
try:
    QB_API_XML           = _qb.QB_API_XML
    QB_API_BINARY        = _qb.QB_API_BINARY
    QB_TIME_EPOCH_OFFSET = _qb.QB_TIME_EPOCH_OFFSET
    QB_CLIENT_DEFAULT_CONF = _qb.QB_CLIENT_DEFAULT_CONF                                         # qb.conf
    QB_SUPERVISOR_CONFIG_DEFAULT_LICENSE_FILE = _qb.QB_SUPERVISOR_CONFIG_DEFAULT_LICENSE_FILE   # qb.lic
    QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE = _qb.QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE # qbwrk.conf
    QB_SUPERVISOR_CONFIG_DEFAULT_LOGPATH = _qb.QB_SUPERVISOR_CONFIG_DEFAULT_LOGPATH           # parent dir for job logs, etc
    QB_WORKER_CONFIG_DEFAULT_LOGFILE     = _qb.QB_WORKER_CONFIG_DEFAULT_LOGFILE               # worker log file
    QB_SUPERVISOR_CONFIG_DEFAULT_LOGFILE = _qb.QB_SUPERVISOR_CONFIG_DEFAULT_LOGFILE           # supervisor log file
except:
    # Explicitly set for backwards compatibility with _qb lib modules without these constants
    QB_API_XML           = 2
    QB_API_BINARY        = 1
    QB_TIME_EPOCH_OFFSET = 946702800

## ==========================================================================================
##
## CLASSES
##
## ==========================================================================================

class QBObject(dict):
    """Baseclass for Qube python objects.
    
    :Change: Derived from dict starting with Qube 5.2.
    :Change: Starting from Qube 6.5, QBObject is simply a dict.
    :Change: Starting from Qube 6.5-1, use of accessor methods for job attributes will print a DeprecationWarning

    :Compatibility:
        | Starting with Qube 6.5, this library is no longer compatible with Qube <= 5.1
        
    """
    def getOrSetMethod(self, property, ref):
        '''
        Consolidated function used for set/get methods
        DEPRECATED: use dict-style access for job attributes.
        '''
        warnings.simplefilter('default', DeprecationWarning)
        warnings.warn("Method-style access for qbObject attributes is deprecated, use dictionary-style access: job['%s']" % property, DeprecationWarning, stacklevel=3)

        if ref is not None:
            self[property] = ref
        return self[property]

    
class Job(QBObject):
    """Container for Qube's job properties.
    Jobs are the main containers that are submitted by the user.

    Properties (dict access, i.e. ['id']):
    
        - `account`     : Container for holding account information for Job (str)
        - `agenda`      : list of Work that specifies tasks/frames (list(Work))
        - `p_agenda`    : list of priority/poster/preview-work items (list(Work))
        - `agendastatus`: Agenda state. See below for list of states. (str)
        - `callbacks`   : list of Callbacks to be called when job completes (list(Callback))
        - `cluster`     : Cluster to run the Job on (str)
        - `cpus`        : Number of processes/workers/subjobs to use for the Job (int)
        - `cpustally`   : Tally of number of subjobs per status (dict)
        - `data`        : Encoded string representing the package. Note: Edit the package property, not this. (str, internal) available for developers who wish to use a different encoding scheme rather than the package system. 
        - `dependency`  : Jobid(s) to complete before running (str, comma-separated) (listing <jobid> is shortcut for a job, full format is link-<complete,done,failed,killed>-<job,work,subjob>-<jobid>)
        - `domain`      : Windows Domain for authentication on the Worker (str)
        - `flags`       : Bitfield derived from `flagsstring` field (Internal use only)
        - `flagsstring` : Comma-separated list of Job flags (str)
        - `globalorder` : Priority number used with 'top' and 'bottom' (Internal use only)
        - `groups`      : Group of machines the Job can be dispatched to (str, comma-separated)
        - `hostorder`   : Specified order of machines to dispatch Job to
        - `hosts`       : Machines the Job can be dispatched to (str, comma-separated)
        - `id`          : Job id (int)
        - `kind`        : Extra string tag (str)
        - `label`       : Abstract tag that can be used to reference Job in Callback triggers.  Note: the combination of `pgrp` and `label` must be unique for a job.
        - `lastupdate`  : timestamp since last modification (int)
        - `localorder`  : Priority number used with 'top' and 'bottom' (Internal use only)
        - `mailaddress` : Email address to use for the email callback (str)
        - `name`        : Name of the job (str)
        - `notes`       : User-specified general notes on the job (str)
        - `omitgroups`  : Specified groups of machines to NOT be dispatched to (str, comma-separated)
        - `omithosts`   : Machines the Job can be dispatched to (str, comma-separated)
        - `package`     : Data used when Worker runs the job.  (dict(str, val))
        - `path`        : Reserved
        - `pathmap`     : Reserved
        - `pgrp`        : Job process group. (int) Useful for grouping jobs together logically.  Note: the combination of `pgrp` and `label` must be unique for a job.
        - `pid`         : Job parent id (int)
        - `priority`    : Job priority (int)  Lower number means higher priority.
        - `prototype`   : Job type name (str)
        - `queue`       : Reserved
        - `reason`      : Reason why a job is pending, specified by Supervisor (str)
        - `requirements`: Properties required to determine host eligibility (str, comma-separated)
        - `reservations`: Reserved properties used when dispatching a job (i.e. licenses, memory, etc) (str, comma separated)
        - `restrictions`: Restrict jobs to specific clusters. (str, comma separated)
        - `retrysubjob` : Number of time to attempt to retry a subjob on failure (int)
        - `retrywork`   : Number of time to attempt to retry a frame or work item on failure (int)
        - `retrywork_delay` : Number of seconds to wait before automatically retrying a frame or work item on failure (int)
        - `serverid`    : Reserved
        - `status`      : Job state. See below for list of states. (str)
        - `subjobs`     : list of Subjobs that specifies the machines to execute the work (list(Subjob))
        - `subjobstatus`: Subjob state. See below for list of states. (str)
        - `timecomplete`: timestamp for when job completed (int)
        - `timelimit`   : maximum time in seconds the job is allowed to run before it's forcefully failed (int)
        - `timeout`     : maximum time in seconds the job is allowed to run before a timeout event is generated (int)
        - `agenda_timelimit` : maximum time in seconds a frame is allowed to run before it's forcefully failed (int)
        - `agenda_timeout` : maximum time in seconds a frame is allowed to run before a frame timeout event is generated (int)
        - `timestart`   : timestamp for when job started (int)
        - `timesubmit`  : timestamp for submission time (int)
        - `todo`        : Number of frames/tasks for the job (int)
        - `todotally`   : Tally of number of frames (work) per status (dict)
        - `user`        : User submitting the job. (str) Note: Submitting as different user requires "impersonate" priviledges. 
        - `waitfor`     : Jobid(s) to complete before running (int), Generates callbacks in qb.submit() [DEPRECATED: Use 'dependency']
        - `prod_show`   : holds production show name (str)
        - `prod_shot`   : holds production shot name (str)
        - `prod_seq`    : holds production seq name (str)
        - `prod_client` : holds production client name (str)
        - `prod_dept`   : holds production department name (str)
        - `prod_custom1`: holds production custom data (str)
        - `prod_custom2`: holds production custom data (str)
        - `prod_custom3`: holds production custom data (str)
        - `prod_custom4`: holds production custom data (str)
        - `prod_custom5`: holds production custom data (str)
        - `preflights`  : comma-separated list of paths to job-level preflight programs (str)
        - `postflights` : comma-separated list of paths to job-level postflight programs (str)
        - `agenda_preflights`  : comma-separated list of paths to agenda-level preflight programs (str)
        - `agenda_postflights` : comma-separated list of paths to agenda-level postflight programs (str)

    Job States:
    
        - *complete*    : job is complete. Success.
        - *failed*      : job has failed.
        - *killed*      : job is killed.
        - *blocked*     : job is prevented from running either explicitly or through a dependency.
        - *waiting*     : job is waiting on the worker but not taking resources.
        - *suspended*   : job processing is paused (like a unix process is suspended)
        - *pending*     : job is queued to run.
        - *running*     : job is running.
        - *unknown*     : unknown state reached.
        - *badlogin*    : pending state set when worker password is invalid.
        
    :Change: QBObject derived from dict starting with Qube 5.2.
    """
    
    def __init__(self, data = {}, name='', prototype='', package={}):
        """Construct a job instance.

        :Change: Added in Qube 5.3: name, prototype, and package keyword parameters

        :Parameters:
            data : dict or Job
                initializing properties (optional)
            name : str
                specify name of job (optional)
            prototype : str
                specify prototype/jobtype (optional)
            package : dict
                specify package dict of job (optional)
        """
        # Init QBObject
        QBObject.__init__(self, data)
        # Create required fields if not exist
        self.setdefault('name', '')
        self.setdefault('prototype', '')
        self.setdefault('package', {})
        # Set overrides from keyword args (NOTE: will override dict values if exist)
        if name != '':      self['name']      = name
        if prototype != '': self['prototype'] = prototype
        if package != {}:   self['package']   = package
        
        # Convert dicts to the wrapper types
        if data != None:
            if 'agenda' in data:
                self['agenda']    = [Work(i)     for i in data['agenda']]
            if 'p_agenda' in data:
                self['p_agenda']    = [Work(i)     for i in data['p_agenda']]
            if 'subjobs' in data:
                self['subjobs']   = [Subjob(i)   for i in data['subjobs']]
            if 'callbacks' in data:
                self['callbacks'] = [Callback(i) for i in data['callbacks']]

    def id(self, ref = None):
        return self.getOrSetMethod('id', ref)

    def pid(self, ref = None):
        return self.getOrSetMethod('pid', ref)

    def pgrp(self, ref = None):
        return self.getOrSetMethod('pgrp', ref)

    def priority(self, ref = None):
        return self.getOrSetMethod('priority', ref)

    def localorder(elf, ref = None):
        return self.getOrSetMethod('localorder', ref)

    def globalorder(self, ref = None):
        return self.getOrSetMethod('globalorder', ref)

    def status(self, ref = None):
        return self.getOrSetMethod('status', ref)

    def user(self, ref = None):
        return self.getOrSetMethod('user', ref)

    def domain(self, ref = None):
        return self.getOrSetMethod('domain', ref)

    def name(self, ref = None):
        return self.getOrSetMethod('name', ref)

    def cluster(self, ref = None):
        return self.getOrSetMethod('cluster', ref)

    def cpus(self, ref = None):
        return self.getOrSetMethod('cpus', ref)

    def todo(self, ref = None):
        return self.getOrSetMethod('todo', ref)

    def data(self, ref = None):
        return self.getOrSetMethod('data', ref)

    def prototype(self, ref = None):
        return self.getOrSetMethod('prototype', ref)

    def kind(self, ref = None):
        return self.getOrSetMethod('kind', ref)

    def flags(self, ref = None):
        return self.getOrSetMethod('flags', ref)

    def flagsstring(self, ref = None):
        return self.getOrSetMethod('flagsstring', ref)

    def account(self, ref = None):
        return self.getOrSetMethod('account', ref)

    def label(self, ref = None):
        return self.getOrSetMethod('label', ref)

    def groups(self, ref = None):
        return self.getOrSetMethod('groups', ref)

    def hosts(self, ref = None):
        return self.getOrSetMethod('hosts', ref)

    def hostorder(self, ref = None):
        return self.getOrSetMethod('hostorder', ref)

    def requirements(self, ref = None):
        return self.getOrSetMethod('requirements', ref)

    def reservations(self, ref = None):
        return self.getOrSetMethod('reservations', ref)

    def restrictions(self, ref = None):
        return self.getOrSetMethod('restrictions', ref)

    def serverid(self, ref = None):
        return self.getOrSetMethod('serverid', ref)

    def lastupdate(self, ref = None):
        return self.getOrSetMethod('lastupdate', ref)

    def timesubmit(self, ref = None):
        return self.getOrSetMethod('timesubmit', ref)

    def timestart(self, ref = None):
        return self.getOrSetMethod('timestart', ref)

    def timecomplete(self, ref = None):
        return self.getOrSetMethod('timecomplete', ref)

    def timeout(self, ref = None):
        return self.getOrSetMethod('timeout', ref)

    def timelimit(self, ref = None):
        return self.getOrSetMethod('timelimit', ref)

    def agenda_timeout(self, ref = None):
        return self.getOrSetMethod('agenda_timeout', ref)

    def agendatimeout(self, ref = None):
        return self.getOrSetMethod('agenda_timeout', ref)

    def agenda_timelimit(self, ref = None):
        return self.getOrSetMethod('agenda_timelimit', ref)

    def waitfor(self, ref = None):
        return self.getOrSetMethod('waitfor', ref)

    def dependency(self, ref = None):
        return self.getOrSetMethod('dependency', ref)

    def package(self, ref = None):
        return self.getOrSetMethod('package', ref)

    def callbacks(self, ref = None):
        #warnings.warn("considering the deprecation of this get/set function method.  Please access properties like a standard dict (i.e.  myjob['id'] = 123  print myjob['id'].", DeprecationWarning, stacklevel=2)
        if ref is not None: self.__setitem__('callbacks', ref)
        val = self.get('callbacks', None)
        if val == None:
            warnings.warn("Converting from None to [].  This adjustment will be deprecated in the future.", DeprecationWarning, stacklevel=2)
            return []
        else:
            return val

    def agenda(self, ref = None):
        #warnings.warn("considering the deprecation of this get/set function method.  Please access properties like a standard dict (i.e.  myjob['id'] = 123  print myjob['id'].", DeprecationWarning, stacklevel=2)
        if ref is not None: self.__setitem__('agenda', ref)
        val = self.get('agenda', None)
        if val == None:
            warnings.warn("Converting from None to [].  This adjustment will be deprecated in the future.", DeprecationWarning, stacklevel=2)
            return []
        else:
            return val

    def p_agenda(self, ref = None):
        #warnings.warn("considering the deprecation of this get/set function method.  Please access properties like a standard dict (i.e.  myjob['id'] = 123  print myjob['id'].", DeprecationWarning, stacklevel=2)
        if ref is not None: self.__setitem__('p_agenda', ref)
        val = self.get('p_agenda', None)
        if val == None:
            warnings.warn("Converting from None to [].  This adjustment will be deprecated in the future.", DeprecationWarning, stacklevel=2)
            return []
        else:
            return val

    def subjobs(self, ref = None):
        #warnings.warn("considering the deprecation of this get/set function method.  Please access properties like a standard dict (i.e.  myjob['id'] = 123  print myjob['id'].", DeprecationWarning, stacklevel=2)
        if ref is not None: self.__setitem__('subjobs', ref)
        val = self.get('subjobs', None)
        if val == None:
            warnings.warn("Converting from None to [].  This adjustment will be deprecated in the future.", DeprecationWarning, stacklevel=2)
            return []
        else:
            return val


class Subjob(QBObject):
    """Container for Qube's subjob properties.
    Subjobs control the processes that perform the Work.
    
    Properties (dict access, i.e. ['id']):
    
        - `id`          -- Subjob id (int)
        - `pid`         -- Parent job id (int)
        - `host`        -- machine the subjob is running on (str)
        - `count`       -- number of attempts to process the Subjob
        - `retry`       -- retry limit
        - `status`      -- Subjob state. See below for list of states. (str)
        - `lastupdate`  -- timestamp since last modification (int)
        - `timesubmit`  -- timestamp for submission time (int)
        - `timestart`   -- timestamp for when job started (int)
        - `timecomplete`-- timestamp for when job completed (int)

    Job States:
    
        - complete    -- job is complete. Success.
        - failed      -- job has failed.
        - killed      -- job is killed.
        - blocked     -- job is prevented from running either explicitly or through a dependency.
        - waiting     -- job is waiting on the worker but not taking resources. 
        - suspended   -- job processing is paused (like a unix process is suspended)
        - pending     -- job is queued to run.
        - running     -- job is running.
        - unknown     -- unknown state reached.
        - badlogin    -- pending state set when worker password is invalid.

    :Change: QBObject derived from dict starting with Qube 5.2.
    """
    
    def __init__(self, data = {}):
        """Construct a Subjob instance.

        :Parameters:
            data : dict or Subjob
                initilization properties (optional)
        """
        QBObject.__init__(self, data)

    def id(self, ref = None):
        return self.getOrSetMethod('id', ref)

    def pid(self, ref = None):
        return self.getOrSetMethod('pid', ref)

    def host(self, ref = None):
        return self.getOrSetMethod('host', ref)

    def count(self, ref = None):
        return self.getOrSetMethod('count', ref)

    def retry(self, ref = None):
        return self.getOrSetMethod('retry', ref)
        
    def resultpackage(self, ref = None):
        return self.getOrSetMethod('resultpackage', ref)

    def status(self, ref = None):
        return self.getOrSetMethod('status', ref)

    def lastupdate(self, ref = None):
        return self.getOrSetMethod('lastupdate', ref)

    def timesubmit(self, ref = None):
        return self.getOrSetMethod('timesubmit', ref)

    def timestart(self, ref = None):
        return self.getOrSetMethod('timestart', ref)

    def timecomplete(self, ref = None):
        return self.getOrSetMethod('timecomplete', ref)


## Qube python work class
class Work(QBObject):
    """Container for Qube's Work properties.
    Work is what is to be processed (i.e. frame or task) by a Subjob.

    :Change: QBObject derived from dict starting with Qube 5.2.
    
    Properties (dict access, i.e. ['name']):
    
        - `pid`         -- Parent job id (int)
        - `subid`       -- Subjob id that received the Work (int)
        - `host`        -- machine the Work is processing on (str)
        - `name`        -- name of the Work.  Usually a frame number or range.  Can be a label.  (str)
        - `status`      -- Work state. See below for list of states. (str)
        - `address`     -- IP Address of the machine that received the Work (str)
        - `data`        -- Encoded string representing the Work package. Note: edit the package, not this. (str, internal)
        - `package`     -- Dict passed to Worker when processing the Work. Optional structure for custom jobtypes.  Not currently used by cmdline or cmdrange. (dict(str, val))
        - `result`      -- Result package to be passed back to the supervisor. (dict(str,val)) 
        - `count`       -- Number of attempts used to process the Work, read-only (int)
        - `retry`       -- automatic retry limit (int)
        - `retrydelay`  -- delay before automatic retries (int)
        - `resultpackage`--Dict retrieved from Worker after processing Work. Useful for frame filenames, etc. (dict(str, val))
        - `lastupdate`  -- timestamp since last modification (int)
        - `timesubmit`  -- timestamp for submission time (int)
        - `timestart`   -- timestamp for when job started (int)
        - `timecomplete`-- timestamp for when job completed (int)

    Job States:
    
        - complete    -- job is complete. Success.
        - failed      -- job has failed.
        - killed      -- job is killed.
        - blocked     -- job is prevented from running either explicitly or through a dependency.
        - waiting     -- job is waiting on worker but not taking resources.
        - suspended   -- job processing is paused (like a unix process is suspended)
        - pending     -- job is queued to run.
        - running     -- job is running.
        - unknown     -- unknown state reached.
        - badlogin    -- pending state set when worker password is invalid.
    """
    
    def __init__(self, data = {}):
        """Construct a Work instance.

        :Parameters:
            data : dict or Work
                initilization properties (optional)
        """
        QBObject.__init__(self, data)

    def pid(self, ref = None):
        return self.getOrSetMethod('pid', ref)

    def subid(self, ref = None):
        return self.getOrSetMethod('subid', ref)

    def host(self, ref = None):
        return self.getOrSetMethod('host', ref)

    def name(self, ref = None):
        return self.getOrSetMethod('name', ref)

    def status(self, ref = None):
        return self.getOrSetMethod('status', ref)

    def address(self, ref = None):
        return self.getOrSetMethod('address', ref)

    def data(self, ref = None):
        if ref != None:
            warnings.warn("data property should not be set directly.  Get/Set package instead.", DeprecationWarning, stacklevel=2)
        return self.getOrSetMethod('data', ref)

    def package(self, ref = None):
        return self.getOrSetMethod('package', ref)

    def result(self, ref = None):
        return self.getOrSetMethod('result', ref)

    def count(self, ref = None):
        return self.getOrSetMethod('count', ref)

    def retry(self, ref = None):
        return self.getOrSetMethod('retry', ref)

    def retrydelay(self, ref = None):
        return self.getOrSetMethod('retrydelay', ref)

    def resultpackage(self, ref = None):
        return self.getOrSetMethod('resultpackage', ref)

    def lastupdate(self, ref = None):
        return self.getOrSetMethod('lastupdate', ref)
    
    def timesubmit(self, ref = None):
        return self.getOrSetMethod('timesubmit', ref)

    def timestart(self, ref = None):
        return self.getOrSetMethod('timestart', ref)

    def timecomplete(self, ref = None):
        return self.getOrSetMethod('timecomplete', ref)


## Qube python callback class
class Callback(QBObject):
    """Container for Qube's Callback properties.
    Callbacks execute an action when triggered by an event.
    
    Properties (dict access, i.e. ['id']):
    
        - `id`          -- Callback id (int)
        - `pid`         -- Parent job id (int)
        - `triggers`    -- list of events that trigger the Callback.  See Event Triggers below. (list)
        - `code`        -- code called when Callback triggered. (str)
        - `language`    -- language the code block is written in [values: perl, python, qube] (str)
        - `user`        -- username the Callback code will execute as (str)
        - `count`       -- Number of times the callback has been executed. (int)
        - `maximum`     -- Maximum number of times the callback will be executed. (int) [default: unlimited]
        - `ready`       -- (Internal data property) 

    Event Triggers:
        The event specification syntax is generalized into these 4 parts. 
        <name>-<type>-<context>-<extra>
        Please see the Developer documentation for more information.
    
        Event Names:
            The name is the component of the event which details when the event should 
            take place. This is either pre-defined, or user-defined.
            
            Pre-defined event names:
                - complete        : Job is set to COMPLETE 
                - done            : Job is set to COMPLETE or KILLED or FAILED 
                - submit          : Job has been submitted 
                - killed          : Job has been killed 
                - blocked         : Job has been blocked 
                - failed          : Job has failed 
                - running         : Job has started running 
                - waiting         : Job has been set to WAITING 
                - assigned        : Job has been assigned to a host 
                - removed         : Job has been removed 
                - modified        : Job has been modified 

        Event Types:
            The type of the event allows the system to identify the kind of event referred 
            to. The available pre-defined names are relative to the specification of the 
            type.
            
            Defined event types: 
                - job         : Specifies the entire job 
                - subjob      : Specifies a single subjob 
                - work        : Specifies a single work agenda item 
                - host        : Specifies the event belongs to a host 
                - time        : Specifies a time-based event 
                - repeat      : Specifies an interval event 
                - global      : Specifies a time-based event that exists independent of a job 

        Event Contexts:
            The context or the "label" of the event is a specification to narrow the scope
            of the event. When someone specifies 'job' they don't normally mean all jobs,
            so a context is required to determine which job they are describing.
            
            A context can be specified in 3 different forms: 
                - pre-defined label 
                - process group label
                    Process group labels exist to provide the developer with an abstract method 
                    of determining job relationships independent of the job name or job ID rela- 
                    tive to the process group ID. In order to support this, the jobs must all be 
                    submitted under the same process group ID either by submitting the jobs in 
                    the same API call, or by attaching the job to a process group upon submis- 
                    sion. 
                - job ID 
                    - self        : This job 
                    - parent      : The job referred to by pid 
            
        Event Extras:
            The extra information corresponds to additional information required
            when specifying the event type.
            
                - job             : None 
                - subjob          : subjobid 
                - work            : workid/name 
                - host            : hostname  (str)
                - time            : timeofday (seconds since qube epoch)
                - repeat          : timeofday-interval (seconds)
                - global          : None 
                - globaltime      : timeofday (seconds since qube epoch)
                - globalrepeat    : timeofday-interval (seconds)

        Example event trigger names:
            - done-job-19234
            - running-job-world 
            - done-subjob-self-5 

    :Change: QBObject derived from dict starting with Qube 5.2.
    """

    def __init__(self, data = {}):
        """Construct a Callback instance.

        :Parameters:
            data : dict or `Callback`
                initilization properties (optional)
        """
        QBObject.__init__(self, data)

    def id(self, ref = None):
        return self.getOrSetMethod('id', ref)
    
    def pid(self, ref = None):
        return self.getOrSetMethod('pid', ref)

    def triggers(self, ref = None):
        return self.getOrSetMethod('triggers', ref)

    def code(self, ref = None):
        return self.getOrSetMethod('code', ref)

    def language(self, ref = None):
        return self.getOrSetMethod('language', ref)

    def user(self, ref = None):
        return self.getOrSetMethod('user', ref)

    def count(self, ref = None):
        return self.getOrSetMethod('count', ref)

    def maximum(self, ref = None):
        return self.getOrSetMethod('maximum', ref)

    def ready(self, ref = None):
        return self.getOrSetMethod('ready', ref)


## Qube python host class
class Host(QBObject):
    """Container for Qube's Host properties.
    Hosts are the Workers/Subjobs that process the Work of a Job 
    
    Properties (dict access, i.e. ['name']):
    
        - `state`       : state of the host [values: active, down, panic, none] (str)
        - `name`        : name of machine (str)
        - `macaddress`  : MAC address of the machine.  This is the db's primary key. (str, comma-separated)
        - `cluster`     : cluster the Host belongs to (str)
        - `resources`   : list of resources associated with host that can be reserved by job reservations (str, comma-separated)
        - `restrictions`: cluster restrictions associated with host will only run jobs in specified clusters (str, comma-separated)
        - `properties`  : properties of the host (i.e. processor speed, OS, etc)
        - `stats`       : (reserved) 
        - `groups`      : groups the host belongs to (str, comma-separated)
        - `address`     : IP address of host
        - `subjobs`     : subjobs currently running on host

    :Change: QBObject derived from dict starting with Qube 5.2.
    """

    def __init__(self, data = {}):
        """Construct a Host instance.

        :Parameters:
            data : dict or `Host`
                initilization properties (optional)
        """
        QBObject.__init__(self, data)

    def state(self, ref = None):
        return self.getOrSetMethod('state', ref)

    def name(self, ref = None):
        return self.getOrSetMethod('name', ref)

    def cluster(self, ref = None):
        return self.getOrSetMethod('cluster', ref)

    def resources(self, ref = None):
        return self.getOrSetMethod('resources', ref)

    def restrictions(self, ref = None):
        return self.getOrSetMethod('restrictions', ref)

    def properties(self, ref = None):
        return self.getOrSetMethod('properties', ref)

    def stats(self, ref = None):
        return self.getOrSetMethod('stats', ref)

    def groups(self, ref = None):
        return self.getOrSetMethod('groups', ref)

    def address(self, ref = None):
        return self.getOrSetMethod('address', ref)

    def subjobs(self, ref = None):
        return self.getOrSetMethod('subjobs', ref)


class JobTallyValidator(dict):
    """A class to validate a qb.Job's todotally and cpustally"""
    fields = [
        'badlogin',
        'blocked',
        'complete',
        'failed',
        'killed',
        'pending',
        'running',
        'suspended',
        'unknown',
        'waiting',
    ]

    @classmethod
    def validate(cls, tally_dict):
        """Ensure that all possible states in the tally dictionary are non-negative integers

        :Parameters:
            tally_dict : dict
                a cpustally or todotally dictionary from a qb.Job

        :Returns: Boolean

        :Example: JobTallyValidator.validate(job['cpustally'])
        """
        for field in cls.fields:
            val = tally_dict.get(field)
            if val is None or not(isinstance(val, int)) or val < 0:
                return False
        return True


class JobValidator(object):
    """A class to ensure that a qb.Job instance is not malformed

        :Attention:
            the ``validate`` method **will exit at the first field to fail**

        Validation fields:
            Field tuples:
                string :
                    attr_name
                    
                tuple :
                    data type
                    validation test or function
            
            Validation tests per type:
                int :
                    min_value (default: 0)
                    
                str:
                    min_length (default: 0)
                    
                dict:
                    min # of keys (default: 0)
            
    """
    agenda_fields = [
        ('count', (int,)),
        ('data', (str,)),
        ('host', (str,)),
        ('id', (int,)),
        ('lastupdate', (int, QB_TIME_EPOCH_OFFSET)),
        ('name', (str, 1)),
        ('package', (None,)),
        ('pid', (int,)),
        ('result', (str,)),
        ('resultpackage', (None,)),
        ('retry', (int, -1)),
        ('retrydelay', (int,)),
        ('status', (str, 1)),
        ('subid', (int, -1)),
        ('timecomplete', (int, QB_TIME_EPOCH_OFFSET)),
        ('timecumulative', (int,)),
        ('timestart', (int, QB_TIME_EPOCH_OFFSET)),
    ]

    subjob_fields = [
        ('allocations', (str,)),
        ('count', (int,)),
        ('data', (str,)),
        ('host', (str,)),
        ('id', (int,)),
        ('lastupdate', (int, QB_TIME_EPOCH_OFFSET)),
        ('package', (None,)),
        ('pid', (int,)),
        ('result', (str,)),
        ('resultpackage', (None,)),
        ('retry', (int, -1)),
        ('slots', (int,)),
        ('status', (str,)),
        ('timecomplete', (int, QB_TIME_EPOCH_OFFSET)),
        ('timecumulative', (int,)),
        ('timestart', (int, QB_TIME_EPOCH_OFFSET)),
    ]

    job_fields = [
        ('account', (str,)),
        ('agenda_postflights', (str,)),
        ('agenda_preflights', (str,)),
        ('agenda_timeout', (int, -1)),
        ('agendastatus', (str, 1)),
        ('agenda_timeout', (int, -1)),
        ('auto_migrate_count', (int,)),
        ('cluster', (str,)),
        ('cpus', (int, 1)),
        ('cpustally', (dict, JobTallyValidator.validate)),
        ('cwd', (str,)),
        ('data', (str, 1)),
        ('dependency', (str,)),
        ('domain', (str,)),
        ('drivemap', (dict,)),
        ('flags', (int,)),
        ('flagsstring', (str,)),
        ('globalorder', (int,)),
        ('groups', (str,)),
        ('hostorder', (str,)),
        ('hosts', (str,)),
        ('id', (int,)),
        ('kind', (str,)),
        ('label', (str,1)),
        ('lastupdate', (int, QB_TIME_EPOCH_OFFSET)),
        ('localorder', (int,)),
        ('mailaddress', (str,)),
        ('max_cpus', (int, -1)),
        ('name', (str,)),
        ('notes', (str,)),
        ('omitgroups', (str,)),
        ('omithosts', (str,)),
        ('p_agenda_cpus', (int, -1)),
        ('p_agenda_priority', (int, -1)),
        ('package', (dict, 1)),
        ('path', (str,)),
        ('pathmap', (dict,)),
        ('pgrp', (int,)),
        ('pid', (int, 1)),
        ('postflights', (str,)),
        ('preflights', (str,)),
        ('priority', (int, 1)),
        ('prod_client', (str,)),
        ('prod_custom1', (str,)),
        ('prod_custom2', (str,)),
        ('prod_custom3', (str,)),
        ('prod_custom4', (str,)),
        ('prod_custom5', (str,)),
        ('prod_dept', (str,)),
        ('prod_seq', (str,)),
        ('prod_shot', (str,)),
        ('prod_show', (str,)),
        ('prototype', (str, 1)),
        ('queue', (str,)),
        ('reason', (str,)),
        ('requirements', (str,)),
        ('reservations', (str, 1)),
        ('restrictions', (str,)),
        ('retrysubjob', (int, -1)),
        ('retrywork', (int, -1)),
        ('retrywork_delay', (int,)),
        ('serverid', (int,)),
        ('sourcehost', (str, 1)),
        ('status', (str, 1)),
        ('subjobstatus', (str, 1)),
        ('timecomplete', (int, QB_TIME_EPOCH_OFFSET)),
        ('timeout', (int, -1)),
        ('timestart', (int, QB_TIME_EPOCH_OFFSET)),
        ('timesubmit', (int, QB_TIME_EPOCH_OFFSET)),
        ('todo', (int,)),
        ('todotally', (dict, JobTallyValidator.validate)),
        ('user', (str, 1)),
    ]

    @classmethod
    def validate_int(cls, value, min_value=0):
        """Validate whether a value is an integer and is equal to or greater than a minimum value

        :param value: ``int``
        :param min_value: ``int``
        :return: Boolean
        """
        return isinstance(value, int) and value >= min_value

    @classmethod
    def validate_str(cls, value, min_length=0):
        """Validate whether a value is a string or unicode and has a minimum length

        :param value: ``str`` or ``unicode``
        :param min_length: ``int``
        :return: ``Boolean``
        """
        return isinstance(value, str) and len(value) >= min_length

    @classmethod
    def validate_list(cls, value, min_length=0):
        """Validate whether a value is a list and has at least a minimum number of elements

        :param value: ``list`` or ``tuple``
        :param min_length: ``int``
        :return: ``Boolean``
        """
        return isinstance(value, (list, tuple)) and len(value) >= min_length

    @classmethod
    def validate_dict(cls, value, min_keys=0):
        """Validate whether a value is a dictionary and has at least a minimum number of keys

        :param value:
        :param min_keys: ``int``
        :return:
        """
        return isinstance(value, dict) and len(value) >= min_keys

    @classmethod
    def validate(cls, job, agenda=False, subjobs=False, verbose=False):
        """Iterate over all the fields in a qb.Job dictionary, validating each one in turn
        
        :Attention:
            the ``validate`` method **will exit at the first field to fail**
        
        :param job: a dictionary representing a qb.Job - ``dict``
        :param agenda: if True, also verify all the agenda items in a job - ``boolean``
        :param subjobs: if True, also verify all the job instances - ``boolean``
        :param verbose: if True, print the name of the field that failed validation
        
        :return: ``Boolean``
        
        :Example: qb.JobValidator.validate({'id': 123, 'cluster': '/',...})
        :Example: qb.JobValidator.validate({'id': 123, 'cluster': '/',...}, verbose=True)
        :Example: qb.JobValidator.validate({'id': 123, 'cluster': '/',...}, agenda=True, subjobs=True, verbose=True)
            
        """
        validator_map = {
            int: cls.validate_int,
            str: cls.validate_str,
            str: cls.validate_str,
            list: cls.validate_list,
            tuple: cls.validate_list,
            dict: cls.validate_dict,
            None: lambda x: True
        }

        if agenda and job.get('todo', False) and not ('agenda' in job and isinstance(job.get('agenda', list()), list)):
            if verbose:
                print('no agenda item found in agenda-based job')
            return False

        if subjobs and not ('subjobs' in job and isinstance(job.get('subjobs', list()), list)):
            if verbose:
                print('no instances found')
            return False
        
        validating = [
            (
                'job',
                job,
                cls.job_fields
            )
        ]
        
        if agenda:
            validating.append(
                (
                    'agenda',
                    job.get('agenda', list()),
                    cls.agenda_fields
                )
            )
        
        if subjobs:
            validating.append(
                (
                    'subjobs',
                    job.get('subjobs', list()),
                    cls.subjob_fields
                )
            )
        
        for struct_name, validating_struct, fields in validating:
            if struct_name == 'job':
                struct_list = [validating_struct]
            else:
                struct_list = validating_struct
                
            # if verbose:
            #     print '\n\tvalidating %s fields' % struct_name
            #     if agenda and struct_name == 'agenda' and job.get('todo', 1) == 0:
            #         print '\t  (skipping, not an agenda-based job)'
                
            for idx, qb_struct in enumerate(struct_list):
                # if verbose and struct_name != 'job':
                #     print '\t\t%s %i: %s' % ('-'*2, idx, '-'*6,)
                for k, v_tuple in fields:
                    # if verbose:
                    #     print '\t\tfield: %s' % k
                    validator_fn = validator_map[v_tuple[0]]

                    if len(v_tuple) == 1:
                        if validator_fn(qb_struct[k]) is True:
                            continue
                        else:
                            if verbose:
                                print('%s is invalid' % k)
                            return False
                    else:
                        if callable(v_tuple[1]):
                            if v_tuple[1](qb_struct[k]) is True:
                                continue
                            else:
                                if verbose:
                                    print('%s is invalid' % k)
                                return False
                        else:
                            if validator_fn(qb_struct[k], v_tuple[1]) is True:
                                continue
                            else:
                                if verbose:
                                    print('%s is invalid' % k)
                                return False
            
        return True


## ==========================================================================================
##
## FUNCTIONS
##
## ==========================================================================================

def __dontlookatme__():
    """dummy function (deprecated)
    """
    warnings.warn("deprecating this __dontlookatme__() function.  Will remove it in the future.", DeprecationWarning, stacklevel=2)
    return


def jobinfo(fields=[], filters={}, id=None, status=None, agenda=False, subjobs=False, callbacks=False,
            updatedAfter=None, updatedBefore=None, submittedAfter=None, submittedBefore=None,
            minid=None, maxid=None, limit=None, orderby=None):
    """Gather job information from a list of jobs.

    :Parameters:
        fields : list
            additional info to retrieve. See below. (default=[])
            
                *Options*: agenda, subjobs, callbacks

        filters : dict
            properties to filter retrived items.  See below. (default={})

                *Options*: id, name, user, status, priority, pgrp, pid, todo, cluster, prototype, groups, cpus

        id : int or [int]
            filter shortcut. id=val -> filters={'id': val } (default=None)

        status : str
            filter shortcut. status=val -> filters={'status': val }  (default=None)

                *Options*: complete, failed, killed, blocked, waiting, suspended, pending, running, unknown, badlogin, registering, dying
                
        agenda : bool
            field shortcut.  agenda=True -> fields=['agenda']       (default=False)

        subjobs : bool
            field shortcut.  subjobs=True -> fields=['subjobs']     (default=False)

        callbacks : bool
            field shortcut.  callbacks=True -> fields=['callbacks'] (default=False)

        updatedAfter : int or datetime.datetime or datetime.date
            filter for jobs updated after a specific point in time

        updatedBefore : int or datetime.datetime or datetime.date
            filter for jobs updated before a specific point in time

        submittedAfter : int or datetime.datetime or datetime.date
            filter for jobs submitted after a specific point in time

        submittedBefore : int or datetime.datetime or datetime.date
            filter for jobs submitted before a specific point in time

        minid : int
            set the job ID lower bound for the query (only query for jobs >= id)

        maxid : int
            set the job ID upper bound for the query (only query for jobs <= id)

        limit : int
            limit the number of returned jobs for the query

        orderby : str
            specify sorting field; i.e. this forms the ORDERBY clause used for the job query (like 'id' or 'id DESC')

    :Returns: [`Job`]

    :Note: Jobs returned will not contain agenda, subjob, or callback info unless these parameters are specified.

    :Example: jobs = qb.jobinfo(fields=['agenda', 'subjobs'], filters={'id':2024} )
    :Example: jobs = qb.jobinfo(id=2024, agenda=True, subjobs=True)
    :Example: jobs = qb.jobinfo(id=2024, agenda=True, subjobs=True)
    :Example: jobs = qb.jobinfo(id=[2024,2025])
    :Example: jobs = qb.jobinfo(updatedAfter=1530680480, updatedBefore=1530680700)
    :Example: 
        |    import datetime 
        |    week_ago = datetime.date.today() - datetime.timedelta(days=7)
        |    jobs = qb.jobinfo(submittedAfter=week_ago)

    :Example: jobs = qb.jobinfo(minid=1000, maxid=2000)
    :Example: jobs = qb.jobinfo(limit=100, orderby='id DESC')

    """
    # Maintain backwards compatibility [can specify as ordered args (fields, filters) or (filters)]
    if isinstance(fields, dict) and len(filters)==0:
        warnings.warn("Specifying jobinfo 'fields' first is deprecated "
                      "since reordering ordered parameters is inconsistant. "
                      "Please use fields=[...], filters={...}, agenda=True, subjobs=True, or callbacks=True.",
                      DeprecationWarning, stacklevel=2)
        filters = fields
        fields=[]
        
    # Convert the exposed commonly used filter params into the filter
    filters = filters.copy() # make sure to not affect original filter
    if id != None:        filters['id'] = id
    if status != None:    filters['status'] = status

    if minid != None: filters['minid'] = {"name": "id", "sign": ">=", "fields": [{"value": str(minid)}]}
    if maxid != None: filters['maxid'] = {"name": "id", "sign": "<=", "fields": [{"value": str(maxid)}]}

    # Convert the exposed commonly used fields params into the fields
    fields = fields[:] # copy list to make sure to not affect original fields
    if agenda    and not 'agenda'    in fields :   fields.append('agenda')
    if subjobs   and not 'subjobs'   in fields :   fields.append('subjobs')
    if callbacks and not 'callbacks' in fields :   fields.append('callbacks')

    opts = {};
    if limit != None: opts['limit'] = limit
    if orderby != None: opts['orderby'] = orderby

    if isinstance(updatedAfter, float):     updatedAfter    = int(updatedAfter)
    if isinstance(updatedBefore, float):    updatedBefore   = int(updatedBefore)
    if isinstance(submittedAfter, float):   submittedAfter  = int(submittedAfter)
    if isinstance(submittedBefore, float):  submittedBefore = int(submittedBefore)
    
    if isinstance(updatedAfter, (datetime, date)):     updatedAfter    = int(mktime(updatedAfter.timetuple()))
    if isinstance(updatedBefore, (datetime, date)):    updatedBefore   = int(mktime(updatedBefore.timetuple()))
    if isinstance(submittedAfter, (datetime, date)):   submittedAfter  = int(mktime(submittedAfter.timetuple()))
    if isinstance(submittedBefore, (datetime, date)):  submittedBefore = int(mktime(submittedBefore.timetuple()))

    # Handle time constraints/filters
    #    Using unix time converted to qb time
    #    NOTE: Could use BETWEEN if both before and after used
    if updatedAfter    != None and updatedAfter > 0:
        filters['updatedAfterFilter'] = {"name": "lastupdate", "sign": ">", "fields": [{"value": str(updatedAfter - QB_TIME_EPOCH_OFFSET)}]}
    if updatedBefore   != None and updatedBefore > 0:   
        filters['updatedBeforeFilter'] = {"name": "lastupdate", "sign": "<", "fields": [{"value": str(updatedBefore - QB_TIME_EPOCH_OFFSET)}]}
    if submittedAfter  != None and submittedAfter > 0:
        filters['submittedAfterFilter'] = {"name": "timesubmit", "sign": ">", "fields": [{"value": str(submittedAfter - QB_TIME_EPOCH_OFFSET)}]}
    if submittedBefore  != None and submittedBefore > 0:
        filters['submittedBeforeFilter'] = {"name": "timesubmit", "sign": "<", "fields": [{"value": str(submittedBefore - QB_TIME_EPOCH_OFFSET)}]}

    # print "filters=%s" % filters
    return [Job(i) for i in _qb.jobinfo(fields, filters, opts)]


def joborder(filters={}, name=None):
    """Get jobs running or scheduled to run on the host.
    
    :Parameters:
        filters : dict
            host properties to filter hosts acted upon.  See `Host` class properties for a full list of filters. (default={})
        name : str or [str]
            filter shortcut. name=val -> filters={'name': val }  (default=None)

    :Returns: [`Job`]
  
    :Example: jobs = qb.joborder(name='myhost')
    """
    if name != None:   filters['name'] = name
    return [Job(i) for i in _qb.joborder(filters)]


def hostorder(id=None):
    """Get list of hosts in the order that the system will likely assign the given job.
    
    :Parameters:
        id : int
            The jobID of the job we're interested in.

    :Returns: [`Host`]
  
    :Example: hosts = qb.hostorder(id=1234)
    """
    filters = {}
    if id != None:
        filters['id'] = id
    return [Host(i) for i in _qb.hostorder(filters)]


def hostinfo(fields=[], filters={}, name=None, state=None, subjobs=False):
    """Retrieve information from specified hosts.
    
    :Parameters:
        fields : list
            additional info to retrieve. See below. (default=[])

                - *Options*: subjobs

        filters : dict
            host properties to filter hosts acted upon.  See `Host` class properties for a full list of filters. (default={})
            
        name : str or [str]
            filter shortcut. name=val  -> filters={'name': val }   (default=None)
            
        state : str or [str]
            filter shortcut. state=val -> filters={'state': val }  (default=None)
            
        subjobs : bool
            field shortcut.  subjobs=True -> fields=['subjobs']    (default=False)

    :Returns: [`Host`]

    :Note: Hostinfo returned will not contain subjob info unless these parameters are specified.

    :Example: hosts = qb.hostinfo()               # all hosts
    :Example: hosts = qb.hostinfo(name='myhost')  # only host named myhost
    :Example: hosts = qb.hostinfo(state='down')  # only host that are active
    :Example: hosts = qb.hostinfo(subjobs=True)   # all hosts, include subjob info
    :Example: hosts = qb.hostinfo(filters={'name':'myhost'}) # host named 'myhost'
    :Example: hosts = qb.hostinfo(fields=['subjobs'])        # all hosts, include subjob info
    """
    # Maintain backwards compatibility [can specify as ordered args (fields, filters) or (filters)]
    if isinstance(fields, dict) and len(filters)==0:
        warnings.warn("Specifying hostinfo 'fields' first is deprecated "
                      "since reordering ordered parameters is inconsistent. "
                      "Please use fields=[...], filters={...}, or shortcuts",
                      DeprecationWarning, stacklevel=2)
        filters = fields
        fields=[]
    elif not isinstance(fields, list):
        raise ValueError('hostinfo(): Invalid type specified for first arg, "fields". Must be of type list')
        
    # Convert the exposed commonly used filter params into the filter
    filters = filters.copy() # make sure to not affect original filter
    if name  != None:  filters['name']  = name
    if state != None:  filters['state'] = state

    # Convert the exposed commonly used fields params into the fields
    fields = fields[:] # copy list to make sure to not affect original fields
    if subjobs and not 'subjobs' in fields:   fields.append('subjobs')
    
    # Perform action and return Hosts
    return [Host(i) for i in _qb.hostinfo(fields, filters)]


def recoverjob(filename):
    """Load `Job` from file.  
    
    :See: `archivejob`
    
    :Parameters:
        filename : str
            path to file containing saved Job

    :Returns: `Job` on success, None on failure
    
    :Example: loadedJob = qb.recoverjob('c:/myjob.xml')
    """
    loadedJob = _qb.recoverjob(filename)
    if isinstance(loadedJob, (dict, Job)): 
        return Job(loadedJob)
    else:
        warnings.warn("Failed to load job, returning 0 (deprecated).  In the future, an IOError exception will be thrown.", DeprecationWarning, stacklevel=1)
        return 0


def archivejob(filename, job, format=QB_API_XML):
    """Save `Job` to file.  

    :See: `recoverjob`
    
    :Parameters:
        filename : str
            file path to where to save Job.
            
        job : `Job` or dict
            Job to save
            
        format : int
            format to use for saving. (default: QB_API_XML)
            
                - *Options*: QB_API_XML, QB_API_BINARY

    :Returns: filesize in bytes (int)

    :Example: myjob = qb.jobinfo(id=277)[0]
    :Example: loadedJob = qb.archivejob('c:/myjob.xml', myjob)
    """
    # NOTE: These properties do not 100% match up with archive (result and data store display "(=)" if empty "" )
    if not isinstance(job, (Job, dict)):
        raise ValueError("Invalid type specified for job. Must be type Job or dict")
    return _qb.archivejob(filename, job, format)


def hist(jobid, *extraJobids):
    """Retrieve history list of specified jobid/jobid.subjob.
    
    :Parameters:
        jobid : int or str
            jobid or 'jobid.subjobid' to retrieve history for (additional jobids can be specified)

    :Returns:
        history ([dict])
            - *Note*: either subid or workid is specified, but not both. (value -1 used if not specified.)
            - jobid       -- Job id
            - subid       -- subjob id (int)
            - workid      -- task/frame id (int)
            - comment     -- String history event description
            - stamp       -- String date
            - timestamp   -- Int event time in seconds since the epoch

    :Example: loadedJob = qb.hist(250)      # retrieve all history for job 250
    :Example: loadedJob = qb.hist('250.0')  # retrieve history for job 250, subjob 0 only
    """
    return _qb.hist(jobid, *extraJobids)


def stats(subjobid, *extraSubjobids):
    """Retrieve stats list for specified jobid.subjobid.
    
    :Parameters:
        subjobid : str
            jobid or 'jobid.subjobid' to retrieve info for (additional subjobids can be specified)

    :Returns:
        Stats ([dict])
            - jobid       -- Job id (int)
            - subid       -- subjob id (int)
            - logtype     -- (undefined)
            - host        -- (undefined) 
            - data        -- stat info
            - id          -- (undefined)
            - cls         -- (undefined)

    :Note: if only jobid given, then method will return output for jobid.0. 

    :Example: qb.stats('250.0')  # retrieve stats for job 250, subjob 0 only
    """
    if str(subjobid).find('.') == -1 or len([i for i in extraSubjobids if (str(i).find('.') == -1)]) > 0:
        warnings.warn("Current functionality only returns output for subjob 0 when only job specified. This funcionality may change in the future.", RuntimeWarning, stacklevel=2)
    return _qb.stats(subjobid, *extraSubjobids)


#
# _get_log()
# 
def _get_log(*subjobids, **kwargs):
    '''helper routine that implements qb.stdout() and qb.stderr()'''
    pos = kwargs.pop('pos', 0)
    len = kwargs.pop('len', -1)
    logtype = (kwargs.pop('logtype', 'stdout'))

    subjobid_list = []
    # flatten the input list of subjob IDs
    for subjobid in subjobids:
        if isinstance(subjobid, list):
            subjobid_list.extend(subjobid)
        else:
            subjobid_list.append(subjobid)

    if logtype == "stdout":
        return _qb.stdout(subjobid_list, pos, len)
    elif logtype == "stderr": 
        return _qb.stderr(subjobid_list, pos, len)
    else:
        raise TypeError("unknown logtype[%s]" % logtype)


def stderr(*subjobids, **kwargs):
    '''Retrieve the list of stderr output of the specified range, for the specified subjob.
    
    :Parameters:
        subjobids : list of str
            a list of 'jobid.subjobid' for which to retrieve info
        
        pos : int
            position, in bytes, to start reading
            
        len : int
            length, in bytes, to read
        
    :Returns:
        output logs (dict)
            - jobid       -- Job id (int)
            - subid       -- subjob id (int)
            - data        -- log info (str)
            - fullsize    -- full size of the log file, in bytes (int)
    '''
    kwargs["logtype"] = "stderr"
    return _get_log(*subjobids, **kwargs)


def stdout(*subjobids, **kwargs):
    '''Retrieve the list of stdout output of the specified range, for the specified subjob.
    
    :Parameters:
        subjobids : list of str
            a list of 'jobid.subjobid' to retrieve info for
            
        pos :
            position, in bytes, to start reading
        
        len :
            length, in bytes, to read
         
    :Returns:
        output logs (dict)
            - jobid       -- Job id (int)
            - subid       -- subjob id (int)
            - data        -- log info (str)
            - fullsize    -- full size of the log file, in bytes (int)
            
    '''
    kwargs["logtype"] = "stdout"
    return _get_log(*subjobids, **kwargs)


def kill(jobid, *extraJobids):
    """Kills jobs or subjobs.
    
    :Parameters:
        jobid : int
            jobid to kill  (additional jobids can be specified)

    :Returns: 
        killed subjobs (['jobid.subjobid'])

    :Example: qb.kill(250)        # kill all subjobs under job 250
    :Example: qb.kill('250.0')    # kill only subjob 250.0
    """
    return _qb.kill(jobid, *extraJobids)


def retire(jobid, *extraJobids):
    """Force specified jobs to exit and set status to "complete" after each subjob completes its current Work items.

    :Note: Works on jobs that are not complete, killed, or failed.
    
    :Parameters:
        jobid : int
            jobid to retire (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid']) 

    :Example: qb.retire(250)
    """
    return _qb.retire(jobid, *extraJobids)


def top(jobid, *extraJobids):
    """Move specified jobs to the beginning of the execution order queue, within the same priority.
    
    :See: `joborder`, `bottom`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)
            
    :Returns:
        affected jobids ([int])

    :Example: qb.top(260)
    """
    return _qb.top(jobid, *extraJobids)


def bottom(jobid, *extraJobids):
    """Move specified jobs to the end of the execution order queue, within the same priority.
    
    :See: `joborder`, `top`.

    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)
            
    :Returns:
        affected jobids ([int])
  
    :Example: qb.bottom(250)      
    """
    return _qb.bottom(jobid, *extraJobids)


def migrate(jobid, *extraJobids):
    """Interrupt a running job/subjob and force it to run on a different host.
    
    :Parameters:
        jobid : int or str
            jobid or 'jobid.subjobid' to affect (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
        
    :Example: qb.migrate(250)    # migrate all subjobs for job 250
    :Example: qb.migrate('250.1')  # migrate subjob 250.1 to a different host
    """
    return _qb.migrate(jobid, *extraJobids)


def modify(modifyParamDict, jobid, *extrajobids):
    """Requests the supervisor to modify a list of jobs.

    :Parameters:
        modifyParamDict : dict
            items to modify (ie. {'priority':123})

            Modifiable Parameters:

                - priority
                - timeout
                - name
                - account
                - notes
                - cluster
                - restrictions
                - requirements
                - reservations
                - groups
                - hosts
                - omithosts
                - omitgroups
                - hostorder
                - pgrp
                - data
                - cpus
                - max_cpus
                - env
                - prod_show
                - prod_shot
                - prod_seq
                - prod_client
                - prod_dept
                - prod_custom1
                - prod_custom2
                - prod_custom3
                - prod_custom4
                - prod_custom5
                - preflights
                - postflights
                - agenda_preflights
                - agenda_postflights
            
        jobid : int
            jobid to affect (additional jobids can be specified)

    :Returns:
        affected jobids ([int])

    :Note: Only incomplete/active jobs can be modified.

    :Example: qb.modify({'priority':123}, 250)    # modify priority of job 250
    """
    return _qb.modify(modifyParamDict, jobid, *extrajobids)


def remove(jobid, *extraJobids):
    """Remove specified jobids from database.
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        affected jobids ([int])
    """
    return _qb.remove(jobid, *extraJobids)


def interrupt(jobid, *extraJobids):
    """Forces running jobs back to pending state without waiting for agenda items to finish.
    
    :See: `preempt`, `migrate`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.interrupt(jobid, *extraJobids)


def block(jobid, *extraJobids):
    """Set job state to blocked.
    
    :See: `unblock`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.block(jobid, *extraJobids)


def unblock(jobid, *extraJobids):
    """Set job state to pending.
    
    :See: `block`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.unblock(jobid, *extraJobids)


def preempt(jobid, *extraJobids):
    """Forces running jobs back to pending state after agenda item is completed.
    
    :See: `interrupt` and `migrate`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.preempt(jobid, *extraJobids)


def retry(jobid, *extraJobids):
    """Resets jobs in a terminal state (killed, failed, etc) back to a pending
    state.  Note that this command is very similar to the `requeue` command,
    with a subtle yet significant difference-- `requeue` puts the job in a
    "blocked" state, while `retry` puts it in a "blocked" state.

    :See: `requeue`, which does a similar thing, but puts the job in a "blocked" state.
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])

    """
    return _qb.retry(jobid, *extraJobids)


#def reset(jobid, *extraJobids):
#    """Resets jobs in a terminal state (killed, failed, etc) back to a it's original state.
#
#    :Change: In development (not released)
#
#    :See: `retry` and `requeue`
#    
#    :Parameters:
#        jobid : int
#            jobids to affect  (additional jobids can be specified)
#
#    :Returns:
#        list of affected subjobids (['jobid.subjobid'])
#    """
#    return _qb.reset(jobid, *extraJobids)



def requeue(jobid, *extraJobids):
    """Resets jobs in a terminal state (killed, failed, etc) back to a blocked
    state.  Note that this command is very similar to the `retry` command,
    with a subtle yet significant difference-- `retry` puts the job in a
    "pending" state, while `requeue` puts it in a "blocked" state.

    :See: `retry`, which does a similar thing, but puts the job in a "pending" state.
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])

    """
    return _qb.requeue(jobid, *extraJobids)


def suspend(jobid, *extraJobids):
    """Sends SUSPEND signal (unix suspend) to specified running jobs. (Linux Workers only)

    :See: `resume`
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.suspend(jobid, *extraJobids)


def resume(jobid, *extraJobids):
    """Return suspended (unix) jobs to specified running jobs.  (Linux Workers only)

    :See: `suspend`.
    
    :Parameters:
        jobid : int
            jobids to affect  (additional jobids can be specified)

    :Returns:
        list of affected subjobids (['jobid.subjobid'])
    """
    return _qb.resume(jobid, *extraJobids)


def killwork(workid, *extraWorkids):
    """Kills specified frames/tasks. 
    
    :See: `kill`.
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: killwork('250:0')
    :Example: killwork('250:0', '250:1')
    """
    return _qb.killwork(workid, *extraWorkids)


def retirework(workid, *extraWorkids):
    """Retire specified frames/tasks and set their status to "complete". 

    :Since: Qube 5.3.
    :Note: Works on frames/tasks that are not complete, killed, or failed.
    :See: `retire`.
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: retirework('250:0')
    :Example: retirework('250:0', '250:1')
    """
    # Sanity checks -- make sure that a string (not a list) is being passed in
    if not isinstance(workid, str):
        raise TypeError("Requires workid parameter of type string")
    
    return _qb.retirework(workid, *extraWorkids)


def blockwork(workid, *extraWorkids):
    """Sets specified pending frames/tasks to blocked state.

    :See: `unblockwork`.
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: blockwork('250:0')
    :Example: blockwork('250:0', '250:1')
    """
    return _qb.blockwork(workid, *extraWorkids)


def unblockwork(workid, *extraWorkids):
    """Sets specified blocked frames/tasks to pending state.
    
    :See: `unblockwork`
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: unblockwork('250:0')
    :Example: unblockwork('250:0', '250:1')
    """
    return _qb.unblockwork(workid, *extraWorkids)


def retrywork(workid, *extraWorkids):
    """Resets specified terminal frames/tasks (failed, killed, etc) to pending state.
    Return affected tasks/work items.
    
    :See: `requeuework`
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: retrywork('250:0')
    :Example: retrywork('250:25-29')
    :Example: retrywork('250:0', '250:1')
    """
    return _qb.retrywork(workid, *extraWorkids)


def requeuework(workid, *extraWorkids):
    """Resets specified terminal frames/tasks (failed, killed, etc) to blocked state.

    :See: `retrywork`.
    
    :Parameters:
        workid : str
            task/frame specifier 'jobid:workname' (additional workids can be specified)

    :Returns:
        affected tasks/work items (['jobid:workname'])

    :Example: requeuework('250:0')
    :Example: retrywork('250:25-29')
    :Example: requeuework('250:0', '250:1')
    """
    return _qb.requeuework(workid, *extraWorkids)


def submit(*jobs, **kwargs):
    """Submit a job or list of jobs to the Supervisor.
    
    :Parameters:
        jobs : `Job` or dict
            job properties to submit (additional Jobs or lists of Jobs can be specified)
       deferTableCreation : bool
            whether the supervisor should defer the creation of DB tables
            [default = True]
    
    :Returns:
        list of submitted jobs ([Job])

    :Example: Simple submission to run "set" command
      ::
      
        myjob = qb.Job()
        myjob['name']      = 'test submit'
        myjob['prototype'] = 'cmdline'
        myjob['package']   = {'cmdline' : 'set' }
        qb.submit(myjob)     # returns a [Job()]

    :Example: Simple multi-frame submission to echo the frame number
      ::
      
        myjob = qb.Job()
        myjob['name']      = 'test cmdrange submit'
        myjob['prototype'] = 'cmdrange'
        myjob['package']   = {'cmdline' : 'echo "Frame QB_FRAME_NUMBER"',
                              'padding' : 0,
                              'range'   : '1-10',  #QubeGUI uses this if present
                             }
        myjob['agenda']    = qb.genframes(myjob['package']['range'])
        qb.submit(myjob)     # returns a [Job()]
        
    :Example: Simple per-job multiple dependency example
      ::
        
        myjob = qb.Job(name='dependency test', prototype='cmdline', package={'cmdline' : 'set' })
        job1 = qb.submit(myjob)[0]
        job2 = qb.submit(myjob)[0]
        myjob3 = qb.Job(name='dependency test (waitfor)', prototype='cmdline', package={'cmdline' : 'set' })
        myjob3['dependency'] = "%i,%i" % (job1.id(), job2.id())
        job3 = qb.submit(myjob3)[0]  # returns a Job() that will run after job1 and job2 complete
    """
    deferTableCreation = kwargs.pop('deferTableCreation', True)

    # create single list of jobs from mixed arguments of jobs and lists of jobs
    # Shallow copy jobs so not to modify original values (note: does not deep copy package)
    joblist = []
    for job in jobs:
        if isinstance(job, list):
            joblist.extend([Job(i) for i in job])
        else:
            joblist.append(Job(job))

    # loop over items and add additional info
    for job in joblist:        
        # Check for valid types
        if not isinstance(job, (Job, dict)):
            raise ValueError("Invalid type: arguments need to be of type Job or dict")

        # Handle submit-specific parameters 
        # Timelimit 
        if 'timelimit' in job:    
            job['timeout'] = job['timelimit']
            if 'callbacks' not in job:  job['callbacks'] = [] 
            job['callbacks'].append({
                    "triggers" : "timeout-subjob-self-*",
                    "language" : "qube",
                    "code" : "fail-subjob-self"
                    })

        # Agenda Timelimit
        if 'agenda_timelimit' in job:    
            job['agenda_timeout'] = job['agenda_timelimit']
            if 'callbacks' not in job:  job['callbacks'] = [] 
            job['callbacks'].append({
                    "triggers" : "timeout-work-self-*",
                    "language" : "qube",
                    "code" : "fail-work-self"
                    })

        # Waitfor(s)
        if 'waitfor' in job and len(str(job['waitfor']))>0: # int
            warnings.warn("The 'waitfor' parameter is deprecated. Adding value to preferred 'dependency' parameter.", DeprecationWarning, stacklevel=2)
            if 'dependency' not in job:
                job['dependency'] = ''
            # Set initial state to blocked
            depStr = 'link-done-job-%s' % job['waitfor']
            if len(job['dependency']) > 0:
                job['dependency'] += ','+ depStr
            else:
                job['dependency'] = depStr

    # Submit to the Supervisor
    jobs_submitted = _qb.submit(joblist, deferTableCreation)
    if jobs_submitted == False:
        raise ValueError(error())
    return [Job(i) for i in jobs_submitted]

## ==========================================================================================
##
## SUBMIT UTILITIES
##
## ==========================================================================================

def rangesplit(range, *extraRanges, **kwargs):
    """Convert a frame range into a list of frames.
    Automatically removes duplicate items in the list by default.
        
    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    :Change: Removes duplicates by default (Qube 6.2)
    :Change: Added "removeDuplicates" keyword option for Qube 6.2 [default=True]
    
    :Parameters:
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order
            [default = False]
        removeDuplicates : bool
            remove duplicates in the returned list
            [default = True]
    
    :Returns:
        List of range strings ([str])
    
    """
    # Tokenize range items by ","
    ranges = []
    for r in [range]+list(extraRanges):
        ranges.extend( [i.strip() for i in r.split(',') if i != '']) # split by comma and remove leading and trailing spaces)

    # for each item, if matches numbering pattern, then call rangesplit(), otherwise keep as-is
    sequencePattern = re.compile(r'[0-9\-]+($|-[0-9\-]+($|x[0-9\-]+))')   # matches 1, -1, 1-10, -1--10, 1-10x2
    results = []
    for r in ranges:
        if re.match(sequencePattern, r): # match a sequence: 1, -1, 1-10, -1--10, 1-10x2
            results.extend( _qb.rangesplit(r) )
        else: # not a sequence, keep as-is
            results.append( r )
    
    # Remove duplicates (if specified)
    if kwargs.get('removeDuplicates', True) == True:
        # remove dups (preserve order)
        tmpUniq = {} # temp variable used below 
        results = [tmpUniq.setdefault(i,i) for i in results if i not in tmpUniq] # setdefault() returns the value as well so can be used to add items to the list and to the unique dict

    # Sort (if specifed)
    if kwargs.get('binarySort', False) == True:
        results = binarySort(results)  # perform binary sort if requested (binary=False by default)

    # Return results
    return results


def rangechunk(chunksize, range, *extraRanges, **kwargs):
    """Splits frame range chunks each with <n> frames.
    Automatically removes duplicate items in the list.
    
    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    
    :Parameters:
        chunksize : int
            number of frames per chunk
            
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order (default=False)
    
    :Returns:
        List of range strings ([str])
        
    :Example: qb.rangechunk(5, '1-10')  
    :Example: qb.rangechunk(5, '-100--1')
    :Example: qb.rangechunk(5, '1-20', binarySort=True)
    """
    # Tokenize range items by ","
    ranges = []
    for r in [range]+list(extraRanges):
        ranges.extend( [i.strip() for i in r.split(',')] ) # split by comma and remove leading and trailing spaces)

    # for each item, if matches numbering pattern, then call rangesplit(), otherwise keep as-is
    # Group sequences together and literals together so chunking can be most efficient

    # matches 1, -1, 1-10, -1--10, 1-10x2. Whitespace is allowed before/after
    # tokens, such as " -1 - -10 x 3" (but not before unary "-")
    sequencePattern = re.compile(r'[0-9\-]+($|\s*-\s*[0-9\-]+($|\s*x\s*[0-9\-]+))')

    results = []
    rangeSequences = []
    for r in ranges:
        if re.match(sequencePattern, r): # match a sequence: 1, -1, 1-10, -1--10, 1-10x2
            rangeSequences.append( r )
        else: # not a sequence, keep as-is
            results.append( r )
    # Perform chunking on the sequence items
    results.extend( _qb.rangechunk(int(chunksize), *rangeSequences) ) # NOTE: _qb.rangechunk() Auto-removes dups
    
    # Sort (if specifed) and then return
    if kwargs.get('binarySort', False) == True: results = binarySort(results)  # perform binary sort if requested (binary=False by default)
    return results


def rangepartition(numPartitions, range, *extraRanges, **kwargs):
    """Split frame range into <n> partitions.
    Automatically removes duplicate items in the list.

    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    
    :Parameters:
        numPartitions : int
            number of partitions to split the range into
            
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order (default=False)
    
    :Returns:
        List of range strings ([str])
        
    :Example: qb.rangepartition(2, '1-10') 
    :Example: qb.rangepartition(2, '-100--1') 

    """
    frames = rangesplit(range, *extraRanges)
    if numPartitions < 1:
        results = frames
    else:
        # determine chunk size
        chunksize = len(frames) / numPartitions
        # if there is a fractional part, then increase chunksize by 1
        if (len(frames) % numPartitions) > 0:
            chunksize += 1
        results = rangechunk(chunksize, range, *extraRanges) # NOTE: rangechunk() Auto-removes dups

    if kwargs.get('binarySort', False) == True: results = binarySort(results)  # perform binary sort if requested (binary=False by default)
    return results


def genframes(range, *extraRanges, **kwargs):
    """Generate a work agenda (individual Work items) based upon range list.
    Automatically removes duplicate items in the list by default.

    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    :Change: Removes duplicates by default (Qube 6.2)
    :Change: Added "removeDuplicates" keyword option for Qube 6.2 [default=True]
    
    :Parameters:
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order
            [default = False]
        removeDuplicates : bool
            remove duplicates in the returned list
            [default = True]
    
    :Returns: list of `Work` instances. ([`Work`])
    
    :Example: qb.genframes('1-10x2')
    :Example: qb.genframes('-10--1x2')
    :Example: qb.genframes('ls,set,echo HI')
    """
    return [Work({'name':i}) for i in rangesplit(range, *extraRanges, **kwargs)]


def genchunks(chunksize, range, *extraRanges, **kwargs):
    """Generate a work agenda (individual Work items) in frame chunks based upon range list.
    Automatically removes duplicate items in the list.

    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    
    :Parameters:
        chunksize : int
            number of frames per chunk
            
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order (default=False)
    
    :Returns: list of Work instances. ([`Work`])
    
    :Example: qb.genchunks(10, '1-100')
    :Example: qb.genchunks(10, '-100--10')
    """
    return [Work({'name':i}) for i in rangechunk(chunksize, range, *extraRanges, **kwargs)]


def genpartitions(numPartitions, range, *extraRanges, **kwargs):
    """Generate a work agenda (individual Work items) based upon range list splitting frame range into <n> partitions.
    Automatically removes duplicate items in the list.

    :See: `rangesplit`, `rangechunk`, `rangepartition`
    :See: `genframes`, `genchunks`, `genpartitions`
    :Change: Added "binarySort" keyword option for Qube 5.3
    
    :Parameters:
        numPartitions : int
            number of partitions to split the range into
            
        range : str
            Frame range string (additional ranges can be specified)
    
                - n1                                       (ie.  1)
                - n1,n2,...   -- comma separated list      (i.e. 1,2,3,5,10)
                - n1-n2       -- n1 through n2             (i.e. 1-10)
                - n1-n2xStep  -- n1 through n2, step Step  (i.e. 1-10x2)

    :Keywords:
        binarySort : bool
            perform a binary sort (first, last, middle) on the resulting order (default=False)
    
    :Returns: list of Work instances. ([`Work`])
    
    :Example: qb.genpartitions(2, '1-10') 
    :Example: qb.genpartitions(2, '-10--1') 
    """
    return [Work({'name':i}) for i in rangepartition(numPartitions, range, *extraRanges, **kwargs)]


def binarySort(origList):
    """Return a new list reordered with first, last, and then the recursed median values for the remaining items.

    :Since: Qube 5.3.
        
    :Parameters:
        origList : list
            original list to be sorted

    :Returns: new sorted list
    
    :Example: qb.binarySort([1,2,3,4,5,6,7,8,9,10]) 
    """
    if len(origList) < 2:
        return origList[:] # return copy of original list values unless list has more than 2 items
    else:
        # Helper function that returns a list reordered by the recursed median values of the lists
        # Embedded in the binarySort so that this helper function is not overtly exposed
        def calculateMedianValues(theLists):
            """
            Return a list reordered by the recursed median values of the lists
            """
            mids = []
            newLists = []
            for aList in theLists:
                if len(aList) > 0:
                    midIndex = (len(aList)-1)//2
                    newLists.append(aList[:midIndex])
                    mids.append( aList[midIndex] )
                    newLists.append(aList[midIndex+1:])
            if len(newLists) > 0: mids.extend( calculateMedianValues(newLists) )
            return mids
        # Add the first, last, and then recursed median values
        sortedList = [origList[0], origList[-1]]
        sortedList.extend( calculateMedianValues([origList[1:-1]]) )
        return sortedList
    
    
def updatepassword(user=None, password=None, domain=None):
    """Update supervisor with new Windows password information for a Windows user.
    
    :Parameters:
        user : str
            username
            
        password : str
            new password
            
        domain : str
            Windows domain
            
    :Returns: (bool)  True on success, False on failure

    :Compatibility:
        - For backwards compatibility, handle reordering of arguments.
        - *option1*: (password)
        - *option2*: (user, password)
        - *option3*: (user, password, domain)
    """
    if user != None and password != None and domain != None:
        return _qb.updatepassword(user, password, domain) == True
    elif user != None and password != None:
            return _qb.updatepassword(user, password) == True
    elif user != None and password == None: # reorder since password is required, not name
            password = user
            return _qb.updatepassword(password) == True
    else:
        raise ValueError("Need to specify a password")
    return False


def checkpassword():
    """Check for valid password of current user. [Windows only]
    
    :Returns: success of valid password (bool)
    """
    return _qb.checkpassword()


## ==========================================================================================
##
## JOBTYPE BACKEND AND CALLBACK FUNCTIONS
##
## ==========================================================================================

def _init_assign():
    """Backend routine to manually fetch job information (assignment) into the current execution context. (jobtype backend)

    :Since: Qube 5.3.
    """
    return _qb._init_assign()


def _assignment(*args):
    """Proxy routine (internal use only)
    """
    return _qb._assignment(*args)


def _setjob(archivefile):
    """Used to short-circuit need for Supervisor (jobtype backend)
    See Developer documentation and examples scripts.

    :Parameters:
        archivefile
            load a job archive file as the current job.
    """
    return _qb._setjob(archivefile)


def jobid():
    """Get the job's id for the job process (jobtype backend)

    :Since: Qube 5.3.
    
    :See: Developer docs for information on usage.
    """
    return _qb.jobid()


def subid():
    """Get the job's subjob id for the job process (jobtype backend)

    :Since: Qube 5.3.
    
    :See: Developer docs for information on usage.
    """
    return _qb.subid()


def jobobj():
    """Get a dict for the job to process (jobtype backend)
    
    :See: Developer docs for information on usage.
    """
    return _qb.jobobj()


def requestwork():
    """Ask supervisor for work agenda items (jobtype backend)
    
    :See: Developer docs for information on usage.
    """
    return _qb.requestwork()


def reportwork(*args):
    """Returns updated work agenda items to the supervisor (jobtype backend)
    
    :See: Developer docs for information on usage.
    """
    return _qb.reportwork(*args)


def reportjob(*args):
    """Return updated job status to supervisor (jobtype backend)
    
    :See: Developer docs for information on usage.
    """
    return _qb.reportjob(*args)


def workerpathmap():
    """Return the current worker's worker pathmap (jobtype backend)

    :See: Developer docs for information on usage.
    """
    return _qb.workerpathmap()


def convertpath(*args):
    """convert the given path to be suitable for the current worker, using the worker's pathmap

    :See: Developer docs for information on usage.
    """
    return _qb.convertpath(*args)

## ==========================================================================================
##
## SUPERVISOR FUNCTIONS
##
## ==========================================================================================


def version():
    """Returns version number for qube."""
    return _qb.version()

def settimeout(timeout):
    """Set the client timeout (in milliseconds).

    :Since: Qube 5.3.

    :Parameters:
        timeout : int 
            length of timeout in milliseconds
    """
    return _qb.settimeout(timeout)


def gettimeout():
    """Returns the current client timeout setting in milliseconds

    :Since: Qube 5.3.
    """
    return _qb.gettimeout()


def setlogpath(logpath):
    """Set the client logpath to access the job logs directly.
    Set to '' to use the default logpath specified in the config file.
    Set to 'USE_SUPERVISOR' to force the queries to ignore local access and
    retrieve data directly from the Supervisor.

    :Since: Qube 5.5.

    :Parameters:
        logpath : str 
            directory path to the qube log
    """
    return _qb.setlogpath(logpath)


def getlogpath():
    """Returns the client logpath (used to access the job logs directly).
    If the logpath override is '', then return the logpath specified in the
    config file.
    If the logpath override is 'USE_SUPERVISOR', then force the queries to
    ignore local access and retrieve data directly from the Supervisor.

    :Since: Qube 5.5.
    """
    return _qb.getlogpath()


def setsupervisor(supervisor):
    """Set the supervisor to use.

    :Parameters:
        supervisor : str
            hostname or IP address of supervisor. '' means use default supervisor specified in qb.conf.
    """
    return _qb.setsupervisor(supervisor)


def getsupervisor():
    """Returns the hostname or IP address of the current supervisor ('' means use default supervisor specified in qb.conf).
    """
    return _qb.getsupervisor()


def error():
    """Return the error reason.

    :Since: Qube 5.3.
    """
    return _qb.error()


def ping(supervisor=None, asDict=False):
    """Ping the current or specified Supervisor to confirm it is present and available.

    :Change: Added "supervisor" and "asDict" keyword options for Qube 5.5

    :Change: (Qube 6.0.1) Added hostid (MAC Address) for the Supervisor
        right after the IP Address, as done with `workerping`.  Dict item 'macaddress' added.

    :Parameters:
        supervisor : str or None
            Specify the explicit Supervisor to ping.
            If None value specified, then use the current default supervisor for the given machine            
        asDict : bool
            return a dict containing details on the supervisor ping
    """
    s = _qb.ping(supervisor)
    if asDict == False:
        return s
    else:
        if len(s) == 0: return {}  # unable to ping supervisor
        a = s.split()
        d = {}
        d['address']   = a[0]
        d['macaddress'] = a[1]
        d['version']   = a[2]
        d['build']     = a[3]
        d['os']        = a[4]
        d['license_model'] = a[7]
        d['license_type'] = a[10]
        #d['licenses']  = a[9]
        lics = a[9].split('/')
        d['licenses_used']  = int(lics[0])
        d['licenses'] = int(lics[1])
        if(len(a) > 12):
            p = re.compile('\(metered=(\d+)/(-?\d+)\)')
            m = p.match(a[12])
            d['metered_used'] = int(m.group(1))
            d['metered_max'] = int(m.group(2))
            d['mode'] = int(a[14].split('=')[1])
            p = re.compile('\((.*)\)')
            m = p.match(a[15])
            d['mode_string'] = m.group(1)
        else:
            d['metered_used'] = 0
            d['metered_max'] = 0
            d['mode'] = 0
            d['mode_string'] = ""
        return d


def workerping(worker, asDict=False):
    """Ping the specified Worker to confirm it is present and available.

    :Since: Qube 5.5

    :Parameters:
        worker : str
            Specify the explicit IP address or hostname of the Worker to ping.
        asDict : bool
            return a dict containing details on the ping
    """
    s = _qb.workerping(worker)
    if asDict == False:
        return s
    else:
        if len(s) == 0: return {}  # unable to ping worker
        a = s.split()
        d = {}
        d['address']   = a[0]
        d['macaddress']= a[1]
        d['version']   = a[2]
        d['build']     = a[3]
        d['os']        = a[4]
        return d


def waitfor(post, timeout):
    """Wait for a specific event.
    This is useful for waiting for a specific event, to allow external scripts to wait for jobs before progressing.

    :Since: Qube 5.3.
    """
    return _qb.waitfor(post, timeout)

def currenttime():
    """get the current timestamp from the supervisor.
    This is useful for determining time offset from local clock and supervisor clock.
    """
    return _qb.currenttime()


def jobconfig(jobtype, parameter):
    """Return specified paramaeter value from job.conf.

    :Parameters:
        jobtype : str
            jobtype for the parameter
        parameter : str
            name of parameter to retrieve
    
    :Return: parameter value
    """
    return _qb.jobconfig(jobtype, parameter)

def jobtypeavailable(jobtypepath):
    """Return the list of available jobtypes on current host system.
    
    :Parameters:
        jobtypepath : str
            path to the jobtypes
    
    :Return: list of available jobtypes on current host system ([str])

    """
    return _qb.jobtypeavailable(jobtypepath)


def workerlock(filters={}, lockingString='', name=None, lock=None, purge=False):
    """Sets the locking string for machines used as Workers.

    :Parameters:
        filters : dict
            properties to filter the workers to lock/unlock.  Valid keys=['name'] (default={})
        
        lockingString : str
            comma-separated string used to control lock behavior of host. (default='')
            
            - *Options*:
            
                - host.processor_all=<val>  -- specify action for all the processors
                - host.processor_<#>=<val>  -- specify action for processor n
                - host.lock_mode=aggressive -- immediately purge running jobs off of processors locked

            - *Locking values <val>*:
            
                - For Off/On use: 0=Off, 1=On
                
                - For Watchdog (Windows only): (delay is minutes before idle)::
                
                    watchdog <delay>
                    
                - For Scheduling, use the week calendar to specify timeslots per hour (starts with Sunday)::
                
                    weekcalendar {
                        0 '0' '0' '0' '0' '0' '0' '0'
                        1 '0' '0' '0' '0' '0' '0' '0'
                        2 '0' '0' '0' '0' '0' '0' '0'
                        3 '0' '0' '0' '0' '0' '0' '0'
                        4 '0' '0' '0' '0' '0' '0' '0'
                        5 '0' '0' '0' '0' '0' '0' '0'
                        6 '0' '0' '0' '0' '0' '0' '0'
                        7 '1' '1' '1' '1' '1' '1' '0'
                        8 '1' '1' '1' '1' '1' '1' '0'
                        9 '1' '1' '1' '1' '1' '1' '0'
                        10 '1' '1' '1' '1' '1' '1' '0'
                        11 '1' '1' '1' '1' '1' '1' '0'
                        12 '1' '1' '1' '1' '1' '1' '0'
                        13 '1' '1' '1' '1' '1' '1' '0'
                        14 '1' '1' '1' '1' '1' '1' '0'
                        15 '0' '0' '0' '0' '0' '0' '0'
                        16 '0' '0' '0' '0' '0' '0' '0'
                        17 '0' '0' '0' '0' '0' '0' '0'
                        18 '0' '0' '0' '0' '0' '0' '0'
                        19 '0' '0' '0' '0' '0' '0' '0'
                        20 '0' '0' '0' '0' '0' '0' '0'
                        21 '0' '0' '0' '0' '0' '0' '0'
                        22 '0' '0' '0' '0' '0' '0' '0'
                        23 '0' '0' '0' '0' '0' '0' '0'
                        }

        name : str
            filter shortcut.  name='myhost' -> filters={'name':'myhost'}

        lock : bool
            lockingString shortcut.  lock=False/True -> lockingString='host.processor_all=0/1'

        purge : bool
            lockingString shortcut.  purge=True -> lockingString += ',host.lock_mode=aggressive'

    :Return: hostnames of affected machines ([str])
        
    :Example: qb.workerlock(name='myhost', lock=True)  # locks 'myhost'
    :Example: qb.workerlock(name='myhost', lock=True, purge=True) # locks 'myhost' and purges running jobs from host
    :Example: qb.workerlock(name='myhost', lock=False) # unlock 'myhost'
    :Example: qb.workerlock(lockingString='host.processor_0=1,host.processor_1=1', name='myhost')
    :Example: qb.workerlock(lockingString='host.processor_all=0', name='myhost') # unlocks 'myhost'
    :Example: qb.workerlock(lockingString='host.processor_all=1', name='myhost') # locks 'myhost'
    :Example: qb.workerlock(lockingString='host.lock_mode=aggressive,host.processor_all=watchdog 30', name='myhost')
    """
    # Set and check filters
    if name != None:
        filters = filters.copy()  # use a copy so as not to modify the original
        filters['name'] = name
    if 'name' not in filters:
        raise TypeError("The workerlock() function needs 'name' specified as either keyword argument or filter key")
    
    # Set and check lockingString
    if lock != None:
        if len(lockingString) > 0:
            raise TypeError("The workerlock() function not have both 'lockingString' and 'lock' shortcut set")
        lockingString = 'host.processor_all=%i' % lock
    if len(lockingString) == 0:
        raise TypeError("The workerlock() function needs 'lockingString' specified either directly or by 'lock' shortcut bool")
    if purge == True:
        lockingString = "host.lock_mode=aggressive,"+lockingString
    
    # Execute command
    hostnames = _qb.workerlock(filters, lockingString)
    return hostnames


def shove(jobid, *extraJobids):
    """Force the re-evaluation of a pending job for running on Workers

    :Since: Qube 5.5

    :Parameters:
        jobid : int
            jobids to affect (additional jobids can be specified)

    :Returns:
        list of affected jobids (['jobid'])
        
    :Example: qb.shove(250)    
    """
    return _qb.shove(jobid, *extraJobids)


#
# Functions in development (Not released)
#
#def command(cmd, *result):
#    """Execute command
#
#    :Change: In development (not released)
#    
#    :Parameters:
#        cmd : str
#            command  
#
#    :Returns: 
#        result
#
#    """
#    return _qb.command(cmd, *result)
#
#
def admincommand(cmd, *result):
   """Execute admincommand
   
   :Parameters:
       cmd : str
           the admincommand to execute

   :Returns: 
       result
       
   :Change: In development (not released)
   """
   return _qb.admincommand(cmd, *result)


# TODO: edit supervisor qbwrk.conf remotely
# TODO: edit supervisor qb.conf remotely
# TODO: edit local qb.conf (see updatelocalconfig)
# TODO: look into command and admincommand for other functionality

def workerconfig(name):
    """Query the configuration of the specified Worker

    :Since: Qube 5.5
    
    :Returns:
        dict of parameters

    """
    return _qb.workerconfig(name)


def supervisorconfig():
    """Query the configuration of the current Supervisor
    
    :Since: Qube 5.5

    :Returns:
        dict of parameters

    """
    return _qb.supervisorconfig()


def localconfig():
    """Query the configuration of the local machine.

    :Since: Qube 5.5
    :See: `updatelocalconfig`
    
    :Returns:
        dict of parameters

    """
    return _qb.localconfig()


def updatelocalconfig(configDict, auth=True):
    """Saves the specified config parameters to local qb.conf file.
    Automatically prompt for authentication as needed on OSX.

    :Since: Qube 5.5
    :See: `localconfig`

    :Parameters:
        configDict : dict
            dict of configuration string parameters
        auth : bool
            allow authentication dialog to prompt for Administrator password as needed (OSX only)
            
    :Returns: 
        success (bool)
        
    """
    # Get config template from existing qb.conf
    configTemplate = ""
    if os.path.isfile(QB_CLIENT_DEFAULT_CONF):
        try:
            f = open(QB_CLIENT_DEFAULT_CONF, 'r')
            configTemplate = f.read()
            f.close()
        except:
            return False

    # Get the current list of properties as they will be commented out unless they are in the dict
    configDictOfStr = localconfig()  
    # Convert all values to strings, or call configDictToStr will fail
    configDictOfStr.update( dict([(k,str(v)) for k,v in configDict.items()]) )
    # Cull out blank entries
    configDictOfStr = dict([(k,v) for k,v in configDictOfStr.items() if (v!='')])

    # Determine new config str
    confStr = _qb.configDictToStr(configDictOfStr, configTemplate)

    # Write as new qb.conf
    if auth==True and sys.platform == 'darwin': # for OSX
        import subprocess
        p = subprocess.Popen(["/usr/libexec/authopen", "-w", "-c", QB_CLIENT_DEFAULT_CONF],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        p.stdin.write(confStr)
        p.stdin.close()
        result = p.wait()
        if result != 0:
            return False
    else: # standard write file
        try:
            f = open(QB_CLIENT_DEFAULT_CONF, 'w')
            f.write(confStr)
            f.close()
        except IOError:
            return False
    
    # Return success
    return True

def qbadmin_reconfigureworkers():
    """Performs call same as "qbadmin worker --reconfigure" to push
    out new qbwrk.conf to all workers
    
    :Note: This command requires qube 'admin' permissions to work. 

    :Returns: 
        success (bool)
    """
    return _qb.admincommandstr("update_workers")


# TODO: Consider calling this update_qbwrk or updatecentralworkerconfig
def updateworkerconfig(configDict, hostnames, auth=True):
    """Saves the specified config parameters to local qbwrk.conf file.
    This should be run on the Supervisor machine only.
    Automatically prompt for authentication as needed on OSX.
    
    One should call `qbadmin_reconfigureworkers` after this file has
    been updated to push out the configuration.

    :Since: Qube 5.5
    :Note: Must be run from Supervisor machine.
    :See: qbadmin_reconfigureworkers

    :Parameters:
        configDict : dict
            dict of configuration string parameters
        hostnames : list
            list of Worker hostnames to update with these values
        auth : bool
            allow authentication dialog to prompt for Administrator password as needed (OSX only)
            
    :Returns: 
        success (bool)
        
    """
    # Get config template from existing qb.conf
    configTemplate = ""
    if os.path.isfile(QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE):
        try:
            f = open(QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE, 'r')
            configTemplate = f.read()
            f.close()
        except:
            return False

    # === Read in existing qbwrk.conf ===

    #  A container for any commented-out lines that will appear before the first
    #  template line 
    hdrTemplateName = '...header...'

    # Break into sections
    configSections = {hdrTemplateName: {'data': []}}
    configTemplateLines = configTemplate.splitlines()

    # this 'key' variable (awful name...) will get reset at the first encounter
    # with a valid template
    key = hdrTemplateName
    for line in configTemplateLines:
        if  len(line) == 0:
            continue
        # skip commented lines if we've already encountered a valid template,
        # which caused 'key' to be set to something other than its initialized
        # value
        if line.startswith('#') and key != hdrTemplateName:
            continue

        g = re.match(r'^\[(.+)\](.*)', line)
        if g != None:
            key = g.group(1)
            configSections[key] = {'data':[], 'inheritanceLine':g.group(2)}
        else:
            configSections[key]['data'].append(line)

    # Convert [str] to str for the configSections
    for k,v in list(configSections.items()):
        configSections[k]['data'] = '\n'.join(v['data'])

    for h in hostnames:
        workerConfTemplate = configSections.get(h, {'data':''})['data']
        # Get the current list of properties as they will be commented out unless they are in the dict
        configDictOfStr = _qb.configStrToDict(workerConfTemplate)
        # Convert all values to strings, or call configDictToStr will fail
        configDictOfStr.update( dict([(k,str(v)) for k,v in configDict.items()]) )
        # Cull out blank entries
        configDictOfStr = dict([(k,v) for k,v in configDictOfStr.items() if (v!='')])
    
        # Determine new config str
        configSections.setdefault(h, {})  # make sure there is a dict entry
        configSections[h]['data'] = _qb.configDictToStr(configDictOfStr, workerConfTemplate)        
        configSections[h]['data'] = configSections[h]['data'].replace('# these are not included in the template\n', '')
        configSections[h]['data'] = configSections[h]['data'].strip()
        configSections[h]['inheritanceLine'] = ''  # clear the inheritance line since overriding the data

        # Remove if data for hostname is empty
        # NOTE: Commenting out as this should not be reached (since template just comments out unexposed values)
        #if configSections[h] == '':
        #    del configSections[h]

    # Construct the "confStr" to save as qbwrk.conf
    magicTemplateNames = [hdrTemplateName, 'linux', 'winnt', 'osx']
    magicTemplateNames.sort()

    sortedSectionKeys = [x for x in list(configSections.keys()) if x not in magicTemplateNames]
    sortedSectionKeys.sort()
    confStrLines = []

    # write the file header
    fileHeader = configSections[hdrTemplateName]['data']
    if len(fileHeader):
        confStrLines.append('%s\n' % fileHeader)
    magicTemplateNames.pop(magicTemplateNames.index(hdrTemplateName))

    # write the 'linux', 'osx', and 'winnt' templates
    wroteMagicTemplate = False
    for templateName in magicTemplateNames:
        if templateName in configSections:
            if len( configSections[templateName].get('inheritanceLine', '')):
                warnMsg = '"[%s]" template currently inherits from %s.\n' %  (templateName, configSections[templateName]['inheritanceLine'])
                warnMsg += 'This is not supported with by this API function. Please edit the qbwrk.conf file by hand.\n'
                warnMsg += 'Stripping inheritance from the "[%s]" template.' % templateName
                warnings.warn(warnMsg, SyntaxWarning)

            confStrLines.append('[%s]' % templateName)
            confStrLines.append(configSections[templateName].get('data', ''))
            confStrLines.append('')        
            wroteMagicTemplate = True
        
    if wroteMagicTemplate:
        confStrLines.append('# end of OS-specific templates')
        confStrLines.append('%s%s' % ('#'*40, '\n'))

    for k in sortedSectionKeys:
        confStrLines.append('[%s]%s'%(k, configSections[k].get('inheritanceLine', '')))
        confStrLines.append(configSections[k].get('data', ''))
        confStrLines.append('')        
    confStr = '\n'.join(confStrLines)
    
    # Write as new qb.conf
    if auth==True and sys.platform == 'darwin': # for OSX
        import popen2
        p = popen2.Popen4("/usr/libexec/authopen -w -c %s"%QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE)
        p.tochild.write(confStr)
        p.tochild.close()
        result = p.wait()
        if result != 0:
            return False
    else: # standard write file
        try:
            f = open(QB_SUPERVISOR_CONFIG_DEFAULT_WORKER_CONFIGFILE, 'w')
            f.write(confStr)
            f.close()
        except IOError:
            return False
    
    # Return success
    return True


def encryptpassword(password):
    """Encrypts a password string
   
    :Since: Qube 5.5

    :Parameters:
        password : str
            password to encrypt
            
    :Returns: 
        encryped string (str)
    """
    return _qb.encryptpassword(password)


def isadmin(user):
    '''Query the supervisor to find out if the given user is a qube admin.

    Return TRUE if the user is a qube administrator, FALSE otherwise.  In case
    of errors, FALSE is returned also.

    :Since: Qube 6.5
    
    :Parameters:
        user : str
            name of the user to be checked

    :Returns: True if user is a Qube admin, False otherwise
    '''
    return _qb.isadmin(user)

def getusers(convert=True):
    '''Get the user and user group permissions from the Supervisor.
    
    :Since: Qube 5.5

    :Parameters:
        convert : bool
            convert numeric permission to human readable string list
            'all' used to denote "all non-admin permissions"
    
    :Returns: list of users and permissions {'<username>':{<group>:<permission>,},}
        The "" group indicates the standard user permission
    '''
    # INIT: Map to convert permissions number to readable string array
    choices=[ # Submit permissions 
              "submit_job",
              "submit_callback",
              "submit_global_callback",
              # basic permissions
              "bump",
              "kill",
              "remove",
              "modify",
              "preempt",
              "block",
              "interrupt",
              "complete",
              "unblock",
              "suspend",
              "resume",
              "retry",
              "requeue",
              "migrate",
              "shove",
              "fail",
              "retire",
              "reset",
              # admin permissions
              "lock_host",
              "sudo_admin",
              "impersonate",
              "admin"
            ]
    flagValueOverrides = {
                  'lock_host'  : 0x8000000,
                  'sudo_admin' : 0x10000000,
                  'impersonate': 0x20000000,
                  'admin'      : 0x40000000,
                  }
    flagValues = {}
    for i in range(len(choices)):
        flagValues[ choices[i] ] = 1 << i
    flagValues.update(flagValueOverrides)

    # Retrieve user entries    
    userEntries = _qb.getusers()

    # Convert int permission to a string value
    if convert==True:
        # Loop over user permissions
        for k in list(userEntries.keys()):
            # Loop over user and group permissions for that user
            for gk in list(userEntries[k].keys()):
                intVal = userEntries[k][gk]
                if intVal == -1: intVal = 0xFFFFFFFF   # WORKAROUND: -1 means all admin and regular permissions on some Supervisors
                userPermissions = []
                # Handle special case for "all" (non-admin permissions)
                if intVal & 0x1FFFFF == 0x1FFFFF: # matches "all" (non-admin permissions)                
                    userPermissions.append('all')
                    intVal &= ~0x1FFFFF
                # Handle standard choices
                for c in choices:
                    v = flagValues[c]
                    if (intVal & v):  
                        userPermissions.append(c)
                userEntries[k][gk] = userPermissions

    # return results
    return userEntries
    
    
def setusers(action, user, permissions=[], group=''):
    '''Set the permissions for users and user groups.
    Requires administrator access.
    
    :Since: Qube 5.5

    :Parameters:
        action : bool
            what action is to be performed on the specified users
            accepted values: add, delete, set, drop ('remove' also works for 'delete')
        user : string
            username to set permissions for
        group : string
            group under username to set permissions for
        permissions : int or [string]
            user and admin permissions to set for the user or a group for that user
            both int or a string list is accepted
            
            Basic Permissions: ("all" is a shortcut for all of these)

              - submit_job
              - submit_callback
              - submit_global_callback
              - bump
              - kill
              - remove
              - modify
              - preempt
              - block
              - interrupt
              - complete
              - unblock
              - suspend
              - resume
              - retry
              - requeue
              - migrate
              - shove
              - fail
              - retire
              - reset
              
            Admin permissions:
            
              - lock_host
              - sudo_admin
              - impersonate
              - admin
            
    :Example: qb.setusers('add'   , 'myuser', permissions=['all', 'admin'])
    :Example: qb.setusers('add'   , 'myuser', group='mygroup', permissions=['all', 'admin'])
    :Example: qb.setusers('set'   , 'myuser', permissions=['all', 'admin'])
    :Example: qb.setusers('remove', 'myuser', permissions=['preempt'])
    :Example: qb.setusers('drop'  , 'myuser')
        
    :Returns: True/False based on success
    '''
    
    if action == 'remove': action = 'delete'  # Handle "remove" synonym for "delete"
    if not (action in ['add', 'delete', 'set', 'drop']):
        raise ValueError("Action needs to be either 'add', 'remove'/'delete', 'set', 'drop'")
    
    choices=[ # Submit permissions 
              "submit_job",
              "submit_callback",
              "submit_global_callback",
              # basic permissions
              "bump",
              "kill",
              "remove",
              "modify",
              "preempt",
              "block",
              "interrupt",
              "complete",
              "unblock",
              "suspend",
              "resume",
              "retry",
              "requeue",
              "migrate",
              "shove",
              "fail",
              "retire",
              "reset",
              # admin permissions
              "lock_host",
              "sudo_admin",
              "impersonate",
              "admin",
              # Helpers 
             "all", #All non-admin permissions (not listed for getusers(), only setusers())
            ]
    flagValueOverrides = {
                  'lock_host'  : 0x8000000,
                  'sudo_admin' : 0x10000000,
                  'impersonate': 0x20000000,
                  'admin'      : 0x40000000,
                  'all'        : 0x1FFFFF,  #All non-admin permissions (not listed for getusers(), only setusers())
                  }
    flagValues = {}
    for i in range(len(choices)):
        flagValues[ choices[i] ] = 1 << i
    flagValues.update(flagValueOverrides)
 
    # Convert permissions to int if necessary
    if isinstance(permissions, int):
        perm_int = permissions
    elif isinstance(permissions, list):
        # convert
        perm_int = 0
        for i in permissions:
            if i in choices:
                perm_int |= flagValues[i]
            else:
                raise ValueError("Invalid 'permissions' string in value list.")
    else:
        raise ValueError("'permissions' must be either an int or a list of strings")
        
    # Execute and return
    return _qb.setusers(action, user, group, perm_int)
    
    
def updateresources(resourceDict):
    '''Update used/total counts for a dynamic global license resource
    
    :Since: Qube 5.5

    :Parameters:
        resourceDict : dict {name:(used, total)}
            - name  : of the resource to update
            - used  : number of resources currently in use
            - total : total number of resources that can be used.
            
    :Example: qb.updateresource({'license.maya': (0, 100)})
        
    :Returns: True/False based on success
    '''
    success = True
    # Loop over resources and update them
    #   TODO: [Performance] Update the _qb.updateresource() to work on more than 1 resource at a time
    for k,v in resourceDict.items():
        success |= _qb.updateresource(k, v[0], v[1])
    return success


def getresources():
    '''Get dict of global and license resources with an associated used/total count
    
    :Since: Qube 5.5
            
    :Example: qb.getresources()
        
    :Returns: True/False based on success
    '''
    return _qb.getresources()


def updateworkerresources(worker, resources):
    '''Update used/total counts for worker resources
    
    :Since: Qube 6.3

    :Parameters:
        worker : str
            worker name
        resources : str
            resource string
            
    :Example: qb.updateworkerresources("host1", "host.diskusage=13210/80000")
        
    :Returns: True/False based on success
    '''

    return _qb.updateworkerresources(worker, resources)

def updateworkerproperties(worker, properties):
    '''Update value of worker properties
    
    :Since: Qube 6.3

    :Parameters:
        worker : str
            worker name
        properties : str
            property string
            
    :Example: qb.updateworkerproperties("host1", "host.diskfree=4.5")
        
    :Returns: True/False based on success
    '''

    return _qb.updateworkerproperties(worker, properties)

def deleteworkerresources(worker, resources):
    '''Delete (undefine) named resources from the specified worker
    
    :Since: Qube 6.3

    :Parameters:
        worker : str
            worker name
        resources : list
            list of resource strings
            
    :Example: qb.deleteworkerresources("host1", ["host.diskusage", "host.diskfree"])
        
    :Returns: True/False based on success
    '''

    return _qb.deleteworkerresources(worker, resources)

def deleteworkerproperties(worker, props):
    '''Delete (undefine) named properties from the specified worker
    
    :Since: Qube 6.3

    :Parameters:
        worker : str
            worker name
        props : list
            list of property strings
            
    :Example:
         qb.deleteworkerproperties("host1", ["host.disktotal", "host.tmpavail"])
        
    :Returns: 
        True/False based on success
    '''

    return _qb.deleteworkerproperties(worker, props)


#-----------------------------------------------------------------------------
# routines related to Metered Licensing (new in 6.9)
#-----------------------------------------------------------------------------
def send_ML_authdata(authdata):
    '''send Metered Licensing authorization data to the supervisor
    
    :Since: Qube 6.9

    :Parameters:
        authorization : str
            properly formatted and keyed authorization data
            
    :Example:
        qb.send_ML_authdata(authdata)
        
    :Returns: 
        True when authdata is successfully sent, False otherwise.
    '''

    return _qb.send_ML_authdata(authdata)
    

#-----------------------------------------------------------------------------
# routines related to central preferences (new in 6.8)
#-----------------------------------------------------------------------------
def getpreferences(preference_type, entity_path):
    '''get preferences specified by the entity_path
    
    :Since: Qube 6.8

    :Parameters:
        preference_type : str
            type of the preference ("submission", etc)
        entity_path : str
            path to the preferences
            
    :Example:
        qb.getpreferences("submission", "nuke_cmdline.parameters.nuke_version.fields.major_version")
        
    :Returns: 
        list of dicts, each dict representing a DB row
    '''

    return _qb.getpreferences(preference_type, entity_path)


def setpreference(preference_type, entity_path, entity_value, tier, preset, user, mandate):
    '''set a single preference
    
    :Since: Qube 6.8

    :Parameters:
        preference_type : str
            type of the preference ("submission", etc)
        entity_path : str
            path to the preferences
        entity_value : str
            value of the preferences
        tier : str
            "common" or "specific"
        preset : str
            preset 
        user : str
            user name
        mandate : bool
            if the preference is mandate or not
            
    :Example:
        qb.setpreference("submission", "nuke_cmdline.parameters.nuke_version.fields.major_version", "3.0", "specific", "showA", "", False)

    :Returns: 
        True when preference data is successfully set, False otherwise.
    '''
    # We only support submission preferences at this time:
    if preference_type != "submission":
        raise ValueError("Only 'submission' preferences types are allowed at this time. '%s' is unrecognized" % preference_type)

    # make sure we get a valid tier:
    if preference_type == "submission" and tier not in ("common", "specific"):
        raise ValueError("submission tier must be either 'common' or 'specific'. '%s' given" % tier)

    # make sure we get a valid value:
    if preference_type == "submission" and entity_value is None:
        raise ValueError("entity_value cannot be NoneType")

    if preset is None: preset = ''
    if user is None: user = ''

    entity_value = str(entity_value)
    if entity_value == "True":
        entity_value = '1'
    elif entity_value == "False":
        entity_value = '0'
    
    return _qb.setpreference(preference_type, entity_path, entity_value, tier, preset, user, mandate)

def deletepreference(preference_type, entity_path, tier, preset, user):
    '''delete a single preference
    
    :Since: Qube 6.8

    :Parameters:
        preference_type : str
            type of the preference ("submission", etc)
        entity_path : str
            path to the preferences
            
    :Example:
        qb.deletepreference("submission", "nuke_cmdline.parameters.nuke_version.fields.major_version", "specific", "showA", "")

    :Returns: 
        True when preference data is successfully deleted, False otherwise.
    '''
    # We only support submission preferences at this time:
    if preference_type != "submission":
        raise ValueError("Only 'submission' preferences types are allowed at this time. '%s' is unrecognized" % preference_type)

    # make sure we get a valid tier:
    if preference_type == "submission" and tier not in ("common", "specific"):
        raise ValueError("submission tier must be either 'common' or 'specific'. '%s' given" % tier)

    if preset is None: preset = ''
    if user is None: user = ''

    return _qb.deletepreference(preference_type, entity_path, tier, preset, user)


    

# ========================================================
#
# LEGACY EMBEDDED PYTHON FUNCTIONS (USED IN CALLBACKS before Qube 6.1)
#     Embedded python functions used in the callbacks
#
# MISSING from main qb module
#    {"workid", _py_workid, METH_VARARGS, "workid of callback."},
#    {"jobstatus", _py_jobstatus, METH_VARARGS, "status of job."},
#    {"subjobstatus", _py_subjobstatus, METH_VARARGS, "status of subjob."},
#    {"workstatus", _py_workstatus, METH_VARARGS, "status of work item."},
#    {"sibling", _py_sibling, METH_VARARGS, "siblings."},
#
# NEVER RELEASED in main qb module 
#    {"reset", _py_reset, METH_VARARGS, "reset."}, (use requeue and retry instead)
#
# ========================================================

def workkill(*args, **kwargs):
    ''':Deprecated: Use 'killwork'
    '''
    warnings.warn("the 'workkill' function is deprecated.  Instead use 'killwork'.", DeprecationWarning, stacklevel=2)
    return killwork(*args, **kwargs)

def workretry(*args, **kwargs):
    ''':Deprecated: Use 'retrywork'
    '''
    warnings.warn("the 'workretry' function is deprecated.  Instead use 'retrywork'.", DeprecationWarning, stacklevel=2)
    return retrywork(*args, **kwargs)

def workrequeue(*args, **kwargs):
    ''':Deprecated: Use 'requeuework'
    '''
    warnings.warn("the 'workrequeue' function is deprecated.  Instead use 'requeuework'.", DeprecationWarning, stacklevel=2)
    return requeuework(*args, **kwargs)

def workcomplete(*args, **kwargs):
    ''':Deprecated: Use 'retirework'
    '''
    warnings.warn("the 'workcomplete' function is deprecated.  Instead use 'retirework'.", DeprecationWarning, stacklevel=2)
    return retirework(*args, **kwargs)

def workblock(*args, **kwargs):
    ''':Deprecated: Use 'blockwork'
    '''
    warnings.warn("the 'workblock' function is deprecated.  Instead use 'blockwork'.", DeprecationWarning, stacklevel=2)
    return blockwork(*args, **kwargs)

def workunblock(*args, **kwargs):
    ''':Deprecated: Use 'unblockwork'
    '''
    warnings.warn("the 'workunblock' function is deprecated.  Instead use 'unblockwork'.", DeprecationWarning, stacklevel=2)
    return unblockwork(*args, **kwargs)

# Aliases (and also from embedded API)
def completework(*args, **kwargs):
    '''Alias for 'retirework' function
    '''
    #warnings.warn("the 'completework' function is deprecated.  Instead use 'retirework'.", DeprecationWarning, stacklevel=2)
    return retirework(*args, **kwargs)


def complete(*args, **kwargs):
    '''Alias for 'retire' function
    '''
    #warnings.warn("the 'complete' function is deprecated.  Instead use 'retire'.", DeprecationWarning, stacklevel=2)
    return retire(*args, **kwargs)


def validatejob(jobid, agenda=False, subjobs=False, verbose=False):
    """Test that a qb.Job object does not have invalid or malformed values
    
    **New in Qube 6.9-1**
    
    :param jobid: Job id - ``int``
    :param agenda: if True, check each agenda item - ``Boolean``
    :param subjobs: if True, check each job instance - ``Boolean``
    :param verbose: if True, print the name of the malformed job field - ``Boolean``
    :return: ``Boolean``
    
    :Example: qb.validatejob(123)
    :Example: qb.validatejob(345, verbose=True)
    :Example: qb.validatejob(345, agenda=True, subjobs=True, verbose=True)
    """
    info = jobinfo(id=jobid, agenda=agenda, subjobs=subjobs)
    if len(info) == 0:
        raise ValueError('Job id %s not found in Qube' % jobid)
    else:
        return JobValidator.validate(info[0], agenda=agenda, subjobs=subjobs, verbose=verbose)


def CONST(name):
    '''return the integer value of the Qube command or admincomman constant with name
    
    :Since: Qube 6.9

    :Parameters:
        name : str
            Name of the constant
            
    :Example:
        qb.CONST("QB_ADMIN_ORDER_ACTION_REVERIFY_WORKERS")
        
    :Returns: 
        True when authdata is successfully sent, False otherwise.
    '''

    return _qb.CONST(name)
    


# =================================
# Internal Functions (not exposed)
#    These are functions in the _qb compiled module
#    that are not exposed in the qb module
# =================================
#_qb.configDictToStr
#_qb.packageStrToDict
