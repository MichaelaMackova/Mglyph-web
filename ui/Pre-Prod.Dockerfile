FROM node:24

# make the 'code' folder the current working directory
WORKDIR /code/mglyph-web-vue

# copy both 'package.json' and 'package-lock.json' (if available)
COPY mglyph-web-vue/package*.json ./

# install project dependencies
RUN npm ci

# copy project files and folders to the current working directory
COPY ./mglyph-web-vue .

# Generate the production static files (the "dist" folder)
RUN npm run build

EXPOSE 8080
# Vite preview server port
EXPOSE 4173
# preview built not for production use - testing if build was successful
# and to preview the built app locally
CMD [ "npm", "run", "preview" , "--", "--host", "0.0.0.0" ]