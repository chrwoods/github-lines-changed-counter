import collections
import git
import shutil

from settings import GIT_BASE_ORG_URL, REPO_NAMES

SEPARATOR = '---SEPARATOR---'
# files that get a lot of lines deleted without meaningful contribution
BLOCKED_FILENAMES = {'package-lock.json'}
BLOCKED_FILE_EXTENSIONS = [
    'csv',
]


def pretty_print_author_lines(author_lines_count: dict) -> None:
    print_order = sorted(
        author_lines_count.keys(),
        key=lambda name: author_lines_count[name],
        reverse=True,
    )
    for author_name in print_order:
        print(f'{author_name}: {author_lines_count[author_name]}')


def main(since_date: str='last month') -> None:
    base_repo = git.Repo('')
    author_lines_deleted = collections.defaultdict(int)

    repo_names = REPO_NAMES[:5]

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
                    lines_added, lines_deleted, filename = changed_file.strip().split('\t')

                    # skip binary files
                    if lines_added == '-' or lines_deleted == '-':
                        continue
                    # skip blocked files
                    if filename in BLOCKED_FILENAMES:
                        continue
                    # skip files we don't want to track
                    if filename.split('.')[-1] in BLOCKED_FILE_EXTENSIONS:
                        continue

                    lines_added = int(lines_added)
                    lines_deleted = int(lines_deleted)

                    # if single file changes are very big, log it
                    if lines_added > 1000 or lines_deleted > 100:
                        print(f'Found {lines_added} lines added and {lines_deleted} lines deleted in repo {repo_name} on file {filename}.')

                    author_lines_deleted[author_name] += lines_deleted

        finally:
            # delete cloned repo
            shutil.rmtree(f'repos/{repo_name}')

    print('\nLINES DELETED:')
    pretty_print_author_lines(author_lines_deleted)


if __name__ == "__main__":
    main()
