import git
import os

def git_clone():
    if os.getenv('DJANGO_ENV','') == 'heroku':
        
        os.system('git clone https://github.com/S3Cincinnati/s3cwebsite.git custAdmin/git_publishing/deploy')
        os.system("git config --global user.name \"S3Cincy\"")
        os.system("git config --global user.email \"s3cincinnati.dev@gmail.com\"")

def git_publish_all():

    if os.getenv('DJANGO_ENV','') == 'heroku':
        
        repo = git.Repo(os.getcwd() + '/custAdmin/git_publishing/deploy', search_parent_directories=True)

        repo.git.add('.')
        repo.git.commit('-m', 'Deploy new static files')

        try:
            remote = repo.create_remote('code_push', url='https://' + os.getenv('SC3-dev-token','') + ':x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git')
        except:
            print('Already exisits')
        
        repo.git.push('code_push','main')

