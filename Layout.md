# Project Layout

A typical Python project should be laid out as follows:

```
project_root/ - usually the same name as the project
    code_folder/ - same name as the project 
        __init__.py 
            stores all of the things that get loaded on import - everything
            you want to expose to end users should be here, but should not
            include CLI
        
        cli/ 
            __init__.py 
                Loads the CLI components
        
            main.py 
                The main CLI entrypoints
        
        common/ 
            Stores code shared across project
            
            __init__.py
                Loats the components
        
            common.py 
                Common utilities
        
            logging.py
                Logging utilities
        
            datatypes.py 
                Shared datatypes
        
        project_specific_folders/
            E.g. "api" or "queue" or whatever
        
        more_project_specific_folders
            Continue breaking down project code into subfolders for organization
        
        tests/
            __init__.py
                Empty
        
            conftest.py
        
            common/
                Tests for common directory
                
                test_common.py
                ...
        
            cli/ 
                Tests for CLI
        
            project_specific_folders/
                Tests for project

    docs/
        Folder for Sphinx generated docs

        conf.py
        index.rst
        main.rst
        modules.rst
        
        modules/

    git_hooks/
        Common git hooks for the project

    setup.py
    setup.cfg
    pytest.ini
    tasks.py
    .coveragerc
    requirements.txt
    requirements_build.txt
    requirements_dev.txt
    README.md
```