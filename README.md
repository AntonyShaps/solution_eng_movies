# solution_eng_movies

## Guidelines on Working in the Repo

1. Move your archive (`movies-database.zip`) into the folder with the Git repository.
2. Unpack the archive there.
3. Both the archive and the unpacked folder are already listed in `.gitignore`.
4. Please **do not push directly to `main`**, but create a new branch for your work.
5. Upon merging your branch into `main`, please use a **no-fast-forward merge**:
   
   ### Detailed Process for Merging:
   ```bash
   git checkout main
   git pull origin main
   git merge --no-ff <branch_name>
   git push origin main
   ````
  
    ### project structure
    ```bash
    solution_eng_movies/
    ├── README.md
    ├── .gitignore
    ├── yourSolution.ipynb
    ├── movies-database/
    │   ├── movies.csv
    │   ├── ratings.csv
    │   └── ... (other database files)
    ├── movies-database.zip
    ```



