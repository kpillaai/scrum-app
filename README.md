# FIT2101 Project (spike)
Team Agility
Agile Project Management Software

This git repository contains the project code for our spike. 

## Instructions

1. Setup the Flask python environment (one time):

   Windows:

   ```
   py -3 -m venv .venv
   ```

   macOS/Linux:

   ```
   python3 -m venv .venv
   ```

2. Enter the Flask python environment (must repeat each time you reopen your IDE/terminal):

   Windows:

   ```
   .venv\Scripts\activate
   ```

   macOS/Linux:

   ```
   . .venv/bin/activate
   ```

3. Install flask to python environment (one time):

   ```shell
   pip install Flask Flask-SQLAlchemy
   ```

4. Start the server:

   ```
   flask run
   ```

5. Open site in browser:

   http://localhost:5000/

## Git Policy

* All members are expected to merge pull requests prior to pushing code.
* All members are expected to add meaningful commit messages to their git pushes.
* New code will be pushed to git branches and not directly to the main branch, ensuring the main branch maintains working code for continuous integration.
* All code will be reviewed by two members of the team prior to merging into the main branch
* All code will pass unit and integration testing prior to merging into the main branch