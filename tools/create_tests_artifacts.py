import zipfile
import gitlab
import os

# params needed for access to Gitlab API
URL = f"{os.getenv('CI_SERVER_PROTOCOL')}://{os.getenv('CI_SERVER_HOST')}/"
API_TOKEN = os.getenv("BREST_UNIT_TEST_GATHER_TOKEN")
PROJECT_NAME = "Brest"

gl = gitlab.Gitlab(URL, private_token=API_TOKEN)
project = gl.projects.list(search=PROJECT_NAME)[0]

last_pipeline = project.pipelines.list(all=False)[0]
bridge = last_pipeline.bridges.list()[0]
child_id = bridge.downstream_pipeline['id']

child_pipeline = project.pipelines.get(id=child_id)
jobs_ = child_pipeline.jobs.list()

for idx, job_ in enumerate(jobs_):
    file_name = '__artifacts.zip'

    # only job which contains `artifacts.zip`
    for artifact in job_.artifacts:
        if artifact['filename'] in file_name:
            break
    else:
        continue

    job_name = os.path.splitext(job_.name)[0].split('/')[-1]
    job = project.jobs.get(job_.id, lazy=True)

    with open(file_name, "wb") as f:
        job.artifacts(streamed=True, action=f.write)
    zipped = zipfile.ZipFile(file_name)

    for zip_info in zipped.infolist():
        if not zip_info.filename.endswith('.log'):
            continue
        zip_info.filename = f"{job_name}_{os.path.basename(zip_info.filename)}"
        zipped.extract(zip_info, path=os.path.join(os.path.dirname(__file__), '..', 'log'))

    zipped.close()
