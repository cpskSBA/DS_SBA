# Small Business Data HUB

Local dashboards for SBA contracting data

---

## Local Development

1. Create a virtual environment that uses python 3.8
    ### Linux / MacOS
     + Run the following command:        
        ```
        python3.8 -m venv venv
        ```
     + Activate the virtual environment
        ```
        source venv/bin/activate
        ```
    ### Windows
     + Run the following command:        
        ```
        python3.8 -m venv venv
        ```
     + Activate the virtual environment using Command Prompt
        ```
        \path_to_venv\Scripts\activate.bat
        ```
     + Activate the virtual environment using Powershell
        ```
        \path_to_venv\Scripts\Activate.ps1
        ```
 
1. Install the required modules listed in the requirements file
    ```
        pip install -r requirements.txt
    ```
    ### Host Variable Interpolation
    *TOML does not support variable interpolation [by design](https://toml.io/en/). As a result, in order to pass in environment variables we need to use the <u>toml</u> library to substitute/inject the correct values at runtime. If you do not wish to do so, then you need to comment out the line that calls the interpolation function from the [Local_Scorecard](./src/Local_Scorecard.py) file.*

1. The environment variables can either be setup manually or generated during runtime.

    ### Manual Setup 
    To set the environment variables manually, copy the values in the `secrets.example.toml` to a new `secrets.toml` file in the same directory and update the values. 
    ### Generated During Runtime
    During runtime, the environment variables are generated and stored in a secrets file by the generator module in the utils directory. **This method will only work if there is no `secrets.toml` file.** The generator relies on preset environment variables for each key in the `secrets.example.toml` file with the prefix `sbdh_` *(see examples below)*.
    ### Linux / MacOS
    + Create your variables
        ```
            export sbdh_account=secret_account
            export sbdh_warehouse=WAREHOUSE_INFORMATION
        ```
    ### Windows
    + Create your variables
        ```
            setx sbdh_account secret_account
            setx sbdh_warehouse WAREHOUSE_INFORMATION
        ```
        *NOTE: using setx will create a persistent variable that will still be available when you restart. To setup session variables, you can use the ```set``` command instead of ```setx```*

1. Run the application

    To run the application, navigate to the ```src``` directory and run the following command
    ```
        streamlit run Local_Scorecard.py
    ```

---

## Pushing Code Changes to GitHub

To ensure a smooth workflow and maintain version control, please follow the instructions below to push your code changes to GitHub:

### 1. Create a Feature Branch based on JIRA Issue

Before making any code changes, create a new feature branch in your local repository. This branch should be named after the corresponding JIRA key for the task you are working on. This naming convention helps with organization and tracking. The JIRA project associated with this repo is [Small Business Data HUB](https://sbaone.atlassian.net/jira/software/c/projects/SBDH/boards/53).

To create a branch locally using Git, open your terminal and execute the following command from the `main` branch:

```
git checkout -b BRANCH-NAME
```

Replace `BRANCH-NAME` with the JIRA key, e.g., `SBDH-12-New_Dashboard`.

### 2. Push Code Changes to the Branch

Make the necessary code changes in your local working directory, adding, modifying, or deleting files as required. Once you are ready to commit your changes, follow these steps:

- Add the changed files to the commit:

  ```
  git add .
  ```

- Commit the changes with a descriptive message and for good measure, also include the JIRA key:

  ```
  git commit -m "SBDH-12: Brief description of the changes made"
  ```

### 3. Submit a Pull Request for Code Review

After committing your changes to the branch, it's time to submit a pull request to merge your code into the `main` branch. This step enforces a code review and collaboration with other team members.

To create a pull request, follow these steps:

1. Visit the repository on GitHub.
2. Switch to the branch you created earlier.
3. Click on the "Pull Request" button.
4. Provide a clear title and description for the pull request, summarizing the changes made.
5. Review the changes and confirm the pull request submission.

### 4. Review and Approval

You can continue making changes and pushing them to the same branch. The pull request will update automatically. This is also the best way to also address or respond to specific questions about the pull request.

### 5. Merge Changes into the Main Branch

Once your changes have been reviewed and approved, they will be merged into the `main` branch and the feature branch will be deleted.

### 6. Pushing updates to Production

To push any changes from the `main` branch into the protected "`prod`" branch for production, submit a pull request as follows:

1. Visit the repository on GitHub.
2. Switch to the main branch.
3. Click on the "Pull Request" button.
4. Select the "`prod`" branch as the base branch to pull into.
5. Review the changes and confirm the pull request submission.

Once the pull request is reviewed and approved, the changes will be merged into the "`prod`" branch and deployed to production.

---

The Local Scorecard dashboard is the main dashboard. To deploy it, you need:
1. Local_Scorecard.py
2. SBA_DO_ZIP_matching_table.csv
3. A secrets.toml file in the .streamlit folder that follows the structure in https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management.
4. A config.toml file in the .streamlit folder
5. Python 3.8 and the packages in requirements.txt
