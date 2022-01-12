FROM saoue66/topas:0.1

ENV topas="/topas/topas/bin/topas"
ENV TOPAS_G4_DATA_DIR="/G4Data"

WORKDIR /workflow

COPY . /workflow

RUN chmod ugo+x -R /workflow

RUN apt install -y git &&\
    apt install -y python3.8-venv &&\
    python3 -m venv venv &&\
    ls -a &&\
    ./venv/bin/pip install -r ./requirements.txt

ENTRYPOINT ["./venv/bin/python", "automatic_recalculation_workflow.py", "-o", "Target", "-o", "Bladder", "-o", "Urethra", "-o", "Rectum", "-o", "calcification", "-a", "topas",  "-s", "True",  "-r", "False"]
    
