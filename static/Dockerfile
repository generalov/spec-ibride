FROM node:latest

WORKDIR /static
COPY . /static/
RUN npm --registry http://172.17.0.1:4873/ install --also=dev && mv node_modules /
ENV PATH=/node_modules/.bin:$PATH
EXPOSE 2992
CMD ["npm", "run", "dev"]
