FROM node:latest
WORKDIR /app/static
ENV PATH=/app/node_modules/.bin:$PATH
ARG NPM_ARGS="--registry http://172.17.0.1:4873/ --spin=false --loglevel=http"
COPY package.json /app/package.json
RUN cd /app && npm $NPM_ARGS install --unsafe-perm --also=dev
COPY . /app/static
CMD ["npm", "run", "dev"]
EXPOSE 2992
VOLUME ["/app/static"]
