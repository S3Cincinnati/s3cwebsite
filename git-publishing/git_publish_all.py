import git
import os

def git_publish_all():
    repo = git.Repo(os.getcwd())
    files = repo.git.diff(None, name_only=True)
    for f in files.split('\n'):
        
        repo.git.add(f)

    repo.git.commit('-m', 'Deploy new static files')
    repo.git.push()
    repo.git.push('heroku','main')