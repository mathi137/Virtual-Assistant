FROM mysql:9.4

EXPOSE 3306

RUN echo "[mysqld]" >> /etc/mysql/conf.d/disable-timezone.cnf && \
    echo "default-time-zone='+00:00'" >> /etc/mysql/conf.d/disable-timezone.cnf
