FROM node:11.7.0-alpine

RUN mkdir /code
WORKDIR /code

# https://stackoverflow.com/questions/52196518/could-not-get-uid-gid-when-building-node-docker
RUN npm config set unsafe-perm true
RUN npm install -g http-server

COPY ./myrecipe/package.json ./myrecipe/package-lock.json /code/
RUN npm install

COPY ./myrecipe/ /code/
RUN npm run build

CMD http-server /code/dist
