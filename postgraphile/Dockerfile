FROM node:8.10

WORKDIR /usr/src/app

RUN npm install -g postgraphile

EXPOSE 5000

COPY . /usr/src/app

CMD [ "./run-postgraphile" ]

