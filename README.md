<div align="center">
<img alt="pdoc" src="./docs/_static/logo.svg" width="320" />
</div>
</br>

# Bender Robotics Embedded Systems Toolkit
Goal of the Brest project is to provide a python based resource manager and common libraries for embedded system testing.

Brest is currently in **Beta** stage!
If you are looking for the **documentation**, please refer [here](https://docs.benderrobotics.com/brest/).

## Building Brest from the source
If you want to build Brest from the source, you need to clone the repository first.

    $ git clone https://github.com/BenderRobotics/brest.git
    
Then checkout to `devel` branch to get the latest version, or to `feature/*` branches for the cutting edge versions.

    $ git checkout devel

For building the python wheel, we use GNU **make**. If you don't have **make** installed yet, please refer to [Installing make](#installing-make)

**make** expects that your pip3 installation will be available under `pip` command. Also there is a possibility that `setup.py` may fail
on `bdist_wheel` as an not known argument. To fix this, install `wheel` package again.

Navigate to top-level directory of the cloned repository and you will be able to use the following commands:

    $ make install    # First time Brest installation. It will build the source and install it using pip
    $ make reinstall  # Pulled new commit? Use this to build new wheel, uninstall and install the new version using pip
    $ make all        # Just builds the wheel
    $ make clean      # Cleans the build directories and files

The built wheel is located in `./brest/dist/`.

## Building the offline documentation
To build the docs for offline usage, you need to install the dependencies first. Assuming that you have already Brest installed, you
can use:

    $ pip install brest[docs]

to install dependencies for building the docs. Next step is to navigate to the `./docs/` folder and execute the following command:

    $ make html

If the build was successful, the docs will be accessible in `./docs/_build/html/` directory under `index.html`.
If you don't have **make** installed yet, please refer to [Installing make](#installing-make)

There is an option to build versioned documentation. In order to be able to do that a versioning support has to be added. Navigate to `./cm/sphinx-versions/` and install the package inside:

    $ pip install --no-cache-dir sphinx-versions-1.1.3.post4.tar.gz

After that the versioned documentation can be built by going to `./docs/` and using:

    $ make html-versioned

If the command fails with sth like `fatal: could not read Username for 'https://github.com'` one might have to adjust settings in repository `.git-config`:

    [credential]
        helper = manager

This was observed and fixed on Windows10 machine.

## Installing make
On Ubuntu like machines execute the following command:

    $ sudo apt install make

If you are on windows machine, you can install a [MinGW](http://www.mingw.org/). In the MinGW installer choose `mingw32-base-bin` and
`msys-base-bin` packages, then click on *Installation* and *Apply changes*.
Don't forget to add the **make** binary to the system `PATH`. Default install location should be `C:/MinGW/msys/1.0/bin/`.

## Branching strategy
Because Brest is a relatively small project, it uses a very basic branching strategy.
All feature branches keep their history and merge into the 'devel' branch as merge-commits.
If there has been a commit in the 'devel' branch while the feature branch was under development, 
the procedure is to merge 'devel' into the feature branch (as a merge-commit) to update changes and when the feature 
branch development is over, it can be merged with 'devel'.

## Versioning strategy
**Release versioning:**
    0.0.X 

**Post release versioning:**
    0.0.X.postN     - Nth fix of 0.0.X

**Development release versioning:**
    0.0.Y.devABCD+N - Y = X+1, ABCD = redmine ticket #, Nth dev release

## Dev release steps
To create a development release for a branch, one must follow these steps:
1. Go to the main \_\_init\_\_.py of the package, find \_\_version\_\_ and change it according to the [versioning strategy](#versioning-strategy)
2. Go to setup.py and also change the version there
3. Commit these changes with commit message of the version and reference to the Redmine ticket (e.g. Version 1.0.1.dev8653+0 (refs #8653))
4. Create a tag on this commit with the version

Now in pipeline you should see deploy-wheel-dev.
