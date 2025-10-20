FROM node:24-alpine

# make the 'code' folder the current working directory
WORKDIR /code/mglyph-web-vue

# copy both 'package.json' and 'package-lock.json' (if available)
COPY mglyph-web-vue/package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory
COPY ./mglyph-web-vue .

EXPOSE 8080
# Vite dev server port
EXPOSE 5173
# start app in dev mode
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]