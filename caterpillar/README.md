### Import/update `common` library
```commandline
pip install ../common --upgrade
```

### Environment variables

Exchange
```
GRPT_EXCHANGE_ID=bybit
```
Database
```
GRPT_DB_HOST=localhost
GRPT_DB_PORT=5432
GRPT_DB_NAME=greedypet
GRPT_DB_USER=greedypet
GRPT_DB_PASSWORD=greedypet
GRPT_DB_LOG_REQUESTS=True
```

### Run caterpillar
Put the file .env with parameters environment variables above in the same directory 
with the script ``caterpillar.sh`` and run the script: 
```commandline
./caterpillar.sh
```

### Docker
Login
```commandline
docker login -u "<username>" -p "<password>" docker.io
```
Build image
```commandline
docker image build -t andennis/caterpillar:<tag> . 
```
Push image to repository
```commandline
docker push andennis/caterpillar:0.0.1
```
Run docker image
```commandline
docker run --name caterpillar \
	--rm -d \
	-e GRPT_DB_HOST=192.168.2.144 \
	-e GRPT_DB_PASSWORD=123 \
	-e GRPT_DB_LOG_REQUESTS=False \
	andennis/caterpillar:0.0.1
```
Docker log
```commandline
docker logs -f -n 10 caterpillar
```