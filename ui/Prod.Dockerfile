# Stage 1: Build the app
FROM node:24 AS builder

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


# Stage 2: Serve the app with a static server
FROM nginx:1.29-alpine

# Copy build artifacts from builder stage
COPY --from=builder /code/mglyph-web-vue/dist /usr/share/nginx/html

# Remove default Nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d

# Expose HTTP port and run Nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
