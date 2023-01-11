import collections
import git
import shutil

from settings import GIT_BASE_ORG_URL

SEPARATOR = '---SEPARATOR---'
# files that get a lot of lines deleted without meaningful contribution
BLOCKED_FILENAMES = {'package-lock.json'}


def main(since_date='last month'):
    repo_names = ['avm']
    base_repo = git.Repo('')
    author_lines_deleted = collections.defaultdict(int)

    for repo_name in repo_names:
        try:
            # clone git repo
            cloned_repo = base_repo.clone_from(
                f'{GIT_BASE_ORG_URL}/{repo_name}.git',
                f'repos/{repo_name}',
                shallow_since=since_date,
                single_branch=True,
            )

            # pull all commit logs
            commit_logs = cloned_repo.git.log(numstat=True, since=since_date, format=f'{SEPARATOR}%n%aN%n%ad')
            commit_logs = commit_logs.split(SEPARATOR)
            for commit_log in commit_logs:
                if not commit_log:
                    continue
                author_name, commit_date, _, *changed_files = commit_log.strip().split('\n')
                for changed_file in changed_files:
                    lines_added, lines_deleted, filename = changed_file.split('\t')
                    # only increment if the filename is not blocked
                    if filename not in BLOCKED_FILENAMES:
                        author_lines_deleted[author_name] += int(lines_deleted)

        finally:
            # delete cloned repo
            shutil.rmtree(f'repos/{repo_name}')

    print(author_lines_deleted)


if __name__ == "__main__":
    main()
