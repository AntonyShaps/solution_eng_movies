# solution_eng_movies
Guidelines on working in repo:

1. Move your archive to the folder with git repo.
2. Unpack it.
3. Both archive and unpacked folder are ignored by .gitignore.
4. Please, do not push directly to main, but create branches.
5. Upon merging to main please use git merge --no-ff <branch_name>
    Detailed process of merging:
    1. git checkout main
    2. git pull origing main
    3. git merge --no-ff <branch_name>
    4. git push origin main
