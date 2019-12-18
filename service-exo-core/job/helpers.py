from .wrappers import QASessionAdvisorJob, ProjectJob, FastrackJob


def get_data_for_job(core_job):
    instance = core_job.content_object
    classname = instance.__class__.__name__.lower()

    if classname == 'consultantprojectrole':
        project = instance.project

        if project.is_fastracksprint:
            job = FastrackJob(instance, instance.user)
        else:
            job = ProjectJob(instance, instance.user)
    elif classname == 'qasessionadvisor':
        job = QASessionAdvisorJob(instance, instance.user)
    elif classname == 'userprojectrole':
        job = ProjectJob(instance, instance.user)
    else:
        raise ValueError('Invalid job: {}'.format(classname))

    return job.dump_data()
