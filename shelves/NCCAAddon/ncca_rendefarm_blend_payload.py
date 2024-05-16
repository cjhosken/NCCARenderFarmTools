import os
import sys
sys.path.insert(0,"/public/devel/2023/pfx/qube/api/python/")
import qb

def NCCA_RenderFarm_submit_job(project_name, frame_start, frame_end, frame_step, num_cpus, farm_location, user):
    if os.environ.get("QB_SUPERVISOR") is None :
        os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
        os.environ["QB_DOMAIN"]="ncca"

    job = {{}}
    job['name'] = project_name
    job['prototype'] = 'cmdrange'
    package = {{}}
    package['shell']="/bin/bash"
    pre_render=""
    render_command=f"blender -b {farm_location} -f QB_FRAME_NUMBER -E CYCLES"
    package['cmdline']=f"{pre_render} {render_command}"
            
    job['package'] = package
    job['cpus'] = num_cpus
    
    env={{"HOME" :f"/render/{user}",  
                "SESI_LMHOST" : "lepe.bournemouth.ac.uk",
                "PIXAR_LICENSE_FILE" : "9010@talavera.bournemouth.ac.uk",            
                }}
    job['env']=env

    agendaRange = f'{range}'  
    agenda = qb.genframes(agendaRange)

    job['agenda'] = agenda
            
    listOfJobsToSubmit = []
    listOfJobsToSubmit.append(job)
    listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
    id_list=[]
    for job in listOfSubmittedJobs:
        print(job['id'])
        id_list.append(job['id'])

    print(id_list)