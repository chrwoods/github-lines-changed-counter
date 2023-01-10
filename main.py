import git
import os
import shutil

from settings import GIT_BASE_ORG_URL


def main():
    # g = git.cmd.Git('repos')
    # g.clone('/avm.git', shallow_since="last-month", single_branch=True)
    # print(g)
    # repo = git.Repo('repos/avm')
    # print(repo)

    repo_names = ['avm', 'avm-webapp']
    os.mkdir('repos')

    for repo_name in repo_names:
        base_repo = git.Repo('')
        cloned_repo = base_repo.clone_from(f'{GIT_BASE_ORG_URL}/{repo_name}.git', f'repos/{repo_name}')
        print(cloned_repo)
        shutil.rmtree(f'repos/{repo_name}')

    # os.rmdir('repos')


if __name__ == "__main__":
    main()
