FROM stuartmarsden/docker-twisted

WORKDIR /code

COPY . ./

EXPOSE 80

CMD ["python", "bot.py"]

