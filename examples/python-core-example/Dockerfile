FROM public.ecr.aws/docker/library/python:3.8

ENV PROJECT='python-core-example'
RUN mkdir /python-core-example
WORKDIR /python-core-example

# Install automation tools (poetry, invoke, etc) in the root environment
COPY requirements_build.txt /python-core-example/requirements_build.txt
RUN pip3 install -r requirements_build.txt
# Create a venv for poetry to install our library into (so that poetry won't uninstall our automation tools)
RUN python -m venv /root/default_env/
# Install our package
COPY python-core-example/ /python-core-example/python-core-example/
COPY *.txt *.cfg *.py /python-core-example/
# Install package using virtual environment
RUN bash -c "source /root/default_env/bin/activate && invoke install --clear-cache"
# Make Poetry environment our default for most Python commands
ENV PATH="/root/default_env/bin:${PATH}"
CMD $PROJECT