import git
import os

def git_publish_all():

    if os.getenv('DJANGO_ENV','') != 'local':
        
        os.system('git init')

        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        # files = repo.git.diff(None, name_only=True)
        # for f in files.split('\n'):
        
        #     repo.git.add(f)
        # print()
        repo.git.add('.')
        repo.git.commit('-m', 'Deploy new static files')
        repo.remote.add('origin','https://github.com/S3Cincinnati/s3cwebsite')
        repo.git.push('origin','main')
        repo.git.push('heroku','main')
