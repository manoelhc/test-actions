set dotenv-load
set export

pwd := `pwd`

install-dev:
    export PATH="$HOME/miniconda3/bin:$PATH" && \
        . ${HOME}/miniconda3/etc/profile.d/conda.sh && \
        conda init && \
        conda deactivate && \
        conda activate test-actions && \
        pip install -r requirements.txt && \
        pip install -r requirements-dev.txt && \

build:
    docker build -t test-actions .
run:
    docker build -t test-actions . && \
        docker run -it -p 5000:5000 -e ENVIRONMENT=development -v $pwd/data:/data test-actions
run-ci:
    docker build -t test-actions . && \
        docker run -d -p 5000:5000 -e ENVIRONMENT=development -v $pwd/data:/data --restart=on-failure test-actions
run-local:
    docker run -it -p 5000:5000 -e ENVIRONMENT=development -e 'DATABASE_URL=sqlite:////data/test_db' -v $pwd/data:/data -v $pwd/src:/app test-actions
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
check:
    pre-commit run

test-ci:
    cd $pwd && \
        rm -rf data || true && \
        mkdir -p data
    export DATABASE_URL="sqlite:///$pwd/data/test_db" && \
        export PYTHONPATH=$pwd/src && \
        export ENVIRONMENT=development && \
        pip install -r requirements-dev.txt && \
        pytest --cov=src --cov-report=xml --cov-config=tox.ini --cov-branch src
