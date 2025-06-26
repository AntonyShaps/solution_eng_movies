# solution_eng_movies

## Guidelines to rune the DemoApp

1. clone repo
2. Add to '/solution_eng_movies' folder unzipped file "movies-database" from https://drive.google.com/drive/folders/1PtwDEUqqSup22Auam0fT7G2Jvils1N2a
3. Add to '/solution_eng_movies/models/NeuMF_model' 2 files from https://drive.google.com/drive/folders/1LCJIj_h_OPtl042bgSCGuAr35CKNRRCs?usp=drive_link
4. use commadns:
   ```bash
   cd solution_eng_movies
   conda create -n movie_env python=3.10 -y
   conda activate movie_env
   pip install -r requirements.txt
   streamlit run streamlit/Home.py
   ```

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


