#!/usr/bin/env python
'''
Functions to collect measurements for farm graphs.

FARM UTILIZATION GRAPH
Y Axis: Processors/Processor Slots/Subjobs
Processor/subjob slots (taking into account reservations for host.processors)
    running processes
    pending processes
    blocked processes
Max Farm Processor Slots (Max processor slots available on the farm.  Measures Farm Capacity.)
Max_Conc (Max Requested processor slots for running jobs)


COMMANDLINE EXAMPLES:
$ python charting.py --supervisor localhost --sqlserver localhost --all
FarmProcs_available    2
FarmProcs_runnings     0
FarmProcs_down         0
JobTasks_running       0
JobTasks_pending       5
JobTasks_blocked       0
Jobs_running           0
Jobs_pending           1
Jobs_blocked           0

'''
from __future__ import print_function
from optparse import OptionParser, OptionValueError, OptionGroup
import sys
if sys.version_info < (2,4): from sets import Set as set   # 2.3 compatibility for build-in sets for 2.4

# Add path if qb module in non-standard location
#sys.path.insert(0, '') 

# If in qb module directory, uncomment these
#from __init__ import hostinfo, setsupervisor
#import query
# If not in the qb module directory, switch out the imports with these
from qb import hostinfo, setsupervisor
import qb  # for qb.ping

# "jobinfo" imported below since determining which one to load based on a commandline option
#from qb import jobinfo
#from qb.query import jobinfo

import time
import os.path

# =====================================
# GLOBALS
# =====================================
sqlserver  = ''
supervisor = ''

# =====================================
# UTILS
# =====================================
def getReservationsDict(job):
    '''
    Construct reservations dict from string
    Todo: Consider moving it into the qb module
    Return: dict
    '''
    resStr  = job.get('reservations', '')
    resDict = dict([tuple(i.split('=')) for i in resStr.split(',') if len(i.strip()) > 0])
    for k,v in resDict.items():
        if v.endswith('+'): v = v[:-1]
        resDict[k] = int(v)
    return resDict


# =====================================
# MEASURMENT QUERIES
# =====================================

def getHostResources(host):
    resourcesDict = dict([tuple(r.split('=')) for r in host['resources'].split(',')])
    for k,v in list(resourcesDict.items()):
        resourcesDict[k] = tuple([int(i) for i in v.split('/')])
    return resourcesDict
    

def getWorkerProcessorSlots(states, memory_threshold, reservedProcsPerJob):
    '''
    Sum of processor slots in each state (collects information from Supervisor)
    Return: dict
    '''
    if len(states) == 0: return {}

    # Variable 'dataDict' to return    
    dataDict = {}

    # Get host info
    #   Construct resourcesDict from resources string for easy retrieval
    hosts = hostinfo()
    for host in hosts:
        host['resourcesDict'] =  getHostResources(host)

    # Collect info on running and available procs
    hostProcs = [ host['resourcesDict']['host.processors'] for host in hosts if host['state'] != 'down']
    if hostProcs > 0:
        procs_running, procs_available = list(zip(*hostProcs))
    else:
        procs_running = procs_available = []
    dataDict['running']  = sum(procs_running)
    dataDict['available'] = sum(procs_available)

    # Collect info on down host procs
    if 'down' in states:
        dataDict['down'] = sum([ host['resourcesDict']['host.processors'][1] for host in hosts if host['state'] == 'down'])

    # Collect info on real "free" host procs (sanity checking for free memory, etc)
    if 'free' in states: #free
        for procIncrement in reservedProcsPerJob:
            sum_free = 0
            for host in hosts:
                if host['state'] != 'down':
                    resources = host['resourcesDict']
                    mem = resources.get('host.memory', (0,0))
                    memFree = mem[1]-mem[0]
                    procsUnreserved = resources['host.processors'][1]-resources['host.processors'][0]
                    freeProcs = min( int((memFree)/memory_threshold)/procIncrement, int((procsUnreserved)/procIncrement) )*procIncrement
                    freeProcs = max(0, freeProcs) # cannot have a negative freeProcs
                    sum_free += freeProcs
            dataDict['free_%i'%procIncrement] = sum_free
        if 'free_1' in dataDict:
            dataDict['free'] = dataDict['free_1']

    # Return dict    
    return dataDict


