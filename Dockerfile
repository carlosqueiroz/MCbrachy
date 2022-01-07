FROM saoue66/topas:0.1

ENV topas="/topas/topas/bin/topas"

WORKDIR /workflow

COPY . /workflow

RUN apt-get update --fix-missing &&\
    apt-get install -y unzip &&\
    mkdir patients &&\
    unzip \*.zip -d patients 

WORKDIR ./dicom_rt_calcification_pipeline

RUN apt install -y git &&\
    apt install -y python3.8-venv &&\
    python3 -m venv venv &&\
    ls -a &&\
    ./venv/bin/pip install -r ./requirements.txt
    
