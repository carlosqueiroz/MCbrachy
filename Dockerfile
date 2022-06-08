FROM saoue66/topas:0.1

ARG GIT_USER
ARG GIT_PASS

ENV EGS_HOME="/EGSnrc_CLRP/egs_home/"
ENV EGS_CONFIG="/EGSnrc_CLRP/HEN_HOUSE/specs/linux.conf"
ENV EGS_BATCH_SYSTEM="at"
ENV HEN_HOUSE="/EGSnrc_CLRP/HEN_HOUSE/"

WORKDIR /workflow

COPY . /workflow

SHELL ["/bin/bash", "-c"]

RUN chmod ugo+x -R /workflow

RUN apt-get update -y

RUN apt install -y git &&\
    git config --global url."https://${GIT_USER}:${GIT_PASS}@gitlab.chudequebec.ca".insteadOf "https://gitlab.chudequebec.ca"&&\
    apt install -y python3.8-venv &&\
    python3 -m venv venv &&\
    source ./venv/bin/activate &&\
    pip install --upgrade pip &&\
    pip install -U -r ./requirements.txt

RUN chmod +x ./entrypoint.sh &&\
    sed -i -e 's/\r$//' ./entrypoint.sh

ENV topas="/topas/topas/bin/topas"

ENTRYPOINT ["./entrypoint.sh"]