def getSummaryTasks(states, normalized=True):
    '''
    Weighted summary of work, including jobs with and without Tasks (Collects information from MySQL Database)
    # Description of Work Tallies (weighted):
    # total work pending = sum ( num_tasks_for_jobs_with_tasks*reseravations(host.processors) ) +
    #                      sum ( num_cpus_for_jobs_without_tasks*reservations(host.processors) )
    # The work items correspond 1-to-1 with the Worker slots on the farm.
    # If there are 50 work items being processed, then 50 Worker slots on the farm will be processing
    # This data makes a good addition to the Farm Load/Utilization chart

    Return: dict
    '''
    if len(states) == 0: return ({}, {}, {})
    
    # Get job info for active jobs from SQL database
    if options.querymysql == True:
        jobs = jobinfo(sqlserver=sqlserver, basicFields=['todo', 'todotally', 'reservations', 'cpus', 'cpustally', 'status', 'reason'], filters={'status': states})
    else:
        jobs = jobinfo(filters={'status': states})

    # Construct reservationsDict and host.processors from resources string for easy retrieval
    if normalized:
        for job in jobs:
            job['reservationsDict'] =  getReservationsDict(job)
            job['reservation:host.processors']  =  job['reservationsDict'].get('host.processors', 1)
    else:
        for job in jobs:
            job['reservation:host.processors']  =  1

    # Get list of jobs (cmdline) that do not have a task list (special case)
    jobsWithoutTasks = [i for i in jobs if i['todo'] == 0]
    
    # Work Tallies (weighted)
    sum_work = {}
    sum_requested = {}
    sum_slots = {}
    sum_pendingReasons = {}
    tallyStates = ['pending', 'running']  # for sum_requested
    for state in states:
        sum_work[state]  = sum([i['todotally'][state]*i['reservation:host.processors'] for i in jobs])
        sum_work[state] += sum([i['cpustally'][state]*i['reservation:host.processors'] for i in jobsWithoutTasks])
        sum_slots[state] = sum([i['cpustally'][state]*i['reservation:host.processors'] for i in jobs])

    # Get the pending reason for the slots
    for job in jobs:
        if job['cpustally']['pending'] > 0:
            # collect and sort reasons
            reason = job['reason'].split('\n')
            reason.sort()
            reason = '\n'.join( reason )
            sum_pendingReasons.setdefault(reason, 0)
            sum_pendingReasons[reason] += job['cpustally']['pending']*job['reservation:host.processors'] 
            
    # Note: the sum_work['running'] should equal sum_jobslots['running]
    return (sum_work, sum_pendingReasons, sum_slots)


def getRunningSubjobTaskCorrelation():
    '''
    Search through running subjobs.  Check to make sure the task they are working on is running as well.  If not report it.

    Return: dict
    '''
    import time
    # Get job info for active jobs from SQL database
    iterations = 1
    iteration_interval = 0  # in seconds
    mismatchedJobs_iteration = {}
    for x in range(iterations):
        if options.querymysql == True:
            jobs = jobinfo(sqlserver=sqlserver, basicFields=['id', 'todo', 'todotally', 'reservations', 'cpus', 'cpustally', 'status'], filters={'status': ['running']})
        else:
            jobs = jobinfo(filters={'status': ['running']})
        mismatchedJobs = [i for i in jobs if i['todo'] > 0 and i['cpustally']['running'] !=  i['todotally']['running']]  # Only check on the jobs with tasks for the tasks and subjobs out of sync
        print("Iteration %2i. %4i Out of sync jobs. %5i subjobs-tasks" % (x, len(mismatchedJobs), sum([i['cpustally']['running']-i['todotally']['running'] for i in mismatchedJobs]) ))
        #print 'JOBS WITH NUM TASKS RUNNING != NUM SUBJOBS RUNNING', len(mismatchedJobs)
        #print 'id, tasks, subjobs'
        #for i in mismatchedJobs:
        #        print i['id'], i['todotally']['running'], i['cpustally']['running'], "OFFSET", i['cpustally']['running'] - i['todotally']['running']
        time.sleep(iteration_interval)
        for i in mismatchedJobs:
            mismatchedJobs_iteration.setdefault(i['id'], {})[x] = i
    #print mismatchedJobs_iteration
    print('JOBS WITH NUM TASKS RUNNING != NUM SUBJOBS RUNNING', len(mismatchedJobs_iteration))
    print('id, tasks, subjobs')
    for k,v in mismatchedJobs_iteration.items():
        print(k, end=' ')
        for x in range(iterations):
            if x in v:
                i = v[x]
                print("%2i" % (i['cpustally']['running'] - i['todotally']['running']), end=' ')
            else:
                print(' -', end=' ')
        print()

    return mismatchedJobs


