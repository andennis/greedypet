## Poetry configuration

### Package Repository
The packages are hosted on https://gemfury.com/
```commandline
poetry config repositories.greedypet https://pypi.fury.io/andennis/
poetry config http-basic.greedypet <token> NOPASS
```
### Publishing
```commandline
poetry publish --build --repository greedypet
``` 
### Installation
```commandline
pip install --index-url https://pypi.fury.io/andennis/ common
```