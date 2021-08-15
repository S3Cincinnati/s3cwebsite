import git
import os

def git_clone():
    if os.getenv('DJANGO_ENV','') != 'local' or True:
        
        # os.system('mkdir git_publishing/deploy')
        os.system('git clone https://github.com/S3Cincinnati/s3cwebsite.git custAdmin/git_publishing/deploy')
        os.system("git config --global user.name \"S3Cincy\"")
        os.system("git config --global user.email \"s3cincinnati.dev@gmail.com\"")

def git_publish_all():

    if os.getenv('DJANGO_ENV','') != 'local' or True:
        
        repo = git.Repo(os.getcwd() + '/custAdmin/git_publishing/deploy', search_parent_directories=True)

        # files = repo.git.diff(None, name_only=True)
        # for f in files.split('\n'):
        
        #     # repo.git.add(f)
        #     print(f)

        
        # os.system("git add .")
        # os.system("git commit -m \"Deploy new static files\"")
        # repo.remote
        # os.system("git remote add origin https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git")
        # os.system("git push origin main")

        repo.git.add('.')
        repo.git.commit('-m', 'Deploy new static files')
        # repo.remote.add('origin','https://github.com/S3Cincinnati/s3cwebsite')
        
        # repo.remotes.origin.url = "https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git"
        # repo.remote.url = 'https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git'
        
        try:
            remote = repo.create_remote('code_push', url='https://' + os.getenv('SC3-dev-token','') + ':x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git')
        except:
            print('Already exisits')
            print(repo.remotes.code_push.url)
        repo.git.push('code_push','main')



        # repo.git.push('heroku','main')
        # origin = repo.create_remote('origin1', 'https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git')
        # repo.git.push("--set-upstream", origin, repo.head.ref)
        # repo.git.push('origin1','main')
