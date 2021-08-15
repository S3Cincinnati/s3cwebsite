import git
import os

def git_publish_all():

    if os.getenv('DJANGO_ENV','') != 'local':
        
        os.system('git init')
        os.system("git config --global user.name \"S3Cincy\"")
        os.system("git config --global user.email \"s3cincinnati.dev@gmail.com\"")

        # repo = git.Repo(os.getcwd(), search_parent_directories=True)
        # files = repo.git.diff(None, name_only=True)
        # for f in files.split('\n'):
        
        #     repo.git.add(f)
        # print()

        os.system("git add .")
        os.system("git commit -m \"Deploy new static files\"")
        os.system("git remote set-url origin https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git")
        os.system("git push origin main")

        # repo.git.add('.')
        # repo.git.commit('-m', 'Deploy new static files')
        # repo.remote.add('origin','https://github.com/S3Cincinnati/s3cwebsite')
        # repo.git.push('heroku','main')
        # origin = repo.create_remote('origin1', 'https://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:x-oauth-basic@github.com/S3Cincinnati/s3cwebsite.git')
        # repo.git.push("--set-upstream", origin, repo.head.ref)
        # repo.git.push('origin1','main')
