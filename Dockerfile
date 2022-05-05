FROM vedph2020/macronizer-base
EXPOSE 105
ADD start.sh /
RUN chmod +x /start.sh
CMD ["/start.sh"]
# WORKDIR /usr/local/macronizer/latin-macronizer
# CMD ["/bin/bash", "cd /usr/local/macronizer/latin-macronizer && source .venv/bin/activate && python ./api.py"]
# CMD ["python", "./api.py"]
