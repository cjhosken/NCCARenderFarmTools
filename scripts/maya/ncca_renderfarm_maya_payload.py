import os
import sys
import argparse
sys.path.insert(0,"/public/devel/2022/pfx/qube/api/python")
import qb

def main():
    parser = argparse.ArgumentParser(description="Submit a job to the render farm.")
    parser.add_argument("project_name", type=str, help="Name of the project")
    parser.add_argument("qb_command", type=str, help="Command to run")
    parser.add_argument("cpus", type=str, help="Number of CPUs to use")
    parser.add_argument("user", type=str, help="Username")
    parser.add_argument("frame_range", type=str, help="Frame range")
    
    args = parser.parse_args()
    
    if os.environ.get("QB_SUPERVISOR") is None:
        os.environ["QB_SUPERVISOR"] = "tete.bournemouth.ac.uk"
        os.environ["QB_DOMAIN"] = "ncca"

    job = {}
    job['name'] = args.project_name
    job['prototype'] = 'cmdrange'
    
    package = {}
    package['shell'] = "/bin/bash"
    
    pre_render = "export PATH=/opt/autodesk/maya2023/bin:$PATH;"
    pre_render += "export MAYA_RENDER_DESC_PATH=/opt/autodesk/arnold/maya2023:$MAYA_RENDER_DESC_PATH;"
    pre_render += "export MAYA_PLUG_IN_PATH=/opt/autodesk/arnold/maya2023/plug-ins:$MAYA_PLUG_IN_PATH;"
    pre_render += "export MAYA_MODULE_PATH=/opt/autodesk/arnold/maya2023:$MAYA_MODULE_PATH;"

    # Add spaces around semicolons
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'ncca_renderfarm_maya_enable_plugins.py'), 'r') as file:
        enable_plugins_script_content = file.read()

    # Add the script content to the pre_render variable
    pre_render += f"mayapy -c '''{enable_plugins_script_content}''';"
        
    render_command = args.qb_command
    package['cmdline'] = f"{pre_render} {render_command}"
    
    job['package'] = package
    job['cpus'] = args.cpus
    
    env = {
        "HOME": f"/render/{args.user}",
        "SESI_LMHOST": "lepe.bournemouth.ac.uk",
        "PIXAR_LICENSE_FILE": "9010@talavera.bournemouth.ac.uk",
    }
    job['env'] = env
    
    agendaRange = args.frame_range
    agenda = qb.genframes(agendaRange)
    job['agenda'] = agenda
    
    listOfJobsToSubmit = [job]
    listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
    id_list = []
    for job in listOfSubmittedJobs:
        print(job['id'])
        id_list.append(job['id'])

    print(id_list)

if __name__ == "__main__":
    main()
