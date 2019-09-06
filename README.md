# Bender Robotics Embedded Systems Toolkit
Goal of the Brest project is to provide a python based resource manager and common libraries for embedded system testing.

Brest is currently in **Alpha** stage!
If you are looking for the **documentation**, please refer [here](http://10.0.254.62:8000/)

## Building Brest from the source
If you want to build Brest from the source, you need to clone the repository first.

    $ git clone https://github.com/BenderRobotics/brest.git
    
Then checkout to `devel` branch to get the latest version, or to `feature/*` branches for the cutting edge versions.

    $ git checkout devel

For building the python wheel, we use GNU **make**. If you don't have **make** installed yet, please refer to [Installing make](#installing-make)

Navigate to top-level directory of the cloned repository and you will be able to use the following commands:

    $ make install    # First time Brest installation. It will build the source and install it using pip
    $ make reinstall  # Pulled new commit? Use this to build new wheel, uninstall and install the new version using pip
    $ make all        # Just builds the wheel
    $ make clean      # Cleans the build directories and files

Builded wheel is located in `brest/dist/`.

## Building the offline documentation
To build the docs for offline usage, you need to install the dependencies first. Assuming that you have already Brest installed, you
can use:

    $ pip install brest[docs]

to install dependencies for building the docs. Next step is to navigate to the `brest/docs` folder and execute the following command:

    $ make html

If the build was successful, the docs will be accessible in `brest/docs/_build/html` directory under `index.html`. 
If you don't have **make** installed yet, please refer to [Installing make](#installing-make)

## Installing make
On Ubuntu like machines execute the following command:

    $ sudo apt install make

If you are on windows machine, you can install a [MinGW](http://www.mingw.org/). In the MinGW installer choose `mingw32-base-bin` and
`msys-base-bin` packages, then click on *Installation* and *Apply changes*.
Don't forget to add the **make** binary to the system `PATH`. Default install location should be `C:\MinGW\msys\1.0\bin\`.