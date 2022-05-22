FROM saoue66/egs_brachy:0

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

RUN apt install -y git &&\
    git config --global url."https://${GIT_USER}:${GIT_PASS}@gitlab.chudequebec.ca".insteadOf "https://gitlab.chudequebec.ca"&&\
    apt install -y python3.8-venv &&\
    python3 -m venv venv &&\
    ./venv/bin/pip install -U -r ./requirements.txt

RUN chmod +x ./entrypoint.sh &&\
    sed -i -e 's/\r$//' ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

