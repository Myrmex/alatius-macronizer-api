FROM vedph2020/macronizer-base
EXPOSE 105
CMD ["python", "/usr/local/macronizer/latin-macronizer/api.py"]
