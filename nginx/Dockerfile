FROM nginx:1.15.2

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
COPY dhparam.pem /etc/nginx/
COPY nginx-selfsigned.crt /etc/nginx/
COPY nginx-selfsigned.key /etc/nginx/
COPY self-signed.conf /etc/nginx/
COPY ssl-params.conf /etc/nginx/
