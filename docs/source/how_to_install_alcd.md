# ALCD Installation and Usage Guide

**Note**: ALCD is currently not distributed as a Python package. To use ALCD, you first need to clone the ALCD repository and then create either a Docker or Singularity image.

### Step 1: Clone the ALCD Repository
To begin, clone the ALCD repository to your local machine:
```bash
git clone https://github.com/CNES/ALCD.git
cd ALCD
```

### Step 2: Create the Docker Image

Navigate to the /docker directory in the cloned project:

```bash
cd /path/to/ALCD/docker
```
Build the Docker image with the following command:

```bash
docker build -t alcd .
```
Run the Docker image:

```bash
docker run --rm -it -v /path/to/local/ALCD:/ALCD -v /path/to/local/DATA:/DATA alcd:latest /bin/bash
```
Explanation of the command options:

    --rm: Automatically removes the container when it exits, keeping your environment clean.
    -it: Opens an interactive terminal within the container.
    -v /path/to/local/ALCD:/ALCD: Mounts your local /path/to/local/ALCD directory to /ALCD within the Docker container, allowing data access and output within this directory.
    -v /path/to/local/DATA:/DATA Mounts your local / /path/to/local/DATA directory to /DATA within the Docker container, allowing data access and output within this directory.
    alcd:latest: Refers to the Docker image tagged as alcd, built in step 2.

### Step 3: Create the Singularity Image

Navigate to the /singularity directory within the ALCD project:

```bash
cd /path/to/ALCD/singularity
```
Build the Singularity image using the following command:

```bash
singularity -v build --fakeroot alcd.sif alcd.def
```
    Explanation:
    --fakeroot: Allows image building without root access (required for some systems).
    alcd.sif: The name of the output Singularity image file.
    alcd.def: The Singularity definition file containing instructions for building the image.

Run the Singularity image:

```bash
singularity shell --cleanenv --bind /path/to/local/ALCD:/ALCD alcd.sif /bin/bash
```
    Explanation of the command options:
    --cleanenv: Starts the container with a clean environment, ensuring no unexpected environment variables affect the container.
    --bind /path/to/local/ALCD:/ALCD: Mounts the local directory /path/to/local/ALCD into /ALCD within the Singularity container, allowing seamless data access.
    alcd.sif: Specifies the Singularity image file built in step 3.

Following these steps will set up ALCD for use with either Docker or Singularity, enabling access to the project’s data and output through the mounted /ALCD directory.