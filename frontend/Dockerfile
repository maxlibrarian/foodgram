# build env
FROM node:21.7.1-alpine
ENV npm_config_legacy_peer_deps=true
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
CMD cp -r build result_build
