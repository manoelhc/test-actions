set dotenv-load
set export

# This variable stores the current working directory.
pwd := `pwd`

# Help target
help:
    @echo
    @echo "This Justfile provides the following targets to assist you with your local and ci tasks:"
    @echo
    @echo " install: Install the project dependencies"
    @echo " install-dev: Install the development dependencies"
    @echo " build: Build the project"
    @echo " run: Build and run the application in development mode in your local machine"
    @echo " run-ci: Build and run the application in CI/CD pipeline"
    @echo " run-local: Run the application in development mode in your local machine, using your local source code"
    @echo " test: Run pytest"
    @echo " test-ci: Run pytest in CI/CD pipeline and generate coverage report"
    @echo " check: Check your code before committing (pre-commit hooks)"
    @echo

# This target installs the development dependencies.
install-dev:
    export PATH="$HOME/miniconda3/bin:$PATH" && \
        . ${HOME}/miniconda3/etc/profile.d/conda.sh && \
        conda init && \
        conda deactivate && \
        conda activate test-actions && \
        pip install -r requirements.txt && \
        pip install -r requirements-dev.txt

# This target is used to build the project.
build:
    docker build -t test-actions .

# Use this command to build and run the application in development mode in your local machine
run: build
    docker run -it -p 5000:5000 -e ENVIRONMENT=development -v $pwd/data:/data test-actions

# Use this command to run the application in CI/CD pipeline
run-ci: build
    docker run -d -p 5000:5000 -e ENVIRONMENT=development --restart=on-failure -v $pwd/data:/data test-actions

# Use this command to run the application in development mode in your local machine,
# using your local source code, without the need to rebuild the image. Don't use it if you're
# adding new dependencies to the project.
run-local:
    docker run -it -p 5000:5000 -e ENVIRONMENT=development -e 'DATABASE_URL=sqlite:////data/test_db' -v $pwd/data:/data -v $pwd/src:/app test-actions

# Use this command to run pytest
test:
    rm -rf /$pwd/data/test_db && \
        export DATABASE_URL="sqlite:///$pwd/data/test_db" && \
        export PYTHONPATH=$pwd/src && \
        export ENVIRONMENT=development && \
        export PATH="$HOME/miniconda3/bin:$PATH" && \
        . ${HOME}/miniconda3/etc/profile.d/conda.sh && \
        conda init && \
        conda deactivate && \
        conda activate test-actions && \
        pip install -r requirements-dev.txt && \
        pytest --cov src

# Use this command to run pytest in CI/CD pipeline and generate coverage report
test-ci:
    cd $pwd && \
        rm -rf data || true && \
        mkdir -p data
    export DATABASE_URL="sqlite:///$pwd/data/test_db" && \
        export PYTHONPATH=$pwd/src && \
        export ENVIRONMENT=development && \
        export HOST=0.0.0.0 && \
        pip install -r requirements-dev.txt && \
        pip install -r requirements.txt && \
        pytest --cov=src --cov-report=xml --cov-config=tox.ini --cov-branch src --full-trace

# Use this command to check your code before committing (pre-commit hooks)
check:
    pre-commit run
