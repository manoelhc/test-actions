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
    @echo " build-packages: Build Manocorp utils package"
    @echo

# This target installs the project dependencies.
install-deps:
    export PATH="$HOME/miniconda3/bin:$PATH" && \
    . ${HOME}/miniconda3/etc/profile.d/conda.sh && \
    conda init && \
    conda deactivate && \
    conda activate test-actions && \
    pip install packages/manocorp && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# This target installs the development dependencies.
install-dev:
    # Install miniconda
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    conda env create -f conda/env.yaml

# This target is used to build the project.
build:
    docker build -t test-actions .

# Use this command to build and run the application in development mode in your local machine
run: build
    docker run -it -p 5000:5000 -e ENVIRONMENT=development -v $pwd/data:/data test-actions

# Use this command to run the application in CI/CD pipeline
run-ci: build
    docker run -d -p 5000:5000 \
        -e ENVIRONMENT=development \
        -e HOST=0.0.0.0 \
        --restart=on-failure \
        -v $pwd/data:/data test-actions

# Use this command to run the application in development mode in your local machine,
# using your local source code, without the need to rebuild the image. Don't use it if you're
# adding new dependencies to the project.
run-local:
    docker run -it -p 5000:5000 -e ENVIRONMENT=development -e 'DATABASE_URL=sqlite:////data/test_db' -v $pwd/data:/data -v $pwd/src:/app test-actions

# Use this command to run pytest
test: install-deps
    rm -rf /$pwd/data/test_db && \
        export DATABASE_URL="sqlite:///$pwd/data/test_db" && \
        export PYTHONPATH=$pwd/src && \
        export ENVIRONMENT=development && \
        export PATH="$HOME/miniconda3/bin:$PATH" && \
        . ${HOME}/miniconda3/etc/profile.d/conda.sh && \
        conda init && \
        conda deactivate && \
        conda activate test-actions && \
        pytest --cov src

# Use this command to run pytest in CI/CD pipeline and generate coverage report
test-ci:
    pip install --force-reinstall packages/manocorp && \
        pip install -r requirements.txt && \
        pip install -r requirements-dev.txt && \
        cd $pwd && \
        rm -rf data || true && \
        mkdir -p data && \
        export DATABASE_URL="sqlite:///$pwd/data/test_db" && \
        export PYTHONPATH=$pwd/src && \
        export ENVIRONMENT=development && \
        export HOST=0.0.0.0 && \
        pytest --cov=src --cov-report=xml --cov-config=tox.ini --cov-branch src --full-trace

# Use this command to check your code before committing (pre-commit hooks)
check:
    pre-commit run

# Build packages
build-packages:
    cd packages/manocorp && \
        python setup.py build && \
        pip install .
