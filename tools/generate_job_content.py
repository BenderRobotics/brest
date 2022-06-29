import ruamel.yaml


class JobContent:

    def __init__(self, stage=None, image=None, tags=None,
                 needs=None, before_script=None, script=None,
                 except_=None, artifacts=None):
        # set default values
        self.stage = ''
        self.image = ''
        self.tags = []
        self.needs = []
        self.before_script = []
        self.script = []
        self.except_ = []
        self.artifacts = {}

        if stage is not None:
            self.stage = stage
        if image is not None:
            self.image = image
        if tags is not None:
            self.tags = tags
        if needs is not None:
            self.needs = needs
        if before_script is not None:
            self.before_script = before_script
        if script is not None:
            self.script = script
        if except_ is not None:
            self.except_ = except_
        if artifacts is not None:
            self.artifacts = artifacts

    def generate_job(self, job_name, file_stream):
        """
        Creates the content of the job based on the specified parameters
        and then writes the created job to the *.yaml file.

        :param job_name: name of the job
        :type job_name : str
        :param file_stream: file object return by open() function
        :type file_stream : obj
        """
        job = {}
        job[job_name] = {}

        if self.stage:
            job[job_name]['stage'] = self.stage
        if self.image:
            job[job_name]['image'] = self.image
        if self.tags:
            job[job_name]['tags'] = self.tags
        if self.needs:
            job[job_name]['needs'] = self.needs
        if self.before_script:
            job[job_name]['before_script'] = self.before_script
        if self.script:
            job[job_name]['script'] = self.script
        if self.except_:
            job[job_name]['except'] = self.except_
        if self.artifacts:
            job[job_name]['artifacts'] = self.artifacts

        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(job, file_stream)


if __name__ == '__main__':
    pass
