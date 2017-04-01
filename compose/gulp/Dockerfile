FROM node:7.5
MAINTAINER James Audretsh <audretschjames@gmail.com>

RUN npm i -g gulp && \
    rm -rf /tmp/*

RUN mkdir -p /app

WORKDIR /app

RUN npm install gulp

COPY ./compose/gulp/entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r//' /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gulp", "watch"]
