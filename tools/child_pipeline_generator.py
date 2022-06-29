import os

from generate_job_content import JobContent


def child_pipeline_generator():
    """
    Generates * .yml file in which a separate job will be created for each unit test.
    """
    # job content
    stage = 'test'
    image = 'python:3.7'
    tags = ['docker']
    needs = [{'pipeline': '$PARENT_PIPELINE_ID', 'job': 'build-wheel'}]
    before_script = ['pip install Cython', 'pip install dist/brest-*.whl']
    except_ = ['branches']
    artifacts = {'when': 'always', 'paths': ['log'], 'expire_in': '2 weeks'}

    with open('child-pipeline.yml', 'w+') as f:
        for file in os.listdir(f"tests/"):
            if file.startswith('test') and file.endswith(".py"):
                script = [f'python tests/{file}']

                if 'test_version' in file:
                    content = JobContent(stage=stage, image=image, tags=tags, needs=needs, before_script=before_script,
                                         script=script, except_=except_, artifacts=artifacts)
                else:
                    content = JobContent(stage=stage, image=image, tags=tags, needs=needs, before_script=before_script,
                                         script=script, artifacts=artifacts)

                # generated content of child pipeline to *.yml file
                job_name = os.path.splitext(file)[0]
                content.generate_job(job_name, f)


if __name__ == "__main__":
    child_pipeline_generator()
