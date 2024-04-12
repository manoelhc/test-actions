# How to report a bug, feature request, or ask a question

If you have a bug to report, a feature request, or a question, please open an issue in this repository. To do so, follow these steps:

1. Go to the repository
2. Click on the "Issues" tab
3. Click on the "New issue" button
4. Fill in the title and description of the issue
5. Click on the "Submit new issue" button
6. Wait for a response from the maintainers

# How to contribute to this project

We welcome contributions to this project. To start contributing, follow these steps:

0. Fork the repository
1. Install conda or miniconda: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
2. Install just: https://github.com/casey/just
2. Create the conda environment: `conda env create -f conda/env.yaml`
3. Activate the conda environment: `conda activate test-actions`
3. Install the development requirements: `pip install -r requirements-dev.txt`
4. Install the pre-commit hooks: `pre-commit install`
5. Create a branch for your changes: `git checkout -b feat/my-branch`. Please use `feat/` for new features, `fix/` for bug fixes, `chore/` for maintenance tasks, and `docs/` for documentation changes.
6. Make your changes.
7. Run the tests: `just test`
8. Once everything looks fine, commit you changes. Please follow the commit message conventions: https://www.conventionalcommits.org/en/v1.0.0/. When you try to commit, the pre-commit hooks will run and check your code. If there are any issues, please fix them and commit again.
9. Push your changes to your fork: `git push origin feat/my-branch`
10. Create a pull request.


I recommend using the `just` command line tool to run the most common commands. You can see the available commands by running `just --list`.
You also can explore the `justfile` to see the available commands and read the comments to understand what each command does. the `justfile` is located at the root of the repository and it's format is very similar to a `Makefile`.

If you want to understand more about what the pre-commit hooks do, you can explore the `.pre-commit-config.yaml` file. This file contains the configuration for the pre-commit hooks. You can see the available hooks and what they do in the pre-commit repository: https://pre-commit.com/hooks.html.

## VSCode useful extensions

- Python
- Gihub Copilot (mainly for documentation)
- Bandit (security)
- Pylance (Python language server)
- Python Debugger
