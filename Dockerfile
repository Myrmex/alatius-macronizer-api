FROM vedph2020/macronizer:0.1.1-base
EXPOSE 105
ADD start.sh /
RUN chmod +x /start.sh
CMD ["/start.sh"]