def getSummaryJobs(states):
    '''
    Summary of jobs (Collects information from MySQL Database)
    This lists the number of jobs in different states
    It can be useful to get an idea on how many logical things have been submitted to the farm,
    but it does not correlate to the Worker slots on the farm

    Return: dict
    '''
    if len(states) == 0: return {}

    # Get job info for active jobs from SQL database
    if options.querymysql == True:
        jobs = jobinfo(sqlserver=sqlserver, basicFields=['status'], filters={'status': states})
    else:
        jobs = jobinfo(filters={'status': states})
        
    # Job Tallies
    sum_jobs = {}
    for state in states:
        sum_jobs[state] = sum([1 for i in jobs if i['status'] == state])
    return sum_jobs


# TODO: CPUs and CPUs Tally
# cpus and cpustally can give information on the number of requested processor slots in addition to the number in use
#    this would show useful information as to when the farm is undersubscribed in cpu requests even if there are pending tasks
# Note: the number of running processor slots should match up directly with the number of running work items


# TODO: Average elapsed time for work items
# ???

# TODO: Consider farm throughput by measuring sum of completed work items over time


# TODO: max_conc (farmProc)
# Max concurrent processes requested by running jobs.


def calculateAndReport():
    # Calculate and Report
    hostProcs = getWorkerProcessorSlots(options.farmprocs, options.memoryPerProc, options.reservedProcsPerJob)
    hostProcs_keys = list(hostProcs.keys())
    hostProcs_keys.sort()
    for k in hostProcs_keys:
        if options.hyperic:
            print("FarmProcs_%s=%i"%(k, hostProcs[k]))
        else:
            print("FarmProcs_%-10s  "%k, hostProcs[k])
        if options.gmetric != None:
            os.system('%s  --name Qube_%s --value %i --type int8 --units ProcessSlots'%(options.gmetric, "FarmProcs_%s"%k, hostProcs[k]))

    (jobTasks, jobSlotPendingReasons, jobSlots) = getSummaryTasks(states=options.jobtasks, normalized=options.normalizeTasks)
    for k,v in jobTasks.items():
        if options.hyperic:
            print("JobTasks_%s=%i"%(k, v))
        else:
            print("JobTasks_%-10s   "%k, v)
        if options.gmetric != None:
            os.system('%s  --name Qube_%s --value %i --type int8 --units ProcessSlots'%(options.gmetric, "JobTasks_%s"%k, v))
    for k,v in jobSlots.items():
        if options.hyperic:
            print("JobSlots_%s=%i"%(k, v))
        else:
            print("JobSlots_%-10s   "%k, v)
        if options.gmetric != None:
            os.system('%s  --name Qube_%s --value %i --type int8 --units ProcessSlots'%(options.gmetric, "JobSlots_%s"%k, v))


    # Pending Reasons
    #   Strip out or substitute file-unfriendly characters:    ' : \n <space>
    # List of common pending reasons
    #   no hosts with available resource __________
    #   no hosts with adequate resource __________
    #   no hosts with resource __________
    #   no hosts with available processors
    #   no hosts available in jobs host list
    #   no hosts available in jobs host group list
    #   all available hosts have been omitted by this job
    #   all available groups __________ have been omitted by this job
    #   host missing jobtype __________
    #   no available hosts in farm for this job
    #   resource ________ inadequate
    #   resource ________ unavailable
    for k,v in jobSlotPendingReasons.items():
        if options.hyperic:
            pass #print "JobSlots_pendingReason_%s%i"%(k.replace(' ', '_').replace('\n', '_and_').replace("'", '').replace(':', ''), v)
        else:
            print("JobSlots_pendingReason_%-10s   "%k.replace(' ', '_').replace('\n', '_and_').replace("'", '').replace(':', ''), v)
        # TODO: Add gmetric

    jobs = getSummaryJobs(states=options.jobs)
    for k,v in jobs.items():
        if options.hyperic:
            print("Jobs_%s=%i"%(k, v))
        else:
            print("Jobs_%-10s       "%k, v)
        if options.gmetric != None:
            os.system('%s  --name Qube_%s --value %i --type int8 --units Jobs'%(options.gmetric, "Jobs_%s"%k, v))
    
    if options.outofsync == True:       
        getRunningSubjobTaskCorrelation()
        
    if options.csv != '':
        import datetime
        headerFields = ['"Time"']
        timeNow = datetime.datetime.now()
        dataFields  = ['"%s"'%datetime.datetime.now()]
        for k in hostProcs_keys:
            headerFields.append("\"FarmProcs_%s\""%k)
            dataFields.append('%10i'%hostProcs[k])
        for k,v in jobTasks.items():
            headerFields.append("\"JobTasks_%s\""%k)
            dataFields.append('%10i'%v)
        for k,v in jobSlots.items():
            headerFields.append("\"JobSlots_%s\""%k)
            dataFields.append('%10i'%v)

        csvFileExists = os.path.exists(options.csv)
        f = open(options.csv, 'a')
        if f != None:
            if not csvFileExists:
                f.write(','.join(headerFields)+'\n')
            f.write(','.join([str(i) for i in dataFields])+'\n')
            f.close()



