FROM node:22.15.0-alpine

RUN mkdir /code
WORKDIR /code

RUN npm install -g http-server

COPY ./myrecipe/package.json ./myrecipe/package-lock.json /code/
RUN npm install

COPY ./myrecipe/ /code/
RUN npm run build

CMD http-server /code/dist
