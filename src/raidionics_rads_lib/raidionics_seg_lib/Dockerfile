
# creates virtual ubuntu in docker image
FROM ubuntu:18.04

# maintainer of docker file
MAINTAINER David Bouget <david.bouget@sintef.no>

# set language, format and stuff
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# installing python3
RUN apt-get update -y && \
    apt-get install python3-pip -y && \
    #apt-get install software-properties-common python-software-properties && \
    #apt-get update && \
    #apt-get install python3.6 && \
    apt-get -y install sudo && \
    apt-get update && \
    pip3 install bs4 && \
    pip3 install requests && \
    apt-get install python3-lxml -y && \
    pip3 install Pillow && \
    apt-get install libopenjp2-7 -y && \
    apt-get install libtiff5 -y

# install curl
RUN apt-get install curl -y

# install nano
RUN apt-get install nano -y

# install git (OBS: using -y is conveniently to automatically answer yes to all the questions)
RUN apt-get update && apt-get install -y git

# give deepinfer sudo access and give deepinfer access to python directories
RUN useradd -m ubuntu && echo "ubuntu:ubuntu" | chpasswd && adduser ubuntu sudo
ENV PYTHON_DIR /usr/bin/python3
RUN chown ubuntu $PYTHON_DIR -R
USER ubuntu

# Python
#TMPDIR=/media/dbouget/ihda/Python-envs pip3 install --cache-dir=/media/dbouget/ihda/Python-envs --build /media/dbouget/ihda/Python-envs <package-name>
#RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install tensorflow==1.14.0
RUN pip3 install tensorflow-gpu==1.14.0
#RUN pip3 install torch==1.4.0
#RUN pip3 install pytorch-lightning==0.7.3
RUN pip3 install progressbar2
RUN pip3 install nibabel==3.0.1

RUN pip3 install opencv-python
RUN pip3 install scipy
RUN pip3 install scikit-image
RUN pip3 install progressbar2
RUN pip3 install tqdm
RUN pip3 install SimpleITK
RUN pip3 install dipy==1.1.1
RUN pip3 install aenum
RUN pip3 install sklearn
RUN pip3 install h5py==2.10.0
RUN pip3 install pandas

RUN mkdir /home/ubuntu/raidionicsseg
WORKDIR "/home/ubuntu/raidionicsseg"
COPY raidionicsseg/ $WORKDIR
WORKDIR "/home/ubuntu"
COPY Dockerfile $WORKDIR
COPY main.py $WORKDIR

#RUN mkdir /home/ubuntu/data
RUN mkdir /home/ubuntu/resources
USER root
#RUN chown -R ubuntu:ubuntu /home/ubuntu/data
RUN chown -R ubuntu:ubuntu /home/ubuntu/resources
RUN chmod -R 777 /home/ubuntu/resources
USER ubuntu
EXPOSE 8888

# CMD ["/bin/bash"]
ENTRYPOINT ["python3","/home/ubuntu/main.py"]




