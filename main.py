import collections
import git
import shutil

from git import GitCommandError

from settings import GIT_BASE_ORG_URL, REPO_NAMES

SEPARATOR = '---SEPARATOR---'
# files that get a lot of lines deleted without meaningful contribution
BLOCKED_FILENAMES = {'package-lock.json'}
BLOCKED_FILE_EXTENSIONS = [
    '.csv',
    '.json',
    '.cy.js',
    '.lkml',
    '.secret',
    '.public',
    '.svg',
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
    author_lines_added = collections.defaultdict(int)
    author_lines_deleted = collections.defaultdict(int)

    for repo_name in REPO_NAMES:
        print(f'PROCESSING: {repo_name}')

        try:
            # clone git repo
            cloned_repo = base_repo.clone_from(
                f'{GIT_BASE_ORG_URL}/{repo_name}.git',
                f'repos/{repo_name}',
                shallow_since=since_date,
                single_branch=True,
            )
        except GitCommandError as e:
            if 'fatal: Could not read from remote repository' in str(e):
                # exit early if repo does not exist
                print(f'ERROR: Repo {repo_name} was not found.')
                continue
            if 'fatal: the remote end hung up unexpectedly' in str(e):
                # handle a strange git error and rerun without shallow since
                cloned_repo = base_repo.clone_from(
                    f'{GIT_BASE_ORG_URL}/{repo_name}.git',
                    f'repos/{repo_name}',
                    single_branch=True,
                )
            else:
                raise e

        try:
            # pull all commit logs
            commit_logs = cloned_repo.git.log(numstat=True, since=since_date, format=f'{SEPARATOR}%n%aN%n%ad%n%h')
            commit_logs = commit_logs.split(SEPARATOR)
            for commit_log in commit_logs:
                if not commit_log:
                    continue

                author_name, commit_date, commit_hash, *changed_files = commit_log.strip().split('\n')
                for changed_file in changed_files:
                    if not changed_file:
                        continue

                    lines_added, lines_deleted, filename = changed_file.strip().split('\t')

                    # skip binary files
                    if lines_added == '-' or lines_deleted == '-':
                        continue
                    # skip blocked files
                    if filename in BLOCKED_FILENAMES:
                        continue
                    # skip files we don't want to track
                    if any(filename.endswith(extension) for extension in BLOCKED_FILE_EXTENSIONS):
                        continue

                    lines_added = int(lines_added)
                    lines_deleted = int(lines_deleted)

                    # if single file changes are very big, log it
                    if lines_added > 1000 or lines_deleted > 100:
                        print(f'Found {lines_added} lines added and {lines_deleted} lines deleted in repo {repo_name} on file {filename} (commit hash {commit_hash}).')

                    author_lines_added[author_name] += lines_added
                    author_lines_deleted[author_name] += lines_deleted
        finally:
            # delete cloned repo
            shutil.rmtree(f'repos/{repo_name}')

    print('\nLINES ADDED:')
    pretty_print_author_lines(author_lines_added)

    print('\nLINES DELETED:')
    pretty_print_author_lines(author_lines_deleted)


if __name__ == "__main__":
    main('December 13, 2022')
