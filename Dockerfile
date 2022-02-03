FROM saoue66/egs_brachy:0

ARG GIT_USER
ARG GIT_PASS

ENV EGS_HOME="/EGSnrc_CLRP/egs_home/"
ENV EGS_CONFIG="/EGSnrc_CLRP/HEN_HOUSE/specs/linux.conf"
ENV EGS_BATCH_SYSTEM="at"
ENV HEN_HOUSE="/EGSnrc_CLRP/HEN_HOUSE/"
ENV egs_brachy="/EGSnrc_CLRP/egs_home/bin/linux/egs_brachy"

WORKDIR /workflow

COPY . /workflow

RUN chmod ugo+x -R /workflow

RUN apt install -y git &&\
    git config --global url."https://${GIT_USER}:${GIT_PASS}@gitlab.chudequebec.ca".insteadOf "https://gitlab.chudequebec.ca"&&\
    apt install -y python3.8-venv &&\
    python3 -m venv venv &&\
    ls -a &&\
    ./venv/bin/pip install -U -r ./requirements.txt

ENTRYPOINT ["./venv/bin/python", "automatic_recalculation_workflow.py", "-o", "prostate", "-o", "vessie", "-o", "uretre", "-o", "rectum", "-o", "calcification", "-a", "egs_brachy",  "-s", "True",  "-r", "False"]

