FROM {{ cookiecutter.docker_base_image }}:{{ cookiecutter.python_version }}

ENV PROJECT='{{ cookiecutter.project_name }}'
RUN mkdir /{{ cookiecutter.project_name }}
WORKDIR /{{ cookiecutter.project_name }}

# Install automation tools (poetry, invoke, etc) in the root environment
COPY requirements_build.txt /{{ cookiecutter.project_name }}/requirements_build.txt
RUN pip3 install -r requirements_build.txt
# Create a venv for poetry to install our library into (so that poetry won't uninstall our automation tools)
RUN python -m venv /root/default_env/
# Install our package
COPY {{ cookiecutter.project_name }}/ /{{ cookiecutter.project_name }}/{{ cookiecutter.project_name }}/
COPY *.txt *.cfg *.py /{{ cookiecutter.project_name }}/
# Install package using virtual environment
RUN bash -c "source /root/default_env/bin/activate && invoke install --clear-cache"
# Make Poetry environment our default for most Python commands
ENV PATH="/root/default_env/bin:${PATH}"
CMD $PROJECT