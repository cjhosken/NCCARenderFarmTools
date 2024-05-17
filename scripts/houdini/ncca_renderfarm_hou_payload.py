import os
import sys
import argparse
sys.path.insert(0,"/public/devel/2022/pfx/qube/api/python/")

import qb


def main():
    parser = argparse.ArgumentParser(description="Submit a job to the render farm.")
    parser.add_argument("project_name", type=str, help="Name of the project")
    parser.add_argument("output_driver", type=str, help="ROP path")
    parser.add_argument("file_path", type=str, help="file_path")
    parser.add_argument("cpus", type=str, help="Number of CPUs to use")
    parser.add_argument("user", type=str, help="Username")
    parser.add_argument("frame_range", type=str, help="Frame range")
    
    args = parser.parse_args()

    if os.environ.get("QB_SUPERVISOR") is None :
        os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
        os.environ["QB_DOMAIN"]="ncca"


    job = {}
    job['name'] = f"{args.project_name}"
    job['prototype'] = 'cmdrange'
    package = {}
    package['shell']="/bin/bash"
    pre_render="cd /opt/software/hfs19.5.605/; source houdini_setup_bash; "
    render_command=f"hython $HB/hrender.py -e -F QB_FRAME_NUMBER -R -d {args.output_driver} {args.file_path}"
    package['cmdline']=f"{pre_render} {render_command}"
            
    job['package'] = package
    job['cpus'] = str(args.cpus)
    
    env={"HOME" :f"/render/{args.user}",  
                "SESI_LMHOST" : "lepe.bournemouth.ac.uk",
                "PIXAR_LICENSE_FILE" : "9010@talavera.bournemouth.ac.uk",            
                }
    job['env']=env

    agendaRange = str(args.frame_range)
    agenda = qb.genframes(agendaRange)

    job['agenda'] = agenda
            
    listOfJobsToSubmit = []
    listOfJobsToSubmit.append(job)
    listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
    id_list=[]
    for job in listOfSubmittedJobs:
        id_list.append(job['id'])
    
    print(id_list)

main()