if __name__ == '__main__':
    # ===== DEFAULTS =============
    default_memoryPerProc = 1000
    default_procsReservedPerJob = [1]
    
    # ===== PARSE ARGUMENTS ======
    parser = OptionParser()
    parser.add_option('--supervisor'  , type='string', default='', help='Specify Qube Supervisor to query' )
    parser.add_option('--sqlserver'   , type='string' , help='Specify MySQL Server to query' )
    parser.add_option('--jobtasks'    , type='string' , action='append', default=[], help='Query job tasks for given state.  Normalized to represent processors/processor slots by factoring in host.processor reservation.  Options: running, pending, blocked, ...')
    parser.add_option('--noNormalizeToProc', action='store_false', default=True, dest='normalizeTasks', help='Do not normalize tasks by host.processor job requirement so that value is in processor slots, not number of tasks')

    parser.add_option('--querymysql'  , action='store_true', default=False, help='Dirctly query mysql for info' )

    parser.add_option('--gmetric'   , type='string' , help='Ganglia "gmetric" tool path for writing out data' )
    parser.add_option('--hyperic'   , action='store_true', default=False, help='Print out key=value pairs format used by hyperic' )

    #parser.add_option('--jobslots'    , type='string' , action='append', default=[], help='Query job subjobs/slots for given state.  Normalized to represent processors/processor slots by factoring in host.processor reservation.  Options: running, pending, blocked, ...')
    parser.add_option('--farmprocs'   , type='string' , action='append', default=[], help='Farm load and capacity.   Options: available, running.  "available" is max number of processor slots in the farm that can be assigned. Note: "Running" Should match exactly the running procs from jobs.')
    #parser.add_option('--reqtasks'    , action='store_true', default=False, help='Job Tasks Requested. Max concurrent processes requested by running jobs.  This will show if farm is undersubscribed.')
    parser.add_option('--outofsync', action='store_true', default=False, help='Report on the specific jobs that have out-of-sync tasks and subjobs')
    parser.add_option('--jobs'        , type='string' , action='append', default=[], help='Query number of jobs in different states. Options: running, pending, blocked, ...')
    parser.add_option('--all'         , action='store_true', default=False, help='Query all active jobs for all data options.')
    # real slots available
    parser.add_option('--reservedMemoryPerProc'   , type='int' , dest='memoryPerProc', help='Memory threshold (Mb) per host process slot to determine "real" farm availability (default=%i)'%default_memoryPerProc, default=default_memoryPerProc )
    parser.add_option('--reservedProcsPerJob'     , type='int' , action='append', help='Number of host.processors reserve for each subjob', default=default_procsReservedPerJob)
    # output
    parser.add_option('--csv'        , type='string' , default='', help='Append output to a csv file')    
    parser.add_option('--iterations' , type='int' , help='Iterations to perform before exiting', default=1)
    parser.add_option('--interval' , type='int' , help='Time interval between iterations (sec)', default=1)
    ( options, args ) = parser.parse_args()    

    # Check Options


    # Determine if using the direct supervisor query or mysql query for jobinfo
    if options.querymysql == True:
        from qb.query import jobinfo
        if options.supervisor == '':
            options.supervisor = qb.ping(asDict=True)['address'] # NOTE: asDict is a new option in qb 5.5 api
        if options.sqlserver == None:
            options.sqlserver = options.supervisor
    else:
        from qb import jobinfo
        
    # Modify options
    #   Remove dups and sort the procsReservedPerJob parameter
    options.reservedProcsPerJob = list( set(options.reservedProcsPerJob) )
    options.reservedProcsPerJob.sort()
        
    # Set Globals (file scoped)        
    sqlserver  = options.sqlserver
    supervisor = options.supervisor
    if supervisor != '': setsupervisor(supervisor)
    
    if options.all == True:
        activeStates = ['running', 'pending', 'blocked']
        options.jobtasks = activeStates
        options.farmprocs = ['running', 'available', 'down', 'free']
        options.jobs     = activeStates
        #options.jobslots = ['running', 'pending']
    
    # ==========================
    for i in range(options.iterations):
        calculateAndReport()
        if i < options.iterations:
            time.sleep(options.interval)
    